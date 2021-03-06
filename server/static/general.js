// Generated by CoffeeScript 1.8.0
var actions_formatter, add_new_general_serial_number, add_new_machine, allow, current_state_hash, disallow, gebi, gebi_value, general_serials_url, get_history, get_machines, history_url, is_ip_correct, machines_url, prepare, process_machine_action_add_serial, process_machine_action_edit, process_machine_action_remove, register_serial_number, removeElementDiv, remove_general_serial, remove_general_serials, remove_machine, remove_machines, serials_url, show_message, show_unregistered_serial, system_state_url, unregister_serial, unregister_serial_formatter, unregister_serial_url, update_general_serials_table, update_machine_serials, update_machines_table, update_system_state, update_unregistered_serials;

machines_url = "/ip";

general_serials_url = "/general";

serials_url = "/serial";

system_state_url = "/system/state";

unregister_serial_url = "/unregistered";

history_url = "/history";

current_state_hash = null;

show_message = function(message) {
  return $.notify(message);
};

gebi = function(id) {
  return document.getElementById(id);
};

gebi_value = function(id) {
  return gebi(id).value;
};

is_ip_correct = function(ip) {
  return true;
};

update_machines_table = function() {
  get_machines();
};

unregister_serial = function(number) {
  console.log("Unregister serial");
  $.ajax({
    url: serials_url,
    type: "DELETE",
    data: {
      number: number
    },
    success: function(data) {
      data = JSON.parse(data);
      show_message(data.message);
    }
  });
  update_machine_serials();
};

unregister_serial_formatter = function(value) {
  return "<a class='btn btn-primary' onclick='unregister_serial(\"" + value + "\")'>Unregister</a>\n";
};

update_machine_serials = function() {
  $.ajax({
    url: "/ip/" + $("#edit_machine_modal_form").attr("target"),
    type: "GET",
    success: function(data) {
      var rows;
      rows = [];
      data[0].special_serial_numbers.forEach(function(item, index, array) {
        rows.push({
          serial_number: item,
          actions: item
        });
      });
      $("#edit_machine_table").bootstrapTable("load", rows);
    }
  });
};

process_machine_action_edit = function(data) {
  $("#edit_machine_modal_form").attr("target", data);
  update_machine_serials();
  $("#edit_machine_modal_form").modal("show");
  get_machines();
};

register_serial_number = function() {
  var machine, number;
  machine = $("#add_serial_number_for_machine").attr("target");
  number = gebi_value("new_registered_serial_number");
  gebi("new_registered_serial_number").value = "";
  $.ajax({
    url: serials_url,
    method: "PUT",
    data: {
      machine: machine,
      number: number
    },
    success: function(data) {
      show_message("serial number " + number + " registered!");
    }
  });
};

process_machine_action_add_serial = function(data) {
  var target_form;
  target_form = $("#add_serial_number_for_machine");
  target_form.attr("target", data);
  target_form.modal("show");
};

process_machine_action_remove = function(data) {
  remove_machine(data);
  get_machines();
};

actions_formatter = function(value) {
  var actions, result;
  console.log("formatting " + value.actions);
  console.log(typeof value.actions);
  actions = value.actions;
  result = "";
  actions.forEach(function(item, index, array) {
    if (item === "edit") {
      result += "<a class='btn btn-primary' onclick='process_machine_action_" + item + "(\"" + value.item + "\")'>" + item + "</a>\n";
    } else if (item === "remove") {
      result += "<a class='btn btn-primary' onclick='process_machine_action_" + item + "(\"" + value.item + "\")'>" + item + "</a>\n";
    } else {
      if (item === "add_serial") {
        result += "<a class='btn btn-primary' onclick='process_machine_action_" + item + "(\"" + value.item + "\")'>" + item + "</a>\n";
      }
    }
  });
  return result;
};

get_machines = function() {
  $.ajax({
    url: machines_url,
    type: "GET",
    success: function(data) {
      var rows, table;
      rows = [];
      table = $("#machines_table");
      data.forEach(function(item, index, array) {
        var action_buttons;
        action_buttons = {
          item: item.ip_addr,
          actions: ["add_serial", "edit", "remove"]
        };
        rows.push({
          state: false,
          ip_addr: item.ip_addr,
          description: item.description,
          actions: action_buttons
        });
      });
      $("#machines_table").bootstrapTable("load", rows);
    }
  });
};

get_history = function(page, pagesize) {
  if (page == null) {
    page = 1;
  }
  if (pagesize == null) {
    pagesize = 30;
  }
  $.ajax({
    url: history_url + '/' + page + '/' + pagesize,
    type: "GET",
    dataType: "json",
    success: function(data) {
      var rows, table;
      rows = [];
      table = $("#history_table");
      data.message.forEach(function(item, index, array) {
        var datetime;
        datetime = new Date(item.datetime);
        rows.push({
          date: datetime.getFullYear() + '/' + (datetime.getMonth() + 1) + '/' + datetime.getDate(),
          time: datetime.getHours() + ':' + datetime.getMinutes(),
          source: item.source,
          action: item.action,
          description: item.description
        });
      });
      $("#history_table").bootstrapTable("load", rows);
    }
  });
};

