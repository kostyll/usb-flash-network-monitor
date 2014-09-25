import os

import urllib2

import bottle
import simplejson

import pyudev
import evdev
import usb.core
import usb.util

#TODO : transform loading configuration via configparser module

configuration_file = os.path.join(os.environ['HOME'],'registered_usb_devices')
# master_ip = os.environ['USB_OBSERVER_IP']
master_ip = "127.0.0.1"

class USBFlashObserver(object):
    """
    USB device observer.
    It has abilities to scan connected mass storage devices.
    """

    _registered_usb_devices = []
    _online_devices = []

    def __init__(self,reporter_instance):
        self.reporter=reporter_instance
        self.loadconf()

    def load_registered_serials_from_data(self,data):
        """
        Add's every serial from iterable object to registered devices list
        """
        for serial in data:
            serial._registered_usb_devices.append(serial.strip('\n'))

    def loadconf(self):
        """
        Load configuration: a list of registered devices
        """
        try:
            self.load_registered_serials_from_data(open(configuration_file,'rt'))
        except IOError:
            pass
        self.check_unregistered_devices()

    def saveconf(self):
        """
        Save configuration: a new list of registered devices
        """
        with open(configuration_file,'wt') as f:
            for serial in self._registered_usb_devices:
                f.write("{}\n".format(serial))

    def update_master_conf(self):
        """
        Makes request to the admin.-server to retrive general list
        of allowed(registered) serial numbers
        """
        try:
            general_serials_list = urllib2.urlopen('http://'+master_ip+'/general',timeout=5)
            self.load_registered_serials_from_data(general_serials_list)
        except Exception,e:
            pass

    def add_device_serial(self,serial):
        """
        Add device serial to registered list
        """
        if self._registered_usb_devices.count(serial) == 0:
            self._registered_usb_devices.append(serial)

    def remove_device_serial(self,serial):
        """
        Remove device serial from registered devices list
        """
        if self._registered_usb_devices.count(serial) > 0:
            while self._registered_usb_devices.count(serial) > 0:
                self._registered_usb_devices.remove(serial)

    def add_online_device(self,serial):
        """
        Add serial device to online devices
        """
        if self._online_devices.count(serial) <= 0:
            self._online_devices.append(serial)

    def remove_online_device(self,serial):
        """
        Remove serial device from online devices
        """
        if self._online_devices.count(serial) > 0:
            self._online_devices.remove(serial)

    def check_serial_existance(self,serial):
        """
        returns True if device serial is registered
        else - False
        """
        if self._registered_usb_devices.count(serial) > 0:
            return True
        else:
            return False

    def get_mass_storage_usb_devices(self):
        """
        Getting the list of serial numbers of all usb flash drives.
        """
        mass_storage_usb_devices = list(usb.core.find(find_all=True))
        mass_storage_usb_devices = filter(lambda x: x.product == "Mass Storage Device", mass_storage_usb_devices)
        return mass_storage_usb_devices

    def check_unregistered_devices(self):
        """
        Check online devices.
        Returns True if there is an unregistered device in online devices list.
        Else - False.
        """
        unregistered_serials = set()
        online_devices = self.get_mass_storage_usb_devices()
        for device in online_devices:
            serial = device.serial_number
            if not self.check_serial_existance(serial):
                unregistered_serials.add(serial)
            else:
                self.add_online_device(serial)

        self.report_unregistered_serial(unregistered_serials)

    def report_unregistered_serial(self,device):
        """
        Report about unregistered serial
        """
        self.reporter.report(device)

    def get_registered_devices(self):

        return self._registered_usb_devices

    def get_online_devices(self):

        return self._online_devices


class Reporter(object):
    def __init__(self):

        self.loadconf()

    def loadconf(self):

        self.master_ip = master_ip

    def report(self,serial):

        self._report(serial)

    def _report(self,serial):
        serials = list(serial)
        for serial in serials:
            try:
                urllib2.urlopen('http://'+master_ip+':8090/unregistered/'+serial,timeout=2)
            except:
                pass


def check_sender(func):
    def wrapper(*args,**kwargs):
        if request['REMOTE_ADDR'] == master_ip:
            return func(*args,**kwargs)
        else:
            return
    return wrapper

def main():
    reporter = Reporter()

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('block')

    usb_flash_observer = USBFlashObserver(reporter)
    # usb_flash_observer.add_device_serial('64I27UFQS8TK95JW')

    request_handler = bottle.Bottle()

    @request_handler.get('/device')
    @check_sender
    def show_online_devices():

        return simplejson.dumps(usb_flash_observer.get_online_devices())

    @request_handler.get('/registered')
    @check_sender
    def show_registered_devices():
        if not check_sender(): return
        return simplejson.dumps(usb_flash_observer.get_registered_devices())

    @request_handler.post('/registered')
    @check_sender
    def register_device_serial():
        try:
            serial = bottle.request.forms.get('serial')
            usb_flash_observer.add_device_serial(serial)
            usb_flash_observer.saveconf()
            return simplejson.dumps({'result':'ok'})
        except Exception,e:
            return simplejson.dumps({'result':'error'})

    @request_handler.delete('/registered')
    @check_sender
    def delete_device_serial():
        try:
            serial = bottle.request.forms.get('serial')
            usb_flash_observer.remove_device_serial(serial)
            usb_flash_observer.saveconf()
            return simplejson.dumps({'result':'ok'})
        except Exception,e:
            return simplejson.dumps({'result':'error','error':e})

    def log_envent(action,device):
        if action == "add":
            print ("Device {} has been added!".format(device))
            usb_flash_observer.check_unregistered_devices()
        elif action == "remove":
            print ("Device {} has been removed!".format(device))

    observer = pyudev.MonitorObserver(monitor,log_envent)
    observer.start()
    bottle.run(request_handler,reloader=True)
    while True:
        pass

if __name__ == "__main__":
    print ("Start monitoring ...")
    main()
