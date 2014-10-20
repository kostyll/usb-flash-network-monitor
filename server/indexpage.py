import html
from html import *

from copy import deepcopy
from web_face_gen_templatete import render_html
from utils import _

class IndexPage(object):
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
        self.pages = {}

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
            # (caption_special_serials,dict(align="left",key="special_serial_numbers")),
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
                                       data='get_machines()',
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
                                       # data_show_refresh="true",
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
                                # List special serial numbers
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
                                            TH(
                                               _("Actions"),
                                               data_field="actions",
                                               data_align="center",
                                               data_formatter='unregister_serial_formatter',
                                               )
                with DIV(id_="add_serial_number_for_machine",tabindex="-1", role="dialog",aria_labelledby="add_serial_number_for_machine",aria_hidden="true").modal.fade:
                  with DIV.modal_dialog:
                    with DIV.modal_content:
                      with DIV.modal_header:
                        H4("Add new serial number")
                        with FORM(role="form",action="#"):
                          with DIV.form_group:
                            LABEL(_("Serial number"),for_="new_registered_serial_number")
                            INPUT(
                                  type="text",
                                  id_="new_registered_serial_number",
                                  placeholder=_("type here serial number"),
                                  class_="form-control",
                                  )
                          A(
                            _("Register serial number"),
                            id_="button_register_special_serial_number",
                            type="submit",
                            class_="btn btn-primary",
                            )

        return out

    def get(self,ctx=None):
        ctx_hash = hash(str(ctx))
        if self.pages.has_key(ctx_hash):
            return self.pages[ctx_hash]
        else:
            result = self.index(ctx)
            self.pages[ctx_hash] = result
            return result
