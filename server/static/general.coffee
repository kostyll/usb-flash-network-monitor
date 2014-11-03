machines_url = "/ip"
general_serials_url = "/general"
serials_url = "/serial"

gebi = (id) ->
  document.getElementById id

gebi_value = (id) ->
  gebi(id).value

is_ip_correct = (ip) ->
  true

update_machines_table = ->
  get_machines()
  return

unregister_serial = (number) ->
  $.ajax
    url: serials_url + "/" + number
    type: "DELETE"
    success: (data) ->
      data = JSON.parse(data)
      alert data.message
      return
  update_machine_serials()
  return

unregister_serial_formatter = (value) ->
  "<a class='btn btn-primary' onclick='unregister_serial(\"" + value + "\")'>Unregister</a>\n"

update_machine_serials = ->
  $.ajax
    url: "/ip/" + $("#edit_machine_modal_form").attr("target")
    type: "GET"
    success: (data) ->
      rows = []
      data[0].special_serial_numbers.forEach (item, index, array) ->
        rows.push
          serial_number: item
          actions: item
        return
      $("#edit_machine_table").bootstrapTable "load", rows
      return
  return

process_machine_action_edit = (data) ->

  # alert("edit,"+data);
  $("#edit_machine_modal_form").attr "target", data
  update_machine_serials()
  $("#edit_machine_modal_form").modal "show"
  get_machines()
  return

register_serial_number = ->

  # Register some serial number for selected machine
  machine = $("#add_serial_number_for_machine").attr("target")
  number = gebi_value("new_registered_serial_number")
  gebi("new_registered_serial_number").value = ""
  $.ajax
    url: serials_url + "/" + machine
    method: "PUT"
    data:
      number: number
    success: (data) ->
      alert "serial number " + number + " registered!"
      return
  return

process_machine_action_add_serial = (data) ->
  target_form = $("#add_serial_number_for_machine")
  target_form.attr "target", data
  target_form.modal "show"
  return

process_machine_action_remove = (data) ->
  remove_machine data
  get_machines()
  return

actions_formatter = (value) ->
  console.log "formatting " + value.actions
  console.log(typeof value.actions)
  # return value;
  actions = value.actions
  result = ""
  actions.forEach (item, index, array) ->
    if item is "edit"
      result += "<a class='btn btn-primary' onclick='process_machine_action_" + item + "(\"" + value.item + "\")'>" + item + "</a>\n"
    else if item is "remove"
      result += "<a class='btn btn-primary' onclick='process_machine_action_" + item + "(\"" + value.item + "\")'>" + item + "</a>\n"
    else result += "<a class='btn btn-primary' onclick='process_machine_action_" + item + "(\"" + value.item + "\")'>" + item + "</a>\n"  if item is "add_serial"
    return
  # alert (result);
  result

# $('[data-field="actions"]').data({formatter:actions_formatter});
get_machines = ->
  $.ajax
    url: machines_url
    type: "GET"
    success: (data) ->
      rows = []
      table = $("#machines_table")
      data.forEach (item, index, array) ->
        # action_buttons = document.createElement('div');
        action_buttons =
          item: item.ip_addr
          actions: [
            "add_serial"
            "edit"
            "remove"
          ]
        rows.push
          state: false
          ip_addr: item.ip_addr
          description: item.description
          # special_serial_numbers:item.special_serial_numbers,
          actions: action_buttons
        return
      $("#machines_table").bootstrapTable "load", rows
      return
  return

# alert(rows);
update_general_serials_table = ->
  table = $("#general_serials_table")
  table.bootstrapTable "refresh"
  return

add_new_general_serial_number = ->
  number = gebi_value("general_serial_number")
  input_element = gebi("general_serial_number")
  input_element.value = ""
  $.ajax
    url: general_serials_url
    type: "PUT"
    data:
      number: number
    success: (data) ->
      update_general_serials_table()
      return
  return

add_new_machine = ->
  ip = gebi_value("machine_ip_address")
  gebi("machine_ip_address").value = ""
  descr = gebi_value("machine_description")
  gebi("machine_description").value = ""
  alert "IP is incorrect! Check it please"  unless is_ip_correct(ip)
  $.ajax
    url: machines_url
    type: "PUT"
    data:
      ip: ip
      descr: descr
    success: (data) ->
      update_machines_table()
      return

  return

remove_machines = ->
  table = $("#machines_table")
  selects = table.bootstrapTable("getSelections")
  selects.forEach (item, index, array) ->
    remove_machine item.ip_addr
    return
  update_machines_table()
  return

remove_machine = (ip) ->
  $.ajax
    url: machines_url
    type: "DELETE"
    data:
      ip: ip
    success: (data) ->
  return

# alert("Removed!");
remove_general_serials = ->
  table = $("#general_serials_table")
  selects = table.bootstrapTable("getSelections")
  selects.forEach (item, index, array) ->
    remove_general_serial item.number
    return
  update_general_serials_table()
  return

remove_general_serial = (number) ->
  $.ajax
    url: general_serials_url
    type: "DELETE"
    data:
      number: number
    success: (data) ->
  return

#alert("Removed!");
prepare = ->
  update_machines_table()
  gebi("machine_button").onclick = add_new_machine
  gebi("remove_machine_button").onclick = remove_machines
  gebi("remove_general_serial_button").onclick = remove_general_serials
  gebi("add_new_general_serial_button").onclick = add_new_general_serial_number
  gebi("button_register_special_serial_number").onclick = register_serial_number
  return

# alert("Prepared");
window.onload = prepare
