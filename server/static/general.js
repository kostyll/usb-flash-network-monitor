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

var update_machines_table = function(){
    $.ajax({
        url:machines_url,
        type:'GET',
        success:function(data){
            data.forEach(function(item,index,array){
                alert(item);
            });
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

var prepare = function() {
    gebi("machine_button").onclick = add_new_machine;
    gebi("remove_machine_button").onclick = remove_machines;
    // alert("Prepared");
}

window.onload = prepare;
