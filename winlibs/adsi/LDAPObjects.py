from .Base import ADSIBaseObject, I_User, I_Group
from .utils import escape_path

from pywintypes import IID, SID

#   LDAP Section greatly inspired by (taken from) pyad
class LDAPBaseObject(ADSIBaseObject):
    _class = None
    default_protocol='LDAP'
    _attributes=None
    _obj_map={}

    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        self.__class__.__name__
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

    def _valid_protocol(self, protocol):
        if not protocol.isupper():
            protocol = protocol.upper()
        return protocol == 'LDAP'

    def _set_attributes(self):
        for attr in self.get_attributes():
            if attr == 'type':
                continue
            setattr(self, attr, self.get(attr))

    def _generate_adsi_path(self, distinguished_name):
        # Generates a proper ADsPath to be used when connecting to an active directory object or when searching active directory.
        #
        # Keyword arguments:
        #  - distinguished_name: DN of object or search base such as 'cn=zakir,ou=users,dc=mycompany,dc=com' (required).
        #  - type: 'GC' (global-catalog) or 'LDAP' to determine what directory to be searched (required).
        #  - server: FQDN of domain controller if necessary to connect to a particular server (optional unless port is defined).
        #  - port: port number for directory service if not default port. If port is specified, server must be specified (optional).
        ads_path = ''.join((self.default_protocol,'://'))
        if self._server:
            ads_path = ''.join((ads_path,self._server))
            if self._port:
                ads_path = ':'.join((ads_path,str(self._port)))
            ads_path = ''.join((ads_path,'/'))
        ads_path = ''.join((ads_path,escape_path(distinguished_name)))
        return ads_path