update_general_serials_table = function() {
  var table;
  table = $("#general_serials_table");
  table.bootstrapTable("refresh");
};

add_new_general_serial_number = function() {
  var input_element, number;
  number = gebi_value("general_serial_number");
  input_element = gebi("general_serial_number");
  input_element.value = "";
  $.ajax({
    url: general_serials_url,
    type: "PUT",
    data: {
      number: number
    },
    success: function(data) {
      update_general_serials_table();
    }
  });
};

add_new_machine = function() {
  var descr, ip;
  ip = gebi_value("machine_ip_address");
  gebi("machine_ip_address").value = "";
  descr = gebi_value("machine_description");
  gebi("machine_description").value = "";
  if (!is_ip_correct(ip)) {
    show_message("IP is incorrect! Check it please");
  }
  $.ajax({
    url: machines_url,
    type: "PUT",
    data: {
      ip: ip,
      descr: descr
    },
    success: function(data) {
      update_machines_table();
    }
  });
};

remove_machines = function() {
  var selects, table;
  table = $("#machines_table");
  selects = table.bootstrapTable("getSelections");
  selects.forEach(function(item, index, array) {
    remove_machine(item.ip_addr);
  });
  update_machines_table();
};

remove_machine = function(ip) {
  $.ajax({
    url: machines_url,
    type: "DELETE",
    data: {
      ip: ip
    },
    success: function(data) {}
  });
};

remove_general_serials = function() {
  var selects, table;
  table = $("#general_serials_table");
  selects = table.bootstrapTable("getSelections");
  selects.forEach(function(item, index, array) {
    remove_general_serial(item.number);
  });
  update_general_serials_table();
};

remove_general_serial = function(number) {
  $.ajax({
    url: general_serials_url,
    type: "DELETE",
    data: {
      number: number
    },
    success: function(data) {}
  });
};

removeElementDiv = function(ip, serial) {
  return document.getElementById(ip + serial).remove();
};

allow = function(ip, serial) {
  console.log("Allowed");
  console.log(serial);
  return $.ajax({
    url: serials_url,
    type: "PUT",
    dataType: "json",
    data: {
      machine: ip,
      number: serial
    },
    success: function(data) {
      if (data.result === "ok") {
        show_message("ok");
        return removeElementDiv(ip, serial);
      } else {
        show_message(data);
        return console.log(data);
      }
    }
  });
};

disallow = function(ip, serial) {
  console.log("DisAllowed");
  console.log(serial);
  return removeElementDiv(ip, serial);
};

show_unregistered_serial = function(ip, serial) {
  var dropdownbutton, notify_panel;
  notify_panel = $("#notify");
  dropdownbutton = Jaml.register("dropdownbutton", function(ctx) {
    return div({
      "class": "btn-group",
      id: ctx.ip + ctx.serial
    }, a({
      type: "button",
      "class": "btn btn-danger dropdown-toggle",
      'data-toggle': "dropdown"
    }, ctx.ip + '-' + ctx.serial, span({
      "class": "caret"
    })), ul({
      "class": "dropdown-menu",
      role: "menu"
    }, li(a({
      href: "#",
      onclick: "allow('" + ctx.ip + "','" + ctx.serial + "')"
    }, "Allow")), li({
      "class": "devider"
    }), li(a({
      href: "#",
      onclick: "disallow('" + ctx.ip + "','" + ctx.serial + "')"
    }, "Disallow"))));
  });
  $(notify_panel).append(Jaml.render("dropdownbutton", {
    ip: ip,
    serial: serial
  }));
};

update_unregistered_serials = function() {
  var notify_panel;
  notify_panel = $("#notify");
  notify_panel.html("");
  console.log("Updating unregistered serials list");
  $.ajax({
    url: unregister_serial_url,
    type: "GET",
    dataType: "json",
    success: function(data) {
      $.each(data.message, function(ip, serials) {
        $.each(serials, function(index, serial) {
          show_unregistered_serial(ip, serial);
        });
      });
    }
  });
};

update_system_state = function() {
  $.ajax({
    url: system_state_url,
    type: "GET",
    dataType: "json",
    success: function(data) {
      var state_hash;
      if (data["result"] === "ok") {
        state_hash = data["message"]["system_state_hash"];
        if (current_state_hash != null) {
          if (current_state_hash !== state_hash) {
            update_unregistered_serials();
            current_state_hash = state_hash;
          }
        } else {
          current_state_hash = state_hash;
          update_unregistered_serials();
        }
      }
    }
  });
  return get_history();
};

prepare = function() {
  update_machines_table();
  gebi("machine_button").onclick = add_new_machine;
  gebi("remove_machine_button").onclick = remove_machines;
  gebi("remove_general_serial_button").onclick = remove_general_serials;
  gebi("add_new_general_serial_button").onclick = add_new_general_serial_number;
  gebi("button_register_special_serial_number").onclick = register_serial_number;
  setInterval(update_system_state, 9000);
};

window.onload = prepare;
