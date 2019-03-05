from .Base import ADSIBaseObject
from .utils import escape_path

#   LDAP Section greatly inspired by pyad
#
#
#


class LDAPObject(ADSIBaseObject):
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        self._gc_obj =None
        self._domain_obj=None
        super().__init__(identifier, adsi_com_object, options)


    def _set_adsi_obj(self):
        if self._username and self._password:
            self._credential_adsi_obj(self._username, self._password)
        elif self.default_username and self.default_password:
            self._credential_adsi_obj(self._default_username, self._default_password)
        elif self._ssl:
            self._ssl_adsi_obj()
        elif self.default_ssl:
            self._ssl_adsi_obj()
        else:
            self._adsi_obj = self.adsi_provider.getObject('', self._adsi_path)

    def _ssl_adsi_obj(self):
        raise Exception("Using SSL without specifying credentials is currently unsupported due to what appears to be a bug in pywin32.")
        _ds = self.adsi_provider.getObject('',"LDAP:")
        # from: http://msdn.microsoft.com/en-us/library/windows/desktop/aa772247(v=vs.85).aspx
        # If ADS_USE_SSL is not combined with the ADS_SECURE_AUTHENTICATION
        # flag and the supplied credentials are NULL, the bind will be
        # performed anonymously. If ADS_USE_SSL is combined with the
        # ADS_SECURE_AUTHENTICATION flag and the supplied credentials
        # are NULL, then the credentials of the calling thread are used.
        flag = ADS_AUTHENTICATION_TYPE['ADS_SECURE_AUTHENTICATION'] | \
                        ADS_AUTHENTICATION_TYPE['ADS_USE_ENCRYPTION']
        _ds = self.adsi_provider.getObject('', "LDAP:")
        self._adsi_obj = _ds.OpenDSObject(
                        self._adsi_path,
                        None, # username
                        None, # password
                        flag)

    def _credential_adsi_obj(self, username, password):
        _ds = self.adsi_provider.getObject('',"LDAP:")
        if self._authentication_flag and self._authentication_flag > 0:
            flag = self._authentication_flag
        elif self.default_authentication_flag > 0:
            flag = self.default_authentication_flag
        else:
            # I'm choosing to force encryption of the login credentials.
            # This does not require SSL to be configured, so I believe this
            # should work for everyone. If not, we can change later.
            flag = ADS_AUTHENTICATION_TYPE['ADS_SECURE_AUTHENTICATION']
            if self.default_ssl:
                flag = flag | ADS_AUTHENTICATION_TYPE['ADS_USE_ENCRYPTION']
        self._adsi_obj = _ds.OpenDSObject(
                self._adsi_path,
                username,
                password,
                flag)


    def _generate_adsi_path(self, identifier):
        if not self._valid_protocol(self._protocol):
            raise Exception("Invalid Protocol for. Protocol is required to be WinNT")
        """Generates a proper ADsPath to be used when connecting to an active directory object or when searching active directory.

        Keyword arguments:
         - distinguished_name: DN of object or search base such as 'cn=zakir,ou=users,dc=mycompany,dc=com' (required).
         - type: 'GC' (global-catalog) or 'LDAP' to determine what directory to be searched (required).
         - server: FQDN of domain controller if necessary to connect to a particular server (optional unless port is defined).
         - port: port number for directory service if not default port. If port is specified, server must be specified (optional)."""
        type_ = self._protocol
        #if type_ == "LDAP"  or type_ == "LDAPS":
        server = self._server #if self._server else self.default_server
        port = self._port #if self._port else ADBase.default_port
        # elif type_ == "GC":
        #     server = self._server #if self._server else ADBase.default_gc_server
        #     port = self._port #if self._port else ADBase.default_gc_port
        #else:
        #    raise Exception("Invalid type specified.")
        ads_path = ''.join((type_,'://'))
        if server:
            ads_path = ''.join((ads_path,server))
            if port:
                ads_path = ':'.join((ads_path,str(port)))
            ads_path = ''.join((ads_path,'/'))
        ads_path = ''.join((ads_path,escape_path(distinguished_name)))
        print(ads_path)
        return ads_path

    def _schema(self):
        raise NotImplementedError()

    def _valid_protocol(self, protocol):
        if not protocol.isupper():
            protocol = protocol.upper()
        return ( protocol == 'LDAP' or protocol == 'GC' )

    ###################################
    #   Dict Section
    #   Allow access to LDAP attributes
    #   As if object is dict
    #
    #   Due to nature of LDAP, we want
    #   To have attributes accessed via
    #   LDAPOBJ['Attribute']
    ###################################

    def __setitem__(self, key, item):
        setattr(self._adsi_obj, key, item)

    def __getitem__(self, key):
        try:
            return self._adsi_obj.Get(attrib)
        except:
            raise InvalidAttribute(self.dn, key)

    def __delitem__(self, key):
        if self.has_key(key):
            pass

    def has_key(self, key):
        return hasattr(self._adsi_obj, key)

    def keys(self):
        return self.get_attributes()

    def values(self):
        for attr in self.keys():
            yield attr, self.__getitem__(attr)