class ADObject(LDAPBaseObject):
    _py_ad_object_mappings = {}

    # http://msdn.microsoft.com/en-us/library/aa772300.aspx
    ADS_USER_FLAG = {
    'SCRIPT':0x1,
    'ACCOUNTDISABLE':0x2,
    'HOMEDIR_REQUIRED':0x8,
    'LOCKOUT':0x10,
    'PASSWD_NOTREQD':0x20,
    'PASSWD_CANT_CHANGE':0x40,
    'ENCRYPTED_TEXT_PASSWORD_ALLOWED':0x80,
    'TEMP_DUPLICATE_ACCOUNT':0x100,
    'NORMAL_ACCOUNT':0x200,
    'INTERDOMAIN_TRUST_ACCOUNT':0x800,
    'WORKSTATION_TRUST_ACCOUNT':0x1000,
    'SERVER_TRUST_ACCOUNT':0x2000,
    'DONT_EXPIRE_PASSWD':0x10000,
    'MNS_LOGON_ACCOUNT':0x20000,
    'SMARTCARD_REQUIRED':0x40000,
    'TRUSTED_FOR_DELEGATION':0x80000,
    'NOT_DELEGATED':0x100000,
    'USE_DES_KEY_ONLY':0x200000,
    'DONT_REQUIRE_PREAUTH':0x400000,
    'PASSWORD_EXPIRED':0x800000,
    'TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION':0x1000000}

    TYPE_MAPPPINGS = {
    "Person":"user",
    "Organizational-Unit":"organizationalUnit",
    "Domain-DNS":"domain"}

    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super().__init__(identifier, adsi_com_object, options)
        self.__distinguished_name = self.get('distinguishedName')
        self.__object_guid = self.get('objectGUID')
        self._gc_obj = None
        self._type=None
        if self.__object_guid is not None:
            self.__object_guid = self._convert_guid(self.__object_guid)
        # Set ADObject Type
        occn = self.get('objectCategory')
        if occn:
            # pull out CN from DN
            object_category_cn = occn.split('=',1)[1].split(",",1)[0]
            # some object categories are not very human readable
            # so we provide the option to override
            if object_category_cn in ADObject.TYPE_MAPPPINGS:
                self._type = ADObject.TYPE_MAPPPINGS[object_category_cn]
            else:
                self._type = object_category_cn.lower()
        else:
            # Sometimes you don't have access to objectCategory attribute,
            # try, with objectClass attribute
            objClass = self.get_attribute('objectClass',True)
            if 'domain' in objClass:
                self._type = 'domain'
            elif 'user' in objClass:
                self._type = 'user'
            elif 'organizationalUnit' in objClass:
                self._type = 'organizationalUnit'
            else:
                self._type = 'unknown'
        if self._type in list(self._py_ad_object_mappings.keys()):
            self.__class__ = self._py_ad_object_mappings[self._type]

    def _schema(self):
        return NTSchema(self.__class__.__name__, adsi_com_object=self._scheme_obj)

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
        self.update(key, item)

    def __getitem__(self, key):
        try:
            return self.get(key)
        except:
            raise InvalidAttribute(self.dn, key)

    def __delitem__(self, key):
        if self.has_key(key):
            self.delete(key)

    def has_key(self, key):
        return hasattr(self._adsi_obj, key)

    def keys(self):
        return self.get_attributes()

    def values(self):
        for attr in self.keys():
            yield attr, self.__getitem__(attr)
    ############################################
    #   Global Catalog Interface
    ############################################
    def _init_global_catalog(self, force=False, options={}):
        if 'protocol' in options:
            del options['protocol']
        if not self._gc_obj or force:
            self._gc_obj = GlobalCatalogObject(self.dn)

    def attribute_from_catalog(self, attribute):
        self._init_global_catalog()
        return self._gc_obj.get(attribute)
    ############################################
    #   Start LDAP Specific Functions
    ############################################
    def __get_parent_container(self):
        return ADObject(self.parent_container_path, options = self._make_options() )

    def __get_prefixed_cn(self):
        prefix=None
        if self.type == 'organizationalUnit':
            prefix = 'ou'
        elif self.type == "domain":
            prefix = 'dc'
        else:
            prefix = 'cn'
        return '='.join((prefix, self.get_attribute(prefix, False)))

    def __get_object_sid(self):
        sid = self.get('objectSid')
        return SID(bytes(sid)) if sid else None

    def _convert_guid(self, guid):
        return IID(guid, True)

    def get_UAC_settings(self):
        # Returns a dictionary of settings stored within UserAccountControl.
        # Expected keys for the dictionary are the same as keys in the ADS_USER_FLAG dictionary.
        # Further information on these values can be found at
        # http://msdn.microsoft.com/en-us/library/aa772300.aspx.
        d={}
        uac = self.get('UserAccountControl')
        for key, value in ADObject.ADS_USER_FLAG.values():
            d[key] = uac & value == value
        return d

    def set_UAC_settings(self, userFlag, newValue):
        # Sets a single setting in UserAccountControl.
        # UserFlag must be a value from ADS_USER_FLAG dictionary keys.
        # More information can be found at http://msdn.microsoft.com/en-us/library/aa772300.aspx.
        # newValue accepts boolean values
        if userFlag not in list(ADObject.ADS_USER_FLAG.keys()):
            raise InvalidValue("userFlag",userFlag,list(ADObject.ADS_USER_FLAG.keys()))
        elif newValue not in (True, False):
            raise InvalidValue("newValue",newValue,[True,False])
        else:
            # retreive the userAccountControl as if it didn't have the flag in question set.
            if self.get_attribute('userAccountControl',False) & ADObject.ADS_USER_FLAG[userFlag]:
                nv = self.get_attribute('userAccountControl',False) ^ ADObject.ADS_USER_FLAG[userFlag]
            else:
                nv = self.get_attribute('userAccountControl',False)
            # if the flag is true, then the value is present and
            # we add it to the starting point with B-OR.
            # Otherwise, if it's false, it's just not present,
            # so we leave it without any mention of the flag as in previous step.
            if newValue:
                nv = nv | ADObject.ADS_USER_FLAG[userFlag]
            self.update_attribute('userAccountControl',nv)

    def disable(self):
        try:
            if self.get('AccountDisabled') == False:
                self.set('AccountDisabled', True)
        except:
            raise Exception("Cannot Disable this object!")

    def enable(self):
        try:
            if self.get('AccountDisabled') == True:
                self.set('AccountDisabled', False)
        except:
            raise Exception("Cannot enable this object!")

    def _get_password_last_set(self):
        return self._convert_datetime(self.get('pwdLastSet'))

    def get_last_login(self):
        return self._convert_datetime(self.get('lastLogonTimestamp'))

    def get_uSNChanged(self):
        return self._convert_bigint(self.get('uSNChanged'))

    def move(self, new_ou_object):
        # Moves the object to a new organizationalUnit.
        # new_ou_object expects a ADContainer object where the current object will be moved to.
        try:
            new_path = self.default_protocol + '://' + self.dn
            new_ou_object.MoveHere(self, self.prefixed_cn)
            new_ou_object._flush()
        except:
            raise Exception("new_ou_obj is required to be LDAPContainer")
        new_dn = ','.join((self.prefixed_cn, new_ou_object.dn))
        time.sleep(.5)
        self._ads_path = self._generate_adsi_path(new_dn)
        self._set_adsi_obj()
        self.__distinguished_name = self.get_attribute('distinguishedName', False)
        self._init_global_catalog(True)

    def rename(self, new_name, set_sAMAccountName=True):
        """Renames the current object within its current organizationalUnit.
        new_name expects the new name of the object (just CN not prefixed CN or distinguishedName)."""
        parent = self.parent_container
        if self.type == 'organizationalUnit':
            pcn = 'ou='
        else:
            pcn = 'cn='
        pcn += new_name
        try:
            if self.type in ('user', 'computer', 'group') and set_sAMAccountName:
                self._adsi_obj.Put('sAMAccountName', new_name)
            new_path = self.default_protocol+'://' + self.dn
            parent.MoveHere(new_path, pcn)
            parent._flush()
        except:
            raise Exception("Failed to rename Object %s"%self)
        new_dn = ','.join((pcn, parent.dn))
        time.sleep(.5)
        self.__ads_path = self._generate_ads_path(new_dn)
        self.__set_adsi_obj()
        self.__distinguishedName = self.get('distinguishedName')
        self._init_global_catalog(True)

    def delete(self):
        """Deletes the object from the domain"""
        parent = self.parent_container
        if not parent:
            raise Exception("Object does not have a parent container. Cannot be deleted")
        else:
            parent.remove_child(self)

    def save(self):
        for attr in self.get_attributes():
            if self.get(attr) != getattr(self, attr):
                self.update(attr, getattr(self, attr))
        self._flush()

    ############################################
    #   LDAP Specific Properties
    ############################################
    dn = property(fget=lambda self: self.__distinguished_name,
                    doc="Distinguished Name (DN) of the object")
    prefixed_cn = property(fget=__get_prefixed_cn,
                    doc="Prefixed CN (such as 'cn=mycomputer' or 'ou=mycontainer' of the object")
    guid = property(fget=lambda self: self.__object_guid,
                    doc="Object GUID of the object")
    adsPath = property(fget=lambda self: self.__ads_path,
                    doc="ADsPath of Active Directory object (such as 'LDAP://cn=me,...,dc=com'")
    type = property(fget=lambda self: self._type,
                    doc="pyAD object type (user, computer, group, organizationalUnit, domain).")
    parent_container_path = property(fget=lambda self: ','.join(self.dn.split(',',1)[1:]),
                    doc="Returns the DN of the object's parent container.")
    guid_str = property(fget=lambda self: str(self.guid)[1:-1],
                    doc="Object GUID of the object")
    sid = property(fget=__get_object_sid,
                    doc='Get the SID of the Active Directory object')
    parent_container = property(__get_parent_container, doc="Object representing the container in which this object lives")

    @classmethod
    def set_ADObj(cls, obj):
        o = ADObject(adsi_com_object=obj)
        fingerprint = set( o.get_attributes() )
        for c,k in cls._obj_map.items():
            if k._attributes:
                if not fingerprint ^ k._attributes:
                    o.__class__ = k
        return o

