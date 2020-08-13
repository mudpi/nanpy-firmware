from nanpy.arduinoboard import arduinomethod, returns, FirmwareClass
from nanpy.memo import memoized


class FirmwareMissingFeatureError(Exception):
    pass


def check4firmware(cls):
    if not hasattr(check4firmware, 'names'):
        check4firmware.names = dict()
    cls_name = cls.get_firmware_id()
    assert cls_name not in check4firmware.names.keys()
    check4firmware.names[cls_name] = cls

    def getinstance(connection):
        if cls_name == 'Info':
            return cls(connection)

        if connection is not None:
            if not hasattr(connection, 'classinfo'):
                connection.classinfo = ClassInfo(connection)
            if cls_name not in connection.classinfo.firmware_id_list:
                raise FirmwareMissingFeatureError(
                    '''%s ['%s'] is missing from firmware! 
Please enable it in your cfg.h:
#define  %s  1
                    ''' %
                    (cls, cls_name, cls.cfg_h_name))
        return cls(connection)
#     getinstance.__name__ = cls.__name__
    return getinstance


@check4firmware
class ClassInfoArray(FirmwareClass):
    cfg_h_name = 'USE_Info'
    firmware_id = 'Info'

    @property
    @memoized
    @returns(int)
    @arduinomethod
    def count(self):
        pass

    @memoized
    @arduinomethod
    def name(self, index):
        pass


class ClassInfo(object):

    """Which classes are compiled into the firmware?"""

    def __init__(self, connection):
        self.firmware_class_status = dict()
        self.unknown_firmware_ids = []
        self.firmware_name_list = []
        
        self._arr = ClassInfoArray(connection=connection)

        ls = [self._arr.name(i) for i in range(self._arr.count)]
        assert len(ls)
        self.firmware_id_list = sorted(ls)

        for cls in check4firmware.names.values():
            self.firmware_class_status[cls.__name__] = False

        for x in self.firmware_id_list:
            cls = check4firmware.names.get(x)
            if cls:
                self.firmware_name_list.append(str(cls.__name__))
                self.firmware_class_status[cls.__name__] = True
            else:
                self.firmware_name_list.append(str(x))
                self.unknown_firmware_ids.append(x)
