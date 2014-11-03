showPassword = ->
  key_attr = $("#key").attr("type")
  unless key_attr is "text"
    $(".checkbox").addClass "show"
    $("#key").attr "type", "text"
  else
    $(".checkbox").removeClass "show"
    $("#key").attr "type", "password"
  return

prepare = ->
    btn_login = $("#btn-login")
    btn_login.click(make_login_request)
    return

make_login_request = ->
    username = $("#email")
    password = $("#key")
    if username.val().indexOf("@") < 0 and username.val() == ""
        alert "Not valid email"
        return
    if password.val() == ""
        alert "Not valid password"
        return
    # alert username+password
    $.ajax
        url:'/login'
        type: 'POST'
        dataType:'json'
        data:
            username:username.val().trim()
            password:password.val().trim()
        success: handle_auth_result

handle_auth_result = (data) ->
    # alert "auth result"
    # alert data
    # alert data.result
    if data.result == "ok"
        # alert "changing window location"
        new_locatinon = document.location.protocol + '//'+ document.location.host
        # alert new_locatinon
        window.location.href = new_locatinon
    return

window.onload = prepare

