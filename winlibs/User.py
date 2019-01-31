import win32net, win32security
from datetime import datetime, timedelta, date
from pyad import aduser
from ADQuery import query

class WinUser:

    attrib_prop_map={}

    def __init__(self, username=None, domain=None, SID=None):
        userdata={}
        if SID:
            account_lookup = WinUser.__getADUserAccountInfo(SID)
            userdata = WinUser.__getLocalUserInfo(username=account_lookup[0], server=account_lookup[1])
        elif username:
            userdata = WinUser.__getLocalUserInfo(username=username, server=domain)
        elif domain:
            raise ValueError('Username is required when domain is used.')
        else:
            raise ValueError('SID or Username is required to initialize WinUser')
        self._name = userdata['name']
        self._password=userdata['password']
        self._password_age = userdata['password_age']
        self._password_last_changed = (datetime.now() - timedelta(seconds=userdata['password_age'])).date()
        if userdata['priv'] == 0:
            self._user_type = 'Guest'
        elif userdata['priv'] == 1:
            self._user_type = 'User'
        elif userdata['priv'] == 2:
            self._user_type = 'Administrator'
        self._home_dir = userdata['home_dir']
        self._comment = userdata['comment']
        self._full_name = userdata['full_name']
        self._usr_comment = userdata['usr_comment']
        self._parms = userdata['parms']
        self._workstations = userdata['workstations']
        self._last_logon = datetime.utcfromtimestamp(userdata['last_logon'])
        self._last_logoff = userdata['last_logoff']
        self._expires = datetime.utcfromtimestamp(userdata['acct_expires'])
        self._max_storage = userdata['max_storage']
        self._units_per_week = userdata['units_per_week']
        self._logon_hours = userdata['logon_hours']
        self._bad_pw_count = userdata['bad_pw_count']
        self._num_logons = userdata['num_logons']
        self._logon_server = userdata['logon_server']
        self._country_code = userdata['country_code']
        self._code_page = userdata['code_page']
        self.__SID = userdata['user_sid']
        self._primary_group =None
        self._profile = userdata['profile']
        self._home_dir_drive = userdata['home_dir_drive']
        self._password_is_expired = userdata['password_expired'] != 0

        self.__aduser=None
        if self._full_name:
            try:
                self.__aduser = WinUser.__getADUserByCN(self._full_name)
            except:
                pass
        if not self.__aduser and self._name:
            try:
                self.__aduser = WinUser.__getADUserBySAM(self._name)
            except:
                pass
        if self.__aduser:
            self._distinguished_name = self.__aduser._ADObject__distinguished_name
            self._default_domain = self.__aduser.default_domain
            self.__attributes={}
            for attr in self.__aduser.get_allowed_attributes():
                self.__attributes[attr] = self.__aduser.get_attribute(attr)
        # for i in dir(self.__aduser):
        #     print(i)

    def __setattr__(self, name, value):
        pass


    @property
    def SID(self):
        return self.__SID

    def get_attribute_list(self):
        return self.__attributes.keys()

    def get_attribute(self, attribute):
        attrib = self.__attributes[attribute]
        try:
            if len(attrib) != 1:
                return attrib
            return attrib[0]
        except:
            return None

    def set_attribute(self, attribute, value):
        if value is None:
            value = []
        self.__attributes[attribute]=value

    def map_attribute_property(self, property='', attribute=''):
        if hasattr(self, property):
            if property in self.__class__.attrib_prop_map:
                self.__class__.attrib_prop_map[property].append(attribute)
            else:
                self.__class__.attrib_prop_map[property] = [attribute]
        else:
            raise ValueError("Class does not contain property")

    def remove_attribute_property_map(self, property='', attribute=''):
        if hasattr(self, property):
            if self.__class__.attrib_prop_map[property]:
                self.__class__.attrib_prop_map[property].remove(attribute)
        else:
            raise ValueError("Class does not contain property")

    def get_attribute_property_map(self):
        return dict(self.__class__.attrib_prop_map)

    @staticmethod
    def __getADUserAccountInfo(sid):
        if type(SID) == str:
            return win32security.LookupAccountSid(None, win32security.GetBinarySid(SID))
        elif isinstance(SID, win32security.SID().__class__):
            return win32security.LookupAccountSid(None, SID)
        else:
            raise ValueError('SID Must be of type PySID or str.')

    @staticmethod
    def __getADUserBySAM(username):
        q = query(get_attributes=['distinguishedName'], where_clause="sAMAccountName = '%s'"%username, base_dn="DC=solano, DC=cc, DC=ca, DC=us") #TODO: Replace Base_DN with global config
        if len(q) > 1:
            raise Exception("There are multiple records with that SAMAccountName")
        return WinUser.__getADUserInfo(q[0]['distinguishedName'])

    @staticmethod
    def __getADUserByCN(CN):
        return aduser.ADUser.from_cn(CN)

    @staticmethod
    def __getADUserInfo(distinguishedName):
        return aduser.ADUser(distinguishedName)

    @staticmethod
    def __getLocalUserInfo(username, server=None, level=4):
        return win32net.NetUserGetInfo(server, username, level)