##################################################
#   Object to interface with GlobalCatalogObject #
##################################################
class GlobalCatalogObject(LDAPBaseObject):
    default_protocol='GC'
    def __init__(self, identifier=None, adsi_com_object=None, options={}):
        super().__init__(identifier, adsi_com_object, options)

    def _schema(self):
        raise NotImplementedError()

    def _valid_protocol(self, protocol):
        if not protocol.isupper():
            protocol = protocol.upper()
        return protocol == 'GC'

##################################################
#   AD Based Interfaces
##################################################
class I_ADContainer(ADObject):
    def _copy_here(self, obj_path, new_name=None):
        self._adsi_obj.CopyHere(obj_path, new_name)
    def _create(self, class_type, name):
        return self._adsi_obj.Create(class_type, name)
    def _delete(self, class_type, name):
        self._adsi_obj.Delete(class_type, name)
    def _get_object(self, class_type, name):
        return self._adsi_obj.GetObject(class_type, name)
    def _move_here(self, source, new_name=None):
        self._adsi_obj.MoveHere(source, new_name)
    def move_here(self, source, new_name=None):
        self._move_here(source.dn, new_name)
    def get_children(self, recursive=False, filter_=None):
        for obj in self:
            if obj.type == 'organizationalUnit' and recursive:
                for child in obj.get_children(recursive=recursive, filter_=filter_):
                    yield child
            if not filter_ or obj.__class__ in filter_:
                yield obj
    def __iter__(self):
        for obj in self._adsi_obj:
            yield ADObject(adsi_com_object=obj)

