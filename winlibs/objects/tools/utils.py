def generate_ads_path(distinguished_name, type_, server=None, port=None):
    #Generates a proper ADsPath to be used when connecting to an active directory object or when searching active directory.
    #
    #Keyword arguments:
    # - distinguished_name: DN of object or search base such as 'cn=zakir,ou=users,dc=mycompany,dc=com' (required).
    # - type: 'GC' (global-catalog) or 'LDAP' to determine what directory to be searched (required).
    # - server: FQDN of domain controller if necessary to connect to a particular server (optional unless port is defined).
    # - port: port number for directory service if not default port. If port is specified, server must be specified (optional).

    if type_ == "LDAP"  or type_ == "LDAPS":
        server = server if server else ADBase.default_ldap_server
        port = port if port else ADBase.default_ldap_port
    elif type_ == "GC":
        server = server if server else ADBase.default_gc_server
        port = port if port else ADBase.default_gc_port
    else:
        raise Exception("Invalid type specified.")

    ads_path = ''.join((type_,'://'))
    if server:
        ads_path = ''.join((ads_path,server))
        if port:
            ads_path = ':'.join((ads_path,str(port)))
        ads_path = ''.join((ads_path,'/'))
    ads_path = ''.join((ads_path,escape_path(distinguished_name)))
return ads_path

def generate_nt_path(distinguished_name, class_, server=None, port=None):

    nt_path = "WinNT://"
    if server:
        nt_path = ''.join((nt_path,server))
        if port:
            nt_path = ':'.join((nt_path,str(port)))
        nt_path = ''.join((ads_path,'/'))
    else:

    ads_path = ''.join((ads_path,escape_path(distinguished_name)))
