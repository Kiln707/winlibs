from .adsi.Base import ADSIBaseObject
from .adsi.utils import escape_path

class NTObject(ADSIBaseObject):

    _class = None

    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super(ADSIBaseObject, self).__init__(identifier, adsi_com_object, options)

    def apply_nt_settings(self, options):
        print('Setting Protocol')
        options['protocol']="WinNT"

    def __set_adsi_obj(self):
        #Create connection to ADSI
        if not self._valid_protocol():
            raise Exception("Invalid protocol. Valid Protocols: LDAP, GC, WinNT")
        if self._username and self._password:
            self._adsi_obj = self.__get_adsi_obj_by(self._adsi_path, self._username, self._password)
        elif self.default_username and self.default_password:
            self._adsi_obj = self.__get_adsi_obj_by(self._adsi_path, self.default_username, self.default_password)
        elif self.default_ssl:
            #Need to setup SSL
            pass
        else:
            self._adsi_obj = self.adsi_provider.getObject('', self._adsi_path)

    def __get_adsi_obj_by(self, identifier, username, password):
        return self.adsi_provider.OpenObject('', username, password, 0, identifier)

    def _set_identifier(self):
        raise NotImplementedError()

    def _generate_adsi_path(self, identifier):
        if not self._valid_protocol(self._protocol):
            raise Exception("Invalid Protocol for. Protocol is required to be WinNT")
        adsi_path = ''.join((self._protocol, '://'))
        if self._server:
            adsi_path =''.join((adsi_path,self._server))
            if self._port:
                adsi_path = ':'.join((adsi_path, str(self._port)))
            adsi_path =''.join((adsi_path, '/'))
        adsi_path = ''.join((adsi_path, escape_path(identifier)))
        if self._class:
            adsi_path = ','.join((adsi_path,self._class))
        return adsi_path


class NTUser(NTObject):

    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        self.apply_nt_settings(options)
        super(NTObject,self).__init__(identifier, adsi_com_object, options)
