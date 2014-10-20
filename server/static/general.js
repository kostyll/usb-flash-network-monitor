var gebi = function(id) {
    return document.getElementById(id);
}

var gebi_value = function(id) {
    return gebi(id).value
}

var is_ip_correct = function(ip) {
    return true;
}

machines_url = '/ip';
general_serials_url='/general';

var update_machines_table = function(){
    get_machines();
}

var process_machine_action_edit = function(data){
    // alert("edit,"+data);
    $("#edit_machine_modal_form").attr("target",data);
    $.ajax({
        url:'/ip/'+data,
        type:'GET',
        success:function(data){
            rows = [];
            data[0].special_serial_numbers.forEach(function(item,index,array){
                rows.push({
                    serial_number:item,
                });
            });
            // alert(rows);
            $("#edit_machine_table").bootstrapTable('load',rows);
        }
    });
    $("#edit_machine_modal_form").modal('show');
    get_machines();
}

var register_serial_number = function(){
    // Register some serial number for selected machine
    machine = $("#add_serial_number_for_machine").attr("target");
    number = gebi_value("new_registered_serial_number");
    gebi("new_registered_serial_number").value = "";
    $.ajax({
        url:"/serial/"+machine,
        method:'PUT',
        data:{
            number:number,
        },
        success:function(data){
            alert("serial number "+number+" registered!");
        },
    });
}

var process_machine_action_add_serial = function(data){
    target_form = $("#add_serial_number_for_machine");
    target_form.attr("target",data);
    target_form.modal("show");

}

var process_machine_action_remove = function(data){
    alert("remove"+data);
    get_machines();
}

actions_formatter = function(value){
    console.log("formatting "+ value);
    // return value;
    actions = value.actions;
    result = "";
    actions.forEach(function(item,index,array){
        if (item == "edit"){
            result += "<a class='btn btn-primary' onclick='process_machine_action_"+item+"(\""+value.item+"\")'>"+item+"</a>\n";
        } else if (item == "remove") {
            result += "<a class='btn btn-primary' onclick='process_machine_action_"+item+"(\""+value.item+"\")'>"+item+"</a>\n";
        } else if (item == "add_serial"){
            result += "<a class='btn btn-primary' onclick='process_machine_action_"+item+"(\""+value.item+"\")'>"+item+"</a>\n";
        }
    });
    // alert (result);
    return result
};

// $('[data-field="actions"]').data({formatter:actions_formatter});

var get_machines = function(){
    $.ajax({
        url:machines_url,
        type:'GET',
        success:function(data){
            rows = [];
            table = $("#machines_table");
            data.forEach(function(item,index,array){
                // action_buttons = document.createElement('div');
                action_buttons = {
                    item:item.ip_addr,
                    actions:['add_serial','edit','remove'],
                }

                rows.push({
                    state:false,
                    ip_addr:item.ip_addr,
                    description:item.description,
                    // special_serial_numbers:item.special_serial_numbers,
                    actions:action_buttons,
                });
            });
            $("#machines_table").bootstrapTable('load',rows);
            // alert(rows);
        },
    });
}

var update_general_serials_table = function(){
    var table = $('#general_serials_table');
    table.bootstrapTable("refresh");
}

var add_new_general_serial_number = function(){
    number = gebi_value("general_serial_number");
    input_element =gebi ('general_serial_number');
    input_element.value = '';
    $.ajax({
        url:general_serials_url,
        type:'PUT',
        data:{
            number:number
        },
        success:function(data){
            update_general_serials_table();
        },
    });
}

var add_new_machine = function() {
    ip = gebi_value("machine_ip_address");
    descr = gebi_value("machine_description");
    if (!is_ip_correct(ip)) {
        alert("IP is incorrect! Check it please");
    };
    $.ajax({
        url:machines_url,
        type:'PUT',
        data:{
            ip:ip,
            descr:descr,
        },
        success:function(data){
            update_machines_table();
        },
    });
}

var remove_machines = function(){
    var table = $('#machines_table');
    var selects = table.bootstrapTable('getSelections');
    selects.forEach(function(item,index,array){
        remove_machine(item.ip_addr);
    });
    update_machines_table();
}

var remove_machine = function(ip){
    $.ajax({
        url:machines_url,
        type:"DELETE",
        data:{
            ip:ip,
        },
        success:function(data){
            // alert("Removed!");
        },
    });
}

var remove_general_serials = function(){
    var table = $('#general_serials_table');
    var selects = table.bootstrapTable('getSelections');
    selects.forEach(function(item,index,array){
        remove_general_serial(item.number);
    });
    update_general_serials_table();
}

var remove_general_serial = function(number){
    $.ajax({
        url:general_serials_url,
        type:'DELETE',
        data:{
            number:number,
        },
        success:function(data){
            //alert("Removed!");
        },
    });
}

var prepare = function() {
    update_machines_table();
    gebi("machine_button").onclick = add_new_machine;
    gebi("remove_machine_button").onclick = remove_machines;
    gebi("remove_general_serial_button").onclick = remove_general_serials;
    gebi("add_new_general_serial_button").onclick = add_new_general_serial_number;
    gebi("button_register_special_serial_number").onclick = register_serial_number;
    // alert("Prepared");
}

window.onload = prepare;
