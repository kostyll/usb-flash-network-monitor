import os
from copy import deepcopy
import bottle
from bottle import run, request, Bottle, static_file, response

import simplejson

import peewee

import html
from html import *

from web_face_gen_templatete import render_html
from utils import _


#TODO : transform loading configuration via configparser module

# netmask = "192.168.0.11-14,17,18,19"
# network_prefix,ips = netmask.split('.')[:3],netmask.rpartition ('.')[2]
# for range in ips.split(','):
#     if range.find('-')>-1:
#         start,stop=map(int,range.split('-'))
#         if start > stop:
#             start,stop = stop,start
#         print(list(xrange(start,stop+1)))
#     else:
#         print(range)

database_file = os.path.join(os.environ['HOME'],os.environ['USB_MONITOR_FILE'])

class WrongIPAddressStrRepresentation(Exception):
    pass


class IPField(peewee.Field):
    db_field = 'int'
    octet_offsets = [24,16,8,0]
    def check_str_representation(self,value):
        octets = str(value).split('.')
        if len(octets) != 4:
            raise WrongIPAddressStrRepresentation(value)
        for octet in octets:
            try:
                octet = int(octet)
            except ValueError:
                raise WrongIPAddressStrRepresentation(value)
            if octet<0 or octet>255:
                raise WrongIPAddressStrRepresentation(value)

    def db_value(self,value):
        self.check_str_representation(value)
        octets = map(int, str(value).split('.'))
        octets = map(lambda x,y: x<<y, octets,self.octet_offsets)
        result = sum(octets)
        # print ('result = {}'.format(result))
        return  result

    def python_value(self,value):
        octets = map(lambda y: (value >> y), self.octet_offsets)
        # print ("octets {}".format(octets))
        octets = map(lambda x: x % (2**8), octets)
        # print ("octets {}".format(octets))
        result = ".".join(map(str,octets))
        # print ('result = {}'.format(result))
        return result


peewee.SqliteDatabase.register_fields({'int':'int'})

db = peewee.SqliteDatabase(database_file)

class BaseModel(peewee.Model):
    class Meta:
        database = db


class Client(BaseModel):

    ip_addr = IPField(unique=True)

    description = peewee.CharField(max_length=200)


class GeneralSerial(BaseModel):

    number = peewee.CharField(unique=True)


class ClientSerial(GeneralSerial):

    client = peewee.ForeignKeyField(Client)


class UnregisteredMassStorageObserver(object):

    okay = simplejson.dumps({'result':'ok'})
    error = lambda x:simplejson.dumps({'result':'error','error':x})

    def __init__(self):

        self._unregistered_serials = {}

    def add_unregistered_serial(self,ip,serial):
        self._unregistered_serials.setdefault(ip,[])
        self._unregistered_serials[ip].append(serial)

    def remove_unregistered_serial(self,ip,serial):
        if self._unregistered_serials.has_key(ip):
            try:
                self._unregistered_serials[ip].remove(serial)
                return okay
            except Exception,e:
                return error(str(e))


