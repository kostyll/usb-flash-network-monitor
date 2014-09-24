import os

import pyudev
import evdev
import usb.core
import usb.util

configuration_file = os.path.join(os.environ['HOME'],'registered_usb_devices')

class USBFlashObserver(object):
    """
    USB device observer.
    It has abilities to scan connected mass storage devices.
    """

    _registered_usb_devices = [
    """
    Contains the serial numbers of all registered usb flash drives
    """
    ]
    _online_devices = [
    """
    Contains the serials of connected usb flash devices
    """
    ]

    def __init__(self,reporter_instance):
        self.reporter=reporter_instance
        self.loadconf()

    def loadconf(self):
        """
        Load configuration: a list of registered devices
        """
        try:
            with open(configuration_file,'rt') as f:
                for serial in f:
                    self._registered_usb_devices.append(serial.strip('\n'))
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
            self.online_devices.append(serial)

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

        self.report_unregistered_serial(unregistered_serials)

    def report_unregistered_serial(self,device):
        """
        Report about unregistered serial
        """
        self.reporter.report("Serial {} is unregistered.".format(device))


class Reporter(object):
    def __init__(self):
        self.loadconf()

    def loadconf(self):
        pass

    def report(self,message):
        self._report(message)

    def _report(self,message):
        print (message)


def main():
    reporter = Reporter()

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('block')

    usb_flash_observer = USBFlashObserver(reporter)
    usb_flash_observer.add_device_serial('64I27UFQS8TK95JW')

    def log_envent(action,device):
        if action == "add":
            print ("Device {} has been added!".format(device))
            usb_flash_observer.check_unregistered_devices()
        elif action == "remove":
            print ("Device {} has been removed!".format(device))

    observer = pyudev.MonitorObserver(monitor,log_envent)
    observer.start()
    while True:
        pass

if __name__ == "__main__":
    print ("Start monitoring ...")
    main()
