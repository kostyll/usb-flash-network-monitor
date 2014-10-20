import os
import bottle
from bottle import run, request, Bottle, static_file, response

import simplejson

import peewee

from indexpage import IndexPage

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

database_file = os.path.join(os.environ['HOME'],os.environ['USB_MONITOR_FILE'])

class WrongIPAddressStrRepresentation(Exception):
    pass


class IPField(peewee.Field):
    db_field = 'int'
    octet_offsets = [24,16,8,0]
    def check_str_representation(self,value):
        octets = str(value).split('.')
        if len(octets) != 4:
            raise WrongIPAddressStrRepresentation(value)
        for octet in octets:
            try:
                octet = int(octet)
            except ValueError:
                raise WrongIPAddressStrRepresentation(value)
            if octet<0 or octet>255:
                raise WrongIPAddressStrRepresentation(value)

    def db_value(self,value):
        self.check_str_representation(value)
        octets = map(int, str(value).split('.'))
        octets = map(lambda x,y: x<<y, octets,self.octet_offsets)
        result = sum(octets)
        # print ('result = {}'.format(result))
        return  result

    def python_value(self,value):
        octets = map(lambda y: (value >> y), self.octet_offsets)
        # print ("octets {}".format(octets))
        octets = map(lambda x: x % (2**8), octets)
        # print ("octets {}".format(octets))
        result = ".".join(map(str,octets))
        # print ('result = {}'.format(result))
        return result


peewee.SqliteDatabase.register_fields({'int':'int'})

db = peewee.SqliteDatabase(database_file)

class BaseModel(peewee.Model):
    class Meta:
        database = db


class Client(BaseModel):

    ip_addr = IPField(unique=True)

    description = peewee.CharField(max_length=200)


class GeneralSerial(BaseModel):

    number = peewee.CharField(unique=True)


class ClientSerial(GeneralSerial):

    client = peewee.ForeignKeyField(Client)
    number = peewee.CharField(max_length=200)


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

request_handler = Bottle()
unregistered_devices = UnregisteredMassStorageObserver()
indexpage = IndexPage(ctx={'company':'USB monitor'})

result = lambda status,message: simplejson.dumps({'result':status,'message':message})
error = lambda message : result("error", message)
ok = lambda message : result("ok",message)

@request_handler.get('/unregistered/<serial:re:[a-zA-Z0-9]+>')
def alert_unregisered_serial(serial):

    print ("IP: {} - serial {} is unregistered.".format(request['REMOTE_ADDR'],serial))

@request_handler.get('/general')
def show_general_serials():

    return simplejson.dumps(map(lambda x: {'number':x.number},GeneralSerial.select()))

@request_handler.put('/general')
def add_new_serial_number():
  number = request.forms.number
  GeneralSerial.create(number=number)
  return "Ok"

@request_handler.delete('/general')
def remove_general_serial_number():
  number = request.forms.number
  try:
      general_serial = GeneralSerial.get(GeneralSerial.number == number)
      general_serial.delete_instance()
  except Exception,e:
      print (e)
      pass

@request_handler.route('/static/<path:path>')
def serve_static_file(path):
    return static_file(path, root="./static")

@request_handler.route('/img/<path:path>')
def serve_image_file(path):
    return static_file(path, root="./img")

@request_handler.get('/')
def index_page():
    return indexpage.get({'menu_links':[]})

@request_handler.put('/ip')
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

def main():
    db.connect()
    map(lambda x: x.create_table(fail_silently=True),[Client,GeneralSerial,ClientSerial])
    run(request_handler,port=8090,reloader=True)

if __name__ == "__main__":
    main()