class WebFace(object):
    class rendered(object):

        def __call__(self,func):
            def wrapper(class_instance,ctx):
                context = deepcopy(class_instance.ctx)
                context.update(ctx)
                ctx = context
                html.context = html.StrContext()
                carred_func = lambda *args: func(self,args[0])
                res = str(render_html(ctx, carred_func))
                # print (res)
                return res
            return wrapper

    def __init__(self,ctx=None):
        if ctx is None:
            ctx = {}
        self.ctx = ctx

    @rendered()
    def index(self,ctx=None):
        print ("ctx=",ctx)

        machines_table = "machines_table"
        general_serials_table = "general_serials_table"

        get_action_name = lambda x: _(" ".join(x.split('_')))
        get_button_name = lambda action: action +'_button'
        get_action_class = lambda x: "class_"+x

        action_remove="machine_remove"
        caption_machine_remove = get_action_name(action_remove)

        caption_machine_ip=_("Machine IP")
        caption_machine_desc=_("Machine description")
        caption_machine_actions=_("Actions")
        caption_special_serials=_("Special serials")
        machines_columns = [
            ("",dict(key="state",data_checkbox="true",align="center")),
            (caption_machine_ip,dict(align="center",key="ip_addr")),
            (caption_machine_desc,dict(align="left",key="description")),
            (caption_special_serials,dict(align="left",key="special_serial_numbers")),
            (caption_machine_actions,{'align':"center",'key':"actions",'data-formatter':'actions_formatter'}),
            # (caption_machine_actions,dict(align="center",href="#",action=[action_remove]))
        ]

        caption_general_serial_number = _("Serial number")
        remove_general_serial_action = "remove_general_serial"
        add_new_general_serial_action = "add_new_general_serial"
        general_serials_columns = [
            ("",dict(key="state",data_checkbox="true",align="center")),
            (caption_general_serial_number,dict(align="left",key="number")),
        ]

        get_field_name = lambda x: ''.join(x.split(' ')).lower()

        with DIV.container_fluid as out:
            with UL.nav.nav_tabs:
                with LI:
                    A(_("Machines"),class_="active",href="#machines",data_toggle="tab")
                with LI:
                    A(_("General serials"),href="#general",data_toggle="tab")
                with LI:
                    A(_("New machine"),href="#new_machine",data_toggle="tab")
            with DIV.tab_content:
                with DIV(id_="machines").tab_pane.active:
                    with DIV.row_fluid:
                        H4(_("Installed machines:"),align="center")
                    with DIV.row_fluid:
                        with DIV.span12:
                            with DIV(id_="custom_machines_toolbar"):
                                BUTTON(_(get_action_name(action_remove)),
                                    type="submit",
                                    class_="btn btn-primary",
                                    id_="remove_machine_button",
                                    data_method="remove",
                                    )
                            with TABLE(
                                       id_=machines_table,
                                       data_sort_name="sheduled",
                                       data_sort_order="asc",
                                       data_toggle="table",
                                       width="100%",
                                       align="center",
                                       pagination="true",
                                       data_search="true",
                                       data_show_refresh="true",
                                       data_show_toggle="true",
                                       data_show_columns="true",
                                       data_toolbar="#custom_machines_toolbar",
                                       striped=True,
                                       # data_url='/ip',
                                       # data='get_machines()',
                                       ):
                                with THEAD:
                                    with TR:
                                        for column in machines_columns:
                                            TH(
                                               column[0],
                                               data_field=column[1].get('key',None),
                                               data_sortable="true",
                                               data_align=column[1]['align'],
                                               data_checkbox="true" if column[1].get('data_checkbox',None) == "true" else "false",
                                               data_formatter=column[1].get('data-formatter',''),
                                               )
                                # with TBODY:
                                #     for client in Client.select():
                                #         with TR:
                                #             for column in machines_columns:
                                #                 if column[1].has_key("key"):
                                #                     TD(getattr(client,column[1]['key']))
                                #                 else:
                                #                     with TD:
                                #                         for action in column[1]['action']:
                                #                             A(
                                #                               get_action_name(action),
                                #                               class_="btn btn-success "+get_action_class(action),
                                #                               )

                with DIV(id_="general").tab_pane:
                    with DIV.row_fluid:
                        H4(_("General registered serial numbers"))
                    with DIV.row_fluid:
                        with DIV.span12:
                            with DIV(id_="custom_general_serials_toolbar"):
                                with DIV(role="form").form_inline:
                                    BUTTON(_(get_action_name(remove_general_serial_action)),
                                       type="submit",
                                       class_="btn btn-primary",
                                       id_=get_button_name(remove_general_serial_action),
                                       data_method="remove",
                                       )
                                    INPUT(
                                          id_="general_serial_number",
                                          type="text",
                                          placeholder=_("type here new serial number"),
                                          class_="form-control",
                                          )
                                    BUTTON(
                                           _(get_action_name(add_new_general_serial_action)),
                                           id_=get_button_name(add_new_general_serial_action),
                                           type="submit",
                                           class_="btn btn-primary",
                                           )

                            with TABLE(
                                       id_=general_serials_table,
                                       data_sort_name="sheduled",
                                       data_sort_order="asc",
                                       data_toggle="table",
                                       width="100%",
                                       align="center",
                                       pagination="true",
                                       data_search="true",
                                       data_show_refresh="true",
                                       data_show_toggle="true",
                                       data_show_columns="true",
                                       data_toolbar="#custom_general_serials_toolbar",
                                       # striped=True,
                                       data_url='/general'
                                       ):
                                with THEAD:
                                    with TR:
                                        for column in general_serials_columns:
                                            TH(
                                               column[0],
                                               data_field=column[1].get('key',None),
                                               data_sortable="true",
                                               data_align=column[1]['align'],
                                               data_checkbox="true" if column[1].get('data_checkbox',None) == "true" else "false",
                                               )
                with DIV(id_="new_machine").tab_pane:
                    with DIV.row_fluid:
                        H4(_("Add new machine"),align="center")
                    with DIV.row_fluid:
                        with DIV.span4:
                            with FORM(role="form",action="#"):
                                with DIV.form_group:
                                    LABEL(_("IP address"),for_="ip_address")
                                    INPUT(
                                          type="text",
                                          id_="machine_ip_address",
                                          placeholder=_("ip address"),
                                          class_="form-control"
                                          )
                                with DIV.form_group:
                                    LABEL(_("Description"),for_="description")
                                    INPUT(
                                          type="text",
                                          id_="machine_description",
                                          placeholder=_("IP description"),
                                          class_="form-control"
                                          )
                                A(
                                       _("Add new IP"),
                                       id_="machine_button",
                                       type="submit",
                                       class_="btn btn-primary",
                                       )

                with DIV(id_="edit_machine_modal_form",tabindex="-1", role="dialog",aria_labelledby="edit_machine_modal_form",aria_hidden="true").modal.fade:
                    with DIV.modal_dialog:
                        with DIV.modal_content:
                            with DIV.modal_header:
                                with TABLE(
                                        id_="edit_machine_table",
                                        data_toggle="table",
                                    ):
                                    with THEAD:
                                        with TR:
                                            TH(
                                                _("Serial number"),
                                                data_field="serial_number",
                                                data_align="left",
                                                )
        return out

    def get_ips(self):
        pass

    def add_new_ip(self):
        ip = request.forms.get('ip')
        descr = request.forms.get('descr')
        print ("Adding...{}, {}".format(ip,descr))
        try:
            Client.create(ip_addr=ip,description=descr)
        except peewee.IntegrityError:
            pass
        return "Ok"

    def remove_ip(self):
        try:
            ip_addr = request.forms.ip
            print ("ip_addr = %s" % ip_addr)
            client = Client.get(Client.ip_addr == ip_addr)
            print ("Client = %s" % client)
            client.delete_instance()
        except Exception,e:
            print (e)
            pass

    def add_new_general_serial_number(self):
        number = request.forms.number
        GeneralSerial.create(number=number)
        return "Ok"

    def remove_general_serial_number(self):
        number = request.forms.number
        try:
            general_serial = GeneralSerial.get(GeneralSerial.number == number)
            general_serial.delete_instance()
        except Exception,e:
            print (e)
            pass


