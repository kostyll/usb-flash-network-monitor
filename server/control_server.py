import bottle
from bottle import run, request, Bottle

import simplejson

import html

from web_face_gen_templatete import render_html
from utils import _


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

class ClientsManager(object):

    _clients_ips = []

    def __init__(self):

        pass

    @property
    def clients_ips(self):

        return self._clients_ips

    def client_ip_existance(self,ip):
        try:
            self.clients_ips.index(ip)
            return True
        except ValueError:
            return False

    def add_client_ip(self,ip):
        if not self.client_ip_existance(ip):
            self._clients_ips.append(ip)

    def remove_client_ip(self,ip):
        if self.client_ip_existance(ip):
            self._clients_ips.remove(ip)


class GeneralDataProvider(object):

    _general_serials = []

    def __init__(self):

        self.loadconf()

    @property
    def general_serials(self):

        return self._general_serials

    def loadconf(self):

        pass

    def saveconf(self):

        pass

    def add_serial_to_general(self,serial):
        if not self.serial_existance(serial):
            self._general_serials.append(serial)

    def remove_serial_from_general(self,serial):
        if self.serial_existance(serial):
            self._general_serials.remove(serial)

    def serial_existance(self,serial):
        try:
            self.general_serials.index(serial)
            return True
        except ValueError:
            return False


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


def rendered(func):
    def wrapper(self,ctx):
        html.context = html.StrContext()
        carred_func = lambda *args: func(self,args[0])
        return render_html(ctx, carred_func)
    return wrapper

class WebFace(object):
    def __init__(self):
        self.ctx = {}
    @rendered
    def index(self,ctx):
        with DIV.container_fluid as out:
            out << "Ingex Page"
        return out


request_handler = Bottle()
general_data_provider = GeneralDataProvider()

@request_handler.get('/unregistered/<serial:re:[a-zA-Z0-9]+>')
def alert_unregisered_serial(serial):

    print ("IP: {} - serial {} is unregistered.".format(request['REMOTE_ADDR'],serial))

@request_handler.get('/general')
def show_general_serials():

    return simplejson.dumps(general_data_provider.general_serials)

@request_handler.get('/')
def index_page():

    return

def main():
    run(request_handler,port=8090,reloader=True)

if __name__ == "__main__":
    main()
