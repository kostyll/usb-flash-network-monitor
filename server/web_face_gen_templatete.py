# -*- coding : utf-8 -*-
# from __future__ import unicode_literals

import os
import re
import urllib2, urllib
import datetime

import html
from html import *

from utils import _

DEBUG=True

# print context

def header(ctx):
    with HEAD as out:
        if not DEBUG:
            CSS(href='http://maxcdn.bootstrapcdn.com/bootstrap/2.3.2/css/bootstrap.min.css')
            # CSS(href='http://netdna.bootstrapcdn.com/twitter-bootstrap/2.3.2/css/bootstrap.no-responsive.no-icons.min.css')
            CSS(href='http://silviomoreto.github.io/bootstrap-select/stylesheets/bootstrap-select.css')
            # CSS(href='https://raw.githubusercontent.com/wenzhixin/bootstrap-table/master/src/bootstrap-table.css')
            CSS(href='bootstrap-table.css')
            CSS(href='custom.css')

            JS(src='http://code.jquery.com/jquery-git2.js')

            JS(src='http://maxcdn.bootstrapcdn.com/bootstrap/2.3.2/js/bootstrap.min.js')
            JS(src='http://silviomoreto.github.io/bootstrap-select/javascripts/bootstrap-select.js')
            # JS(src='https://raw.githubusercontent.com/wenzhixin/bootstrap-table/master/src/bootstrap-table.js')
            JS(src='static/bootstrap-table.js')
        else:
            CSS(href='static/bootstrap.css')
            # CSS(href='bootstrap.no-responsive.no-icons.min.css')
            # CSS(href='bootstrap-select.css')
            CSS(href='static/bootstrap-table.css')
            CSS(href='static/bootstrap.icon-large.css')
            CSS(href='static/custom.css')

            JS(src='static/jquery-git2.js')

            JS(src='static/bootstrap.js')
            # JS(src='bootstrap-select.js')
            JS(src='static/bootstrap-table.js')
        JS(src='static/general.js')
        TITLE(ctx.get('title','untitled'))
    return out

def head_links(ctx):
    links = ctx.get('menu_links')
    with UL.nav as out1:
        for link in links:
            attrs = {}
            if len(link) > 3:
                attrs.update(class_=link[2]+"menu_left_buttons btn-menu  ")
            href = link[3]
            # print "href=",href
            with LI:
                if link[1] is not None:
                    with A(href=href,**attrs):
                        out1 << link[0]
                        if callable(link[1]):
                            print ('link is callable')
                            SPAN(link[1](), class_="badge badge-important")
                        else:
                            SPAN(link[1], class_="badge badge-important")
                else:
                    A(link[0], class_=""+attrs.get('class_',''),href=href)
    with UL.nav.navbar_text.pull_right as out2:
        for link in ['Profile','Log Out']:
            with LI:
                A(link,class_="menu_right_buttons",href="#")

    return out1,out2

def general_body(ctx):
    with DIV.navbar_inner as out:
        with DIV.container_fluid:
            with BUTTON(type="button",class_="btn btn-navbar",data_toggle="collapse", data_target=".nav-collapse"):
                for index in xrange(3):
                    SPAN(" ",class_="icon-bar")
            A(ctx.get("company",'Company'),class_="brand",href="/")
            with DIV.nav_collapse.collapse:
                head_links(ctx)
    return out

def page1(ctx):
    field_username = "login_username"
    place_username = _("Username")

    field_password = "login_password"
    place_password = _("Password")
    with DIV.container_fluid as out:
        with DIV.row_fluid:
            with FORM(id="login_form",align="center"):
                H1(ctx.get('company','Company'),align="center")
                BR()
                with FIELDSET:
                    with DIV.span6.offset3:
                        with DIV.row_fluid:
                            with DIV.span5.offset1.pull_left:
                                LABEL(place_username,for_=field_username)
                                with DIV.control_group:
                                    with DIV.controls:
                                        with DIV.input_prepend:
                                            with SPAN.add_on:
                                                I("",class_="icon-user")
                                            INPUT(type='text',placeholder=place_username,id=field_username)
                            with DIV.span5.pull_right:
                                LABEL(place_password,for_=field_password)
                                with DIV.control_group:
                                    with DIV.controls:
                                        INPUT(type='password',placeholder=place_password,id=field_password)
                        with DIV.row_fluid:
                            with DIV(align="center").span4.offset4:
                                BUTTON(_("Login"),type="button",align="center",class_="btn btn-success btn-large")

                with DIV(align="center"):
                    H3(_("Don't you have an account?"))
                    A(_("Register"),type="button",href="#", class_="btn btn-primary btn-large")

def body(ctx):
    with DIV.navbar.navbar_inverse.navbar_static_top as out:
        general_body(ctx)
        for page in (page1,):
            BR()
            page(ctx)

def layout(ctx):
    with HTML5 as c:
        header(ctx)
        body(ctx)
    return c

def render_html(ctx,page):
    # print ctx
    with HTML5 as c:
        header(ctx)
        with DIV.navbar.navbar_static_top:
            general_body(ctx)
        # print (page)
        page(ctx)
    return c

def main():
    print (layout({'title':'HELLO','company':'Game Company'}))

if __name__ == "__main__":
    main()
