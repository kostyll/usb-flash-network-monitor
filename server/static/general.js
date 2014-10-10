var gebi = function(id) {
    return document.getElementById(id);
}

var gebi_value = function(id) {
    return gebi(id).value
}

var is_ip_correct = function(ip) {
    return true;
}

var add_new_machine = function() {
    ip = gebi_value("machine_ip_address");
    descr = gebi_value("machine_description");
    if is_ip_correct(ip) {
        alert("Added"+String(ip)+" "+String(descr));
    } else {
        alert("IP is incorrect! Check it please");
    }

}

var prepare = function() {
    document.getElementById("machine_button").onclick = add_new_machine;
    alert("Prepared");
}

window.onload = prepare;
