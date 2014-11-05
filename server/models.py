import os
import peewee
import datetime

database_file = os.path.join(os.environ['HOME'],os.environ['USB_MONITOR_FILE'])

maintained_tables = []

__all__ = []

def maintained(class_):
    maintained_tables.append(class_)
    class_name = (str(class_).split("'")[1].rpartition('.')[2])
    # print class_name
    __all__.append(class_name)
    return class_


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

db = peewee.SqliteDatabase(database_file, check_same_thread=False)

class BaseModel(peewee.Model):
    class Meta:
        database = db


@maintained
class EventType(BaseModel):

    name = peewee.CharField()


@maintained
class Client(BaseModel):
    ip_addr = IPField(unique=True)
    description = peewee.CharField(max_length=200)


@maintained
class GeneralSerial(BaseModel):

    number = peewee.CharField(unique=True)


@maintained
class ClientSerial(GeneralSerial):
    client = peewee.ForeignKeyField(Client)
    number = peewee.CharField(max_length=200)

@maintained
class Event(BaseModel):
    source = peewee.ForeignKeyField(Client)
    eventtype = peewee.ForeignKeyField(EventType)
    datetime = peewee.DateTimeField(default=datetime.datetime.now)

db.connect()
map(lambda x: x.create_table(fail_silently=True),maintained_tables)
