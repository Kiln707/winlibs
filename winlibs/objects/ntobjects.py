from .ADSIBase import ADSIBaseObject

class NTObject(ADSIBaseObject):

    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super().__init__(identifier, adsi_com_object, options)

    def __set_adsi_obj(self):
        raise NotImplementedError()

    def _set_identifier(self):
        raise NotImplementedError()

class NTUser(NTObject):

    def __init__(self):
        pass
