import bottle
from bottle import run, request, Bottle

import simplejson

request_handler = Bottle()

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


@request_handler.get('/unregistered/<serial:re:[a-zA-Z0-9]+>')
def alert_unregisered_serial(serial):
    print ("IP: {} - serial {} is unregistered.".format(request['REMOTE_ADDR'],serial))

@request_handler.get('/')
def index_page():
    pass

def main():
    run(request_handler,port=8090,reloader=True)

if __name__ == "__main__":
    main()
