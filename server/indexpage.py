import html
from html import *

from copy import deepcopy
import web_face_gen_templatete
from web_face_gen_templatete import render_html
from utils import _

DEBUG = web_face_gen_templatete.DEBUG

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


class IndexPage(object):
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
                                       # data_show_refresh="true",
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

# <section id="login">
#     <div class="container">
#         <div class="row">
#             <div class="col-xs-12">
#                 <div class="form-wrap">
#                 <h1>Log in with your email account</h1>
#                     <form role="form" action="javascript:;" method="post" id="login-form" autocomplete="off">
#                         <div class="form-group">
#                             <label for="email" class="sr-only">Email</label>
#                             <input type="email" name="email" id="email" class="form-control" placeholder="somebody@example.com">
#                         </div>
#                         <div class="form-group">
#                             <label for="key" class="sr-only">Password</label>
#                             <input type="password" name="key" id="key" class="form-control" placeholder="Password">
#                         </div>
#                         <div class="checkbox">
#                             <span class="character-checkbox" onclick="showPassword()"></span>
#                             <span class="label">Show password</span>
#                         </div>
#                         <input type="submit" id="btn-login" class="btn btn-custom btn-lg btn-block" value="Log in">
#                     </form>
#                     <a href="javascript:;" class="forget" data-toggle="modal" data-target=".forget-modal">Forgot your password?</a>
#                     <hr>
#                 </div>
#             </div> <!-- /.col-xs-12 -->
#         </div> <!-- /.row -->
#     </div> <!-- /.container -->
# </section>

class COFFEE(html.TAG):
  name = "script"
  attrs = { 'type': 'text/coffeescript'}

  def __init__(self,src):
    super(COFFEE,self).__init__('', src=src)

class LoginPage(object):
    def get(self):
        html.context = html.StrContext()
        with HTML5 as out:
            with HEAD:
                if not DEBUG:
                    CSS(href='http://maxcdn.bootstrapcdn.com/bootstrap/2.3.2/css/bootstrap.min.css')
                    # CSS(href='static/custom.css')
                    JS(src='http://code.jquery.com/jquery-git2.js')
                    JS(src='http://maxcdn.bootstrapcdn.com/bootstrap/2.3.2/js/bootstrap.min.js')
                else:
                    CSS(href='static/bootstrap.css')
                    # CSS(href='static/custom.css')
                    JS(src='static/jquery-git2.js')
                    JS(src='static/bootstrap.js')

                CSS(href="static/login.css")
                # JS(src="static/coffee-script.js")
                JS(src="static/login.js")
            with BODY:
                with SECTION(id_="login"):
                    with DIV.container:
                        with DIV.row:
                            # with DIV.center:
                                with DIV.form_wrap:
                                    H1(_("Login with your email account"))
                                    with FORM(role="form",action="javascript:;",method="post",id_="login-form",autocomplete="off"):
                                        with DIV.form_group:
                                            with LABEL(for_="email").sr_only:
                                                out << _("Email")
                                            INPUT(type="email",name="email",id_="email",class_="form-control",placeholder=_("somebody@example.com"))
                                        with DIV.form_group:
                                            with LABEL(for_="key").sr_only:
                                                out << _("Password")
                                            INPUT(type="password",name="key",id_="key",class_="form-control",placeholder=_("Password"))
                                        with DIV.checkbox:
                                            with SPAN(onclick="showPassword()").character_checkbox:
                                                pass
                                            with SPAN.label:
                                                out << _("Show password")
                                        INPUT(type="submit",id_="btn-login", class_="btn btn-custom btn-lg btn-block", value=_("Log in"))
                                    # with A(href="javascript:;",):
                                    #     out << _("Forgot your password")
        return str(out)
        return """<!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <title>Bootstrap, from Twitter</title>
            <meta name="description" content="">
            <meta name="author" content="">

            <!-- Le styles -->
            <link href="static/bootstrap.css" rel="stylesheet">
            <style type="text/css">
              /* Override some defaults */
              html, body {
                background-color: #eee;
              }
              body {
                padding-top: 40px;
              }
              .container {
                width: 300px;
              }

              /* The white background content wrapper */
              .container > .content {
                background-color: #fff;
                padding: 20px;
                margin: 0 -20px;
                -webkit-border-radius: 10px 10px 10px 10px;
                   -moz-border-radius: 10px 10px 10px 10px;
                        border-radius: 10px 10px 10px 10px;
                -webkit-box-shadow: 0 1px 2px rgba(0,0,0,.15);
                   -moz-box-shadow: 0 1px 2px rgba(0,0,0,.15);
                        box-shadow: 0 1px 2px rgba(0,0,0,.15);
              }

              .login-form {
                margin-left: 65px;
              }

              legend {
                margin-right: -50px;
                font-weight: bold;
                  color: #404040;
              }

            </style>
            <script src="static/login.js">

        </head>
        <body>
          <div class="container">
            <div class="content">
              <div class="row">
                <div class="login-form">
                  <h2>Login</h2>
                  <form action="">
                    <fieldset>
                      <div class="clearfix">
                        <input name="username" type="text" placeholder="Username">
                      </div>
                      <div class="clearfix">
                        <input name="password" type="password" placeholder="Password">
                      </div>
                      <button id="login_button" class="btn primary" type="submit">Sign in</button>
                    </fieldset>
                  </form>
                </div>
              </div>
            </div>
          </div> <!-- /container -->
        </body>
        </html>"""
