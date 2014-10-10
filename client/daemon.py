import os

import urllib2

import bottle
import simplejson

import configparser

import pyudev
import evdev
import usb.core
import usb.util

configuration_file = os.path.join(os.environ['HOME'],'registered_usb_devices')

class ConfigManager(object):
    def __init__(self):
        """
        Initialization
        """
        self.loadconf()

    def loadconf(self):
        """
        Load configuration from configuration file
        """
        self._config = configparser.ConfigParser()
        try:
            self._config.read(configuration_file)
        except IOError:
            print("Configuration file({}) read-error.".format(configuration_file))
            os.sys.exit(-1)
        self.config = {}
        self.config['master_ip'] = self._config['ADMIN']['IP']
        self.config['serials'] = [key for key in self._config['SERIALS'].keys()]

    def saveconf(self):
        """
        Save configuration to the configuration file
        """
        self._config['SERIALS'] = {serial:0 for serial in self.config['serials']}
        self._config.write(open(configuration_file,'wt'))
        os.sys.exit(-1)

    def add_general_serial(self,serial):
        """
        Add general serial to configuration
        """
        try:
            self.config['serials'].index(serial)
        except ValueError:
            self.config['serials'].append(serial)

    def update_master_conf(self):
        """
        Makes request to the admin.-server to retrive general list
        of allowed(registered) serial numbers
        """
        try:
            general_serials_list = urllib2.urlopen('http://'+self.config['master_ip']+'/general',timeout=5)
            for serial in general_serials_list.split('\n'):
                self.add_general_serial(serial)
        except Exception,e:
            pass

    def remove_general_serial(self,serial):
        """
        Remove serial from general serials list in configuration
        """
        try:
            self.config['serials'].index(serial)
            self.config['serials'].remove(serial)
        except ValueError:
            pass


class USBFlashObserver(object):
    """
    USB device observer.
    It has abilities to scan connected mass storage devices
    and recive notification about new device installation into the system.
    """

    _online_devices = []

    def __init__(self,reporter,configurator):
        """
        Initialize.
        """
        self.reporter=reporter
        self.configurator=configurator
        self.loadconf()

    def loadconf(self):
        """
        Load configuration from configurator instance
        """
        self._registered_usb_devices = []
        for serial in self.configurator.config['serials']:
            self._registered_usb_devices.append(serial)

    def add_device_serial(self,serial):
        """
        Add device serial to registered list
        """
        if self._registered_usb_devices.count(serial) == 0:
            self.configurator.add_general_serial(serial)
            self.loadconf()

    def remove_device_serial(self,serial):
        """
        Remove device serial from registered devices list
        """
        if self._registered_usb_devices.count(serial) > 0:
            self.configurator.remove_general_serial(serial)
            self.loadconf()

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
                self.block_unregistered_device(device)
            else:
                self.add_online_device(serial)

        self.report_unregistered_serial(unregistered_serials)

    def report_unregistered_serial(self,device):
        """
        Report about unregistered serial
        """
        self.reporter.report(device)

    def block_unregistered_serial(self,device):
        """
        Deattach device driver
        """
        pass

    @property
    def registered_serials(self):
        """
        Returns all registered mass storage serials
        """
        return self._registered_usb_devices

    @property
    def online_serials(self):
        """
        Returns online mass storage serials
        """
        return self._online_devices


class Reporter(object):

    def __init__(self,configurator):
        """
        Initialization
        """
        self.configurator = configurator
        self.loadconf()

    def loadconf(self):
        """
        In general saves master ip-address
        """
        self.master_ip = self.configurator.config['master_ip']

    def report(self,serial):
        """
        Report about unregistered serial
        """
        self._report(serial)

    def _report(self,serial):
        """
        Make request to master about unregistered serial number
        """
        serials = list(serial)
        for serial in serials:
            try:
                urllib2.urlopen('http://'+self.master_ip+':8090/unregistered/'+serial,timeout=2)
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
    configurator = ConfigManager()
    reporter = Reporter(configurator)

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('block')

    usb_flash_observer = USBFlashObserver(reporter,configurator)
    # usb_flash_observer.add_device_serial('64I27UFQS8TK95JW')

    request_handler = bottle.Bottle()

    @request_handler.get('/device')
    @check_sender
    def show_online_devices():

        return simplejson.dumps(usb_flash_observer.online_serials)

    @request_handler.get('/registered')
    @check_sender
    def show_registered_devices():
        if not check_sender(): return
        return simplejson.dumps(usb_flash_observer.registered_serials)

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
