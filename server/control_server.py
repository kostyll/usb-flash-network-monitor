import os
from md5 import md5
import datetime
now = datetime.datetime.now
import bottle
from bottle import run, request, Bottle, static_file, response

import simplejson

from models import *

from indexpage import IndexPage, LoginPage

#TODO : transform loading configuration via configparser module

# netmask = "192.168.0.11-14,17,18,19"
# network_prefix,ips = netmask.split('.')[:3],netmask.rpartition ('.')[2]
# for range in ips.split(','):
#     if range.find('-')>-1:
#         start,stop=map(int,range.split('-'))
#         if start > stop:
#             start,stop = stop,start
#         print(list(xrange(start,stop+1)))
#     else:
#         print(range)

auth_file = os.path.join(os.environ['HOME'],'usb_admin_auth.conf')
admin_name,admin_pass = map(lambda x: str(x).strip(),open(auth_file,'rt').read().split('\n'))[:2]
print (admin_name,admin_pass)

class WrongIPAddressStrRepresentation(Exception):

    pass


class UnregisteredMassStorageObserver(object):

    okay = simplejson.dumps({'result':'ok'})
    error = lambda x:simplejson.dumps({'result':'error','error':x})

    def __init__(self):

        self._unregistered_serials = {}

    def add_unregistered_serial(self,ip,serial):
        self._unregistered_serials.setdefault(ip,[])
        self._unregistered_serials[ip].append(serial)

    def remove_unregistered_serial(self,ip,serial):
        if self._unregistered_serials.has_key(ip):
            try:
                self._unregistered_serials[ip].remove(serial)
                return okay
            except Exception,e:
                return error(str(e))


class SingleActualSessionManager(object):
  def __init__(self,admin_name,admin_pass,max_session_seconds=5*60):
    self.admin_name = admin_name
    self.admin_pass = admin_pass
    self.last_request_time = None
    self.current_session_hash = None
    self.max_session_seconds = max_session_seconds

  def is_valid_auth_data(self,user,password):
    if (self.admin_name != user) or (self.admin_pass != password):
      return False
    else:
      return True

  def authorize(self,user,password):
    if self.is_valid_auth_data(user, password):
      self.last_request_time = now()
      self.current_session_hash = md5(self.admin_name+self.admin_pass+str(self.last_request_time)).hexdigest()
      return self.current_session_hash
    else:
      return None

  def is_authorized(self,session_hash):
    if self.last_request_time is None:
      return False
    if self.current_session_hash != session_hash:
      return False
    delta = now() - self.last_request_time
    if delta.seconds >= self.max_session_seconds:
      return False
    return True

  def logout(self):
    self.last_request_time = None

actual_session_manager = SingleActualSessionManager(admin_name, admin_pass)
request_handler = Bottle()
unregistered_devices = UnregisteredMassStorageObserver()
indexpage = IndexPage(ctx={'company':'USB monitor'})


result = lambda status,message: simplejson.dumps({'result':status,'message':message})
error = lambda message : result("error", message)
ok = lambda message : result("ok",message)


def is_authorized(func):
  def wrapper(*args,**kwargs):
    session_hash = request.get_cookie('session_hash')
    if not actual_session_manager.is_authorized(session_hash):
      return bottle.redirect('/login')
    else:
      return func(*args,**kwargs)
  return wrapper

# indexpage.get = is_authorized(indexpage.get)

@request_handler.get('/unregistered/<serial:re:[a-zA-Z0-9]+>')
def alert_unregisered_serial(serial):

    print ("IP: {} - serial {} is unregistered.".format(request['REMOTE_ADDR'],serial))

@request_handler.get('/general')
def show_general_serials():

    return simplejson.dumps(map(lambda x: {'number':x.number},GeneralSerial.select()))

@request_handler.put('/general')
@is_authorized
def add_new_serial_number():
  number = request.forms.number
  GeneralSerial.create(number=number)
  return "Ok"

@request_handler.delete('/general')
@is_authorized
def remove_general_serial_number():
  number = request.forms.number
  try:
      general_serial = GeneralSerial.get(GeneralSerial.number == number)
      general_serial.delete_instance()
  except Exception,e:
      print (e)
      pass

@request_handler.route('/static/<path:path>')
# @is_authorized
def serve_static_file(path):

    return static_file(path, root="./static")

@request_handler.route('/img/<path:path>')
def serve_image_file(path):

    return static_file(path, root="./img")

@request_handler.get('/')
@is_authorized
def index_page():

    return indexpage.get({'menu_links':[]})

@request_handler.put('/ip')
@is_authorized
def add_machine():
  ip = request.forms.get('ip')
  descr = request.forms.get('descr')
  print ("Adding...{}, {}".format(ip,descr))
  try:
      Client.create(ip_addr=ip,description=descr)
  except peewee.IntegrityError:
      pass
  return "Ok"

@request_handler.get('/ip/<machine>')
@request_handler.get('/ip')
@is_authorized
def list_machines(machine=None):
    response.content_type = 'application/json; charset=latin9'
    clients = Client.select()
    if machine is None:
        pass
        special_serial_numbers = []
    else:
        clients = filter(lambda x:x.ip_addr==machine, clients)
        if len(clients) == 0:
          return error("Not found")
        machine = Client.get(Client.ip_addr == machine)
        special_serial_numbers = ClientSerial.select().where(ClientSerial.client == machine)
        special_serial_numbers = map(lambda x: x.number, special_serial_numbers)
    return simplejson.dumps(map(lambda x: {
            'ip_addr':x.ip_addr,
            'description':x.description,
            'special_serial_numbers':special_serial_numbers,
            },clients))

@request_handler.delete('/ip')
@is_authorized
def remove_machine():
  try:
      ip_addr = request.forms.ip
      print ("ip_addr = %s" % ip_addr)
      client = Client.get(Client.ip_addr == ip_addr)
      print ("Client = %s" % client)
      client.delete_instance()
  except Exception,e:
      print (e)
      pass

@request_handler.put('/serial/<machine>')
@is_authorized
def register_serial_at_machine(machine=None):
  number = request.forms.get('number')
  try:
    machine = Client.get(Client.ip_addr == machine)
  except:
    return error("")

  if number is None:
    return error("Error!")
  try:
    ClientSerial.get(ClientSerial.number == number,ClientSerial.client == machine)
  except:
    ClientSerial.create(
                        number=number,
                        client=machine,
                        )
  return ok("")

@request_handler.delete('/serial/<serial>')
@is_authorized
def unregister_serial_at_machine(serial=None):
  if serial is None:
    return error("Not serial specified")
  try:
    client_serial = ClientSerial.get(ClientSerial.number == serial)
    client_serial.delete_instance()
    return ok("Deleted!")
  except:
    return error("Not found")

@request_handler.get('/login')
def show_login_page():
  return LoginPage().get()

@request_handler.post('/login')
def authorize_user():
  user = request.forms.get("username")
  password = request.forms.get("password")
  session_hash = actual_session_manager.authorize(user, password)
  if session_hash is None:
    error("login or password is invalid.")
  else:
    response.set_header('Set-Cookie', 'session_hash={}'.format(session_hash))
    return ok("")

@request_handler.get('/logout')
@is_authorized
def logout():
  actual_session_manager.logout()
  return bottle.redirect('/')

def main():

    run(request_handler,port=8090,reloader=True)

if __name__ == "__main__":
    main()
