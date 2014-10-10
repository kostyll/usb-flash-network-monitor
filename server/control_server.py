import os
from copy import deepcopy
import bottle
from bottle import run, request, Bottle, static_file

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
        octets = map(lambda y: (value >> y), self.octet_offsets)
        octets[1] = octets[1] % 2**8
        octets[2] = octets[2] % 2**16
        octets[3] = octets[3] % 2**24
        return ".".join(map(int,octets))

    def python_value(self,value):
        self.check_str_representation(value)
        octets = map(int, str(value).split('.'))
        octets = map(lambda x,y: x<<y, octets,self.octet_offsets)
        return sum(octets)


peewee.SqliteDatabase.register_fields({'int':'int'})

db = peewee.SqliteDatabase(database_file)

class BaseModel(peewee.Model):
    class Meta:
        database = db


class Client(BaseModel):

    ip_addr = IPField(unique=True)


class GeneralSerial(BaseModel):

    number = peewee.CharField(unique=True)


class ClientSerial(GeneralSerial):

    client = peewee.ForeignKeyField(Client)


class ClientsManager(object):

    _clients_ips = []

    def __init__(self):

        pass

    @property
    def clients_ips(self):

        return self._clients_ips

    def client_ip_existance(self,ip):
        try:
            self.clients_ips.index(ip)
            return True
        except ValueError:
            return False

    def add_client_ip(self,ip):
        if not self.client_ip_existance(ip):
            self._clients_ips.append(ip)

    def remove_client_ip(self,ip):
        if self.client_ip_existance(ip):
            self._clients_ips.remove(ip)


class GeneralDataProvider(object):

    _general_serials = []

    def __init__(self):

        self.loadconf()

    @property
    def general_serials(self):

        return self._general_serials

    def loadconf(self):

        pass

    def saveconf(self):

        pass

    def add_serial_to_general(self,serial):
        if not self.serial_existance(serial):
            self._general_serials.append(serial)

    def remove_serial_from_general(self,serial):
        if self.serial_existance(serial):
            self._general_serials.remove(serial)

    def serial_existance(self,serial):
        try:
            self.general_serials.index(serial)
            return True
        except ValueError:
            return False


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


def rendered(func):
    def wrapper(self,ctx):
        html.context = html.StrContext()
        carred_func = lambda *args: func(self,args[0])
        res = str(render_html(ctx, carred_func))
        print (res)
        return res
    return wrapper

class WebFace(object):
    def __init__(self,ctx=None):
        if ctx is None:
            ctx = {}
        self.ctx = ctx

    @rendered
    def index(self,ctx=None):
        if ctx is None:
            ctx = self.ctx
        else:
            context = deepcopy(self.ctx)
            context.update(ctx)
            ctx = context

        machines_table = "machines_table"

        caption_machine_ip="Machine IP"
        caption_machine_desc="Machine description"
        caption_machine_remove="Remove machine"
        machines_columns = [
            (caption_machine_ip,dict(align="center",key="ip")),
            (caption_machine_desc,dict(align="center",key="description")),
            (caption_machine_remove,dict(align="center",href="#",action=caption_machine_remove))
        ]

        get_field_name = lambda x: ''.join(x.split(' ')).lower()

        with DIV.container_fluid as out:
            with UL.nav.nav_tabs:
                with LI:
                    A(_("Machines"),class_="active",href="#machines",data_toggle="tab")
                with LI:
                    A(_("General serials"),href="#general",data_toggle="tab")
                with LI:
                    A(_("Special serials"),href="#special",data_toggle="tab")
            with DIV.tab_content:
                with DIV(id_="machines").tab_pane.active:
                    with DIV.row_fluid:
                        H4(_("Installed machines:"),align="center")
                    with DIV.row_fluid:
                        with DIV.span12:
                            with TABLE(
                                       id_=machines_table,
                                       data_sort_name="sheduled",
                                       data_sort_order="asc",
                                       width="100%",
                                       align="center",
                                       striped=True,
                                       ):
                                with THEAD:
                                    with TR:
                                        for column in machines_columns:
                                            TH(
                                               column[0],
                                               data_field=get_field_name(column[0]),
                                               data_sortable="true",
                                               data_align=column[1]['align']
                                               )
                                with TBODY:
                                    for client in Client.select():
                                        with TR:
                                            for column in machines_columns:
                                                if column[1].has_key("key"):
                                                    TD(client.ip_addr)
                                                else:
                                                    with TD:
                                                        A(
                                                          _(column[1]['action']),
                                                          class_="icon-large btn button_kill remove_ip_link",
                                                          )
                    with DIV.row_fluid:
                        H4(_("Add new machine"),align="center")
                    with DIV.row_fluid:
                        with DIV.span4.offset4:
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
                                BUTTON(
                                       _("Add new IP"),
                                       id_="machine_button",
                                       type="submit",
                                       class_="btn btn-primary",
                                       )


                with DIV(id_="general").tab_pane:
                    out << "bbb"
                with DIV(id_="special").tab_pane:
                    out << "ccc"

        return out

    def add_new_ip(self):
        # ip = request.forms
        print ("Adding...")

# page_os = '/os'
# page_tasks = '/general'
# page_webcam = '/webcam'
# page_processes = '/processes'

# menu_links = [
#         ('Os state','New','btn-success ',page_os),
#         ('Webcam','New','btn-primary ',page_webcam),
#         ('Tasks',get_tasks_count,'btn-success ',page_tasks),
#         ('Processes',get_processes_count,'btn-success ',page_processes)
#     ]


request_handler = Bottle()
general_data_provider = GeneralDataProvider()
web_face = WebFace(ctx={'ip':'/ip'})

@request_handler.get('/unregistered/<serial:re:[a-zA-Z0-9]+>')
def alert_unregisered_serial(serial):

    print ("IP: {} - serial {} is unregistered.".format(request['REMOTE_ADDR'],serial))

@request_handler.get('/general')
def show_general_serials():

    return simplejson.dumps(general_data_provider.general_serials)

@request_handler.route('/static/<path:path>')
def serve_static_file(path):
    return static_file(path, root="./static")

@request_handler.route('/img/<path:path>')
def serve_image_file(path):
    return static_file(path, root="./img")

@request_handler.get('/')
def index_page():
    return web_face.index({'menu_links':[]})

@request_handler.post('/ip')
def add_machine():
    return web_face.add_new_ip()

def main():
    db.connect()
    map(lambda x: x.create_table(fail_silently=True),[Client,GeneralSerial,ClientSerial])
    run(request_handler,port=8090,reloader=True)

if __name__ == "__main__":
    main()
