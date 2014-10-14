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
    // $.ajax({
    //     url:machines_url,
    //     type:'GET',
    //     success:function(data){
    //         data.forEach(function(item,index,array){
    //             alert(item);
    //         });
    //     },
    // });
    // var table = $('#machines_table');
    // table.bootstrapTable("refresh");
    get_machines();
}

var update_machines_table_action_buttons = function(){
    var table = $("#machines_table");
    
}

var get_machines = function(){
    $.ajax({
        url:machines_url,
        type:'GET',
        success:function(data){
            rows = [];
            data.forEach(function(item,index,array){
                // action_buttons = document.createElement('div');
                action_buttons = null;

                rows.push({
                    ip_addr:item.ip_addr,
                    description:item.description,
                    special_serial_numbers:item.special_serial_numbers,
                    actions:action_buttons,
                });
            });
            $("#machines_table").bootstrapTable('load',{data:rows});            
            alert(rows);            
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
    table.bootstrapTable("refresh");
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
    // alert("Prepared");
}

window.onload = prepare;
