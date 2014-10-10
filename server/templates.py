# -*- coding : utf-8 -*-
# from __future__ import unicode_literals

import html_dsl
from html_dsl import *

from utils import _

def template_processes(ctx):
    field_processes_table = "processes_table"
    caption_process_path = _("Process path")
    caption_process_pid = _("Process PID")
    caption_process_kill = _("KILL")

    columns = [
        (caption_process_pid,dict(align="center",key="pid")),
        (caption_process_path,dict(align="left",key="command")),
        (caption_process_kill,dict(align="center",href="/web/kill/pid",action=caption_process_kill)),
    ]

    get_field_name = lambda x: ''.join(x.split(' ')).lower()

    with DIV.container_fluid as out:
        with DIV.row_fluid:
            H1(_("Processes management"),align="center")
        with DIV.row_fluid:
            with DIV.span12:
                with TABLE(
                           id=field_processes_table,
                           data_sort_name="sheduled",
                           data_sort_order="asc",
                           data_toggle="table",
                           width="100%",
                           align="center",
                           striped=True,
                           ):
                    with THEAD:
                        with TR:
                            for column in columns:
                                TH(column[0],data_field=get_field_name(column[0]),data_sortable="true",data_align=column[1]['align'])
                    with TBODY:
                        processes = ctx.get('processes',{})
                        for pid,process_info in processes.items():
                            with TR:
                                for column in columns:
                                    if column[1].has_key('key'):
                                        TD(process_info[column[1]['key']])
                                    else:
                                        with TD:
                                            A(_(column[1]['action']),class_="icon-large btn button_kill ",process_id=pid)
    return out

def template_os(ctx):
    field_cgroups_table = "cgroups_table"
    caption_cgroups_table = _("Present CGroups")

    caption_cgroup_name = _("Name")
    caption_cgroup_

    field_cgroups_form = "cgroups_form"
    caption_cgroups_form = _("Add new CGroup")

    columns = [
     ]
