import os
import sys
import urllib2
from md5 import md5
import datetime
now = datetime.datetime.now
import bottle
from bottle import run, request, Bottle, static_file, response, ServerAdapter, debug

import simplejson

from models import *

from indexpage import IndexPage, LoginPage
import peewee

_ = lambda x: x

debug(True)
DEBUG=True

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

# Trying SSL with bottle
# ie combo of http://www.piware.de/2011/01/creating-an-https-server-in-python/
# and http://dgtool.blogspot.com/2011/12/ssl-encryption-in-python-bottle.html
# without cherrypy?
# requires ssl

# to create a server certificate, run eg
# openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
# DON'T distribute this combined private/public key to clients!
# (see http://www.piware.de/2011/01/creating-an-https-server-in-python/#comment-11380)
class SSLWSGIRefServer(ServerAdapter):
    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        import ssl
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        srv = make_server(self.host, self.port, handler, **self.options)
        srv.socket = ssl.wrap_socket (
            srv.socket,
            certfile='server.pem',  # path to certificate
            server_side=True)
        srv.serve_forever()

# class SSLCherryPyServer(ServerAdapter):
#   def run(self, handler):
#     from cherrypy import wsgiserver
#     server = wsgiserver.CherryPyWSGIServer((self.host, self.port), handler)
#     server.ssl_certificate = "server.pem"
#     server.ssl_private_key = "key.pem"
#     try:
#       server.start()
#     finally:
#       server.stop()


auth_file = os.path.join(os.environ['HOME'],os.environ['USB_CONFIG_FILE'])
admin_name,admin_pass = map(lambda x: str(x).strip(),open(auth_file,'rt').read().split('\n'))[:2]
print (admin_name,admin_pass)

class WrongIPAddressStrRepresentation(Exception):

    pass


class UnregisteredMassStorageObserver(object):

    okay = simplejson.dumps({'result':'ok'})
    error = lambda x:simplejson.dumps({'result':'error','error':x})

    def __init__(self):

        self._unregistered_serials = {}
        self.process_update()

    def process_update(self):
        self._last_update = now()

    def add_unregistered_serial(self,ip,serial):
        serial = serial.lower()
        try:
          ClientSerial.get(ClientSerial.number==serial)
          return
        except:
          pass
        try:
          GeneralSerial.get(GeneralSerial.number==serial)
          return
        except:
          pass
        self._unregistered_serials.setdefault(ip,[])
        if len(self._unregistered_serials[ip])>0:
          try:
            self._unregistered_serials[ip].index(serial)
          except ValueError:
            self._unregistered_serials[ip].append(serial)
        else:
          self._unregistered_serials[ip].append(serial)
        self.process_update()

    def remove_unregistered_serial(self,ip,serial):
        if self._unregistered_serials.has_key(ip):
            try:
                self._unregistered_serials[ip].remove(serial)
                return okay
            except Exception,e:
                return error(str(e))
        self.process_update()

    @property
    def list_unregistered_serials(self):
        return self._unregistered_serials

    @property
    def current_state_hash (self):
        session_hash = md5(str(self._unregistered_serials)+str(self._last_update)).hexdigest()
        return session_hash


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
request_handler = bottle.Bottle()

unregistered_devices = UnregisteredMassStorageObserver()
indexpage = IndexPage(ctx={
                      'company':'USB monitor',
                      'right_menu_links':[
                        (_("Log out"),"/logout"),
                        ]
                      })

result = lambda status,message: simplejson.dumps({'result':status,'message':message})
error = lambda message : result("error", message)
ok = lambda message : result("ok",message)

def update_client_conf(ip_addr):
    try:
      urllib2.urlopen("http://"+ip_addr+':8091'+'/updateconf',timeout=2)
      return True
    except Exception,e:
      return error(str(e))

def is_authorized(func):
  if not DEBUG:
    def wrapper(*args,**kwargs):
      session_hash = request.get_cookie('session_hash')
      if not actual_session_manager.is_authorized(session_hash):
        return bottle.redirect('/login')
      else:
        return func(*args,**kwargs)
    return wrapper
  else:
    return func

@request_handler.get('/unregistered/<serial:re:[a-zA-Z0-9]+>')
def alert_unregisered_serial(serial):
    ip = request['REMOTE_ADDR']
    print ("IP: {} - serial {} is unregistered.".format(ip,serial))
    unregistered_devices.add_unregistered_serial(ip, serial)

@request_handler.get("/unregistered")
def show_all_unregistered():
    return ok(message=unregistered_devices.list_unregistered_serials)

@request_handler.get('/system/state')
@is_authorized
def get_current_system_state_hash():
    return ok(message={
                'system_state_hash':unregistered_devices.current_state_hash
              })

@request_handler.get('/general')
def show_general_serials():

    return simplejson.dumps(
        map(
            lambda x: {'number':x.number},
            GeneralSerial.select()
        )
    )

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

@request_handler.get('/serial')
def list_specialized_serials():
  ip_addr = request["REMOTE_ADDR"]
  print "ip_addr"
  print ip_addr

  try:
    machine = Client.get(Client.ip_addr==ip_addr)
    print machine
  except Exception,e:
    print e
    return error("Client is not in the register")
  try:
    serials = ClientSerial.select().where(ClientSerial.client==machine)
    serials = [client_serial.number for client_serial in serials]
  except Exception,e:
    return error("Db error "+str(e))
  return ok(serials)


@request_handler.put('/serial')
@is_authorized
def register_serial_at_machine():
  machine = request.forms.get('machine')
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
    print ("removing serial from unregistered devices")
    unregistered_devices.remove_unregistered_serial(machine.ip_addr, number)
    update_client_conf(machine.ip_addr)
  return ok("")

@request_handler.delete('/serial')
@is_authorized
def unregister_serial_at_machine():
  print ("deleting...") 
  serial=request.forms.get('number')
  if serial is None:
    return error("Not serial specified")
  try:
    client_serial = ClientSerial.get(ClientSerial.number == serial)
    machine = client_serial.client
    client_serial.delete_instance()
    # print ("adding serial to unregistered...")
    # unregistered_devices.add_unregistered_serial(machine.ip_addr, client_serial.number)
    update_client_conf(machine.ip_addr)
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

def run_web_face(host="localhost",port=8080,):
    srv = SSLWSGIRefServer(port=8080)#,host="0.0.0.0",)
    run(request_handler,host=host,port=port,reloader=True,server=srv)

def main():
    run_web_face()
    # run(app=request_handler,reloader=True,server=SSLWSGIRefServer)

    # httpd = SecureHTTPServer(('0.0.0.0',8080), request_handler)
    # httpd.serve_forever()

    # httpd.socket = ssl.wrap_socket (httpd.socket, certfile='server.pem', server_side=True)

if __name__ == "__main__":
    # euid = os.geteuid()
    # if euid != 0:
    #     print "Script not started as root. Running sudo.."
    #     args = ['sudo', sys.executable] + sys.argv + [os.environ]
    #     # the next line replaces the currently-running process with the sudo
    #     os.execlpe('sudo', *args)
    # print 'Running. Your euid is', euid
    # new_pid = os.fork()
    # if new_pid == 0:
      main()
    # else:
    #   pid_file = open('cs.pid','wt')
    #   pid_file.write(str(new_pid))
    #   pid_file.close()
    #   os.sys.exit()