request_handler = Bottle()
unregistered_devices = UnregisteredMassStorageObserver()
web_face = WebFace(ctx={'company':'USB monitor','ip':'/ip'})

@request_handler.get('/unregistered/<serial:re:[a-zA-Z0-9]+>')
def alert_unregisered_serial(serial):

    print ("IP: {} - serial {} is unregistered.".format(request['REMOTE_ADDR'],serial))

@request_handler.get('/general')
def show_general_serials():

    return simplejson.dumps(map(lambda x: {'number':x.number},GeneralSerial.select()))

@request_handler.put('/general')
def add_new_serial_number():
    return web_face.add_new_general_serial_number()

@request_handler.delete('/general')
def remove_general_serial_number():
    return web_face.remove_general_serial_number()

@request_handler.route('/static/<path:path>')
def serve_static_file(path):
    return static_file(path, root="./static")

@request_handler.route('/img/<path:path>')
def serve_image_file(path):
    return static_file(path, root="./img")

@request_handler.get('/')
def index_page():
    return web_face.index({'menu_links':[]})

@request_handler.put('/ip')
def add_machine():
    return web_face.add_new_ip()

@request_handler.get('/ip/<machine>')
@request_handler.get('/ip')
def list_machines(machine=None):
    response.content_type = 'application/json; charset=latin9'
    clients = Client.select()
    if machine is None:
        pass
    else:
        clients = filter(lambda x:x.ip_addr==machine, clients)
    return simplejson.dumps(map(lambda x: {
            'ip_addr':x.ip_addr,
            'description':x.description,
            'special_serial_numbers':[],
            },clients))

@request_handler.delete('/ip')
def remove_machine():
    return web_face.remove_ip()

def main():
    db.connect()
    map(lambda x: x.create_table(fail_silently=True),[Client,GeneralSerial,ClientSerial])
    run(request_handler,port=8090,reloader=True)

if __name__ == "__main__":
    main()