##################################################
#   AD Objects
##################################################
class ADSchema(I_ADContainer):
    _class='Schema'
    def __init__(self, schema_class, identifier=None, adsi_com_object=None, options={}):
        super(NTObject, self).__init__(identifier, adsi_com_object, options)
        self._schema_class=schema_class
    def __iter__(self):
        return super().__iter__(self)
    def _init_schema(self):
        if self._scheme_obj is None:
            self._scheme_obj = self._adsi_obj
    def __repr__(self):
        return "< %(class)s for Class: %(name)s >"%{'class':self.__class__.__name__, 'name':self._schema_class}

class ADDomain(I_ADContainer):
    _class='Domain'
    _attributes=set(['dc',])
    def get_default_upn(self):
        # Returns the default userPrincipalName for the domain.
        self._adsi_obj.GetInfoEx(["canonicalName",],0)
        return self._adsi_obj.get("canonicalName").rstrip('/')

class ADOrganizationalUnit(I_ADContainer):
    _class='OrganizationalUnit'
    _attributes=set(['uPNSuffixes', 'searchGuide', 'defaultGroup'])

ADOU = ADOrganizationalUnit

class ADComputer(ADObject):
    _class='Computer'
    _attributes=set(['msTSEndpointType', 'operatingSystemVersion','msDS-isGC','promoExpiration','dNSHostName','msTSSecondaryDesktopBL',\
                'policyReplicationFlags','msDS-ExecuteScriptPassword','ipHostNumber','msTPM-TpmInformationForComputer','nisMapName',\
                'msDS-isRODC','monitoringMailUpdateUnits','siteGUID','msTSEndpointPlugin','netbootSIFFile','machineRole',\
                'physicalLocationObject','msDS-KrbTgtLink','operatingSystemServicePack','msSFU30Aliases','msDS-NeverRevealGroup',\
                'monitoringCachedViaRPC','enatelKeysData','monitoredServices','msDS-IsUserCachableAtRodc','msDS-PromotionSettings',\
                'msExchExchangeServerLink','msDS-GenerationId','monitoredConfigurations','msDS-SiteName','msDS-RevealedUsers',\
                'msImaging-ThumbprintHash','operatingSystemHotfix','monitoringAvailabilityWindow','operatingSystem','monitoringCachedViaMail',\
                'monitoringMailUpdateInterval','msTSPrimaryDesktopBL','netbootInitialization','volumeCount','msTPM-OwnerInformation',\
                'localPolicyFlags','catalogs','msImaging-HashAlgorithm','trackingLogPathName','netbootGUID','msDS-AdditionalDnsHostName',\
                'netbootDUID','msTSEndpointData','msDS-RevealOnDemandGroup','msDS-HostServiceAccount','msDS-AdditionalSamAccountName',\
                'monitoringAvailabilityStyle' ,'logRolloverInterval' ,'msDS-RevealedList','netbootMachineFilePath' ,'monitoringRPCUpdateUnits',\
                'rIDSetReferences' ,'monitoringRPCUpdateInterval' ,'netbootMirrorDataFile'])

class ADUser(ADObject, I_User):
    _class='User'
    #_attributes=

class ADGroup(ADObject, I_Group):
    _class='Group'
    #_attributes=
