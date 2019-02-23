from .Base import ADSIBaseObject, _default_detected_domain, IContainer
from .utils import escape_path
import socket

class NTObject(ADSIBaseObject):

    _class = None
    default_protocol='WinNT'
    default_domain=ADSIBaseObject.default_ntdomain
    default_server=ADSIBaseObject.default_ntdomain

    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        if 'protocol' in options:
            del options['protocol']
        super().__init__(identifier, adsi_com_object, options)

    def _set_adsi_obj(self):
        #Create connection to ADSI
        if not self._valid_protocol(self._protocol):
            raise Exception("Invalid protocol. Valid Protocols: LDAP, GC, WinNT")
        self._adsi_obj = self.adsi_provider.getObject('', self._adsi_path)

    def valid_protocol(self, protocol):
        return protocol == 'WinNT'

    def _generate_adsi_path(self, identifier):
        if not self.valid_protocol(self._protocol):
            raise Exception("Invalid Protocol for. Protocol is required to be WinNT")
        adsi_path = ''.join((self._protocol, '://'))
        if self._server:
            adsi_path =''.join((adsi_path,self._server))
            if self._port:
                adsi_path = ':'.join((adsi_path, str(self._port)))
        else:
            adsi_path = ''.join((adsi_path,socket.gethostname()))
        adsi_path =''.join((adsi_path, '/'))
        adsi_path = ''.join((adsi_path, escape_path(identifier)))
        if self._class:
            adsi_path = ','.join((adsi_path,self._class))
        print(adsi_path)
        return adsi_path

class NTDomain(NTObject, IContainer):
    _class = 'Domain'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

class NTComputer(NTObject, IContainer):
    _class = 'Computer'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)

    def shutdown(self, reboot=False):
        self._adsi_obj.Shutdown(reboot)

    def status(self):
        return self._adsi_obj.Status()

class NTUser(NTObject):
    _class = 'User'

    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super().__init__(identifier, adsi_com_object, options)

    def change_password(self, old_password, new_password):
        self._adsi_obj.SetPassword(password)

    def groups(self):
        pass

    def set_password(self, password):
        self._adsi_obj.SetPassword(password)

class NTFileService(NTObject, IContainer):
    _class = 'FileService'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super().__init__(identifier, adsi_com_object, options)

    def _resources(self):
        return self._adsi_obj.Resources()

    def _sessions(self):
        pass

    def sessions(self):
        pass
