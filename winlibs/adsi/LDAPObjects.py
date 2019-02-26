from .ADSIBase import ADSIBaseObject

class LDAPObject(ADSIBaseObject):

    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super().__init__(identifier, adsi_com_object, options)

    def _set_adsi_obj(self):
        raise NotImplementedError()

    def _generate_adsi_path(self, identifier):
        raise NotImplementedError()

class LDAPContainer(LDAPObject)
