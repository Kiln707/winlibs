from builtins import object
import sys, socket

if sys.platform != 'win32':
    raise Exception("Must be running Windows in order to use WinLibs!")

try:
    import win32api
    import pywintypes
    import win32com.client
except ImportError:
    raise Exception("pywin32 library required. Download from https://pypi.org/project/pywin32/")

_provider = win32com.client.Dispatch("ADsNameSpace")

try:
    # Discover default domain and forest information
    __default_domain_obj = _adsi_provider.GetObject('', "LDAP://rootDSE")
except:
    # If there was an error, this this computer might not be on a domain.
    print("WARN: unable to connect to default domain. Computer is likely not attached to an AD domain")
    __default_domain_obj = None
    _default_detected_forest = None
    _default_detected_domain = None
else:
    # connecting to rootDSE will connect to the domain that the
    # current logged-in user belongs to.. which is generally the
    # domain under question and therefore becomes the default domain.
    _default_detected_forest = __default_domain_obj.Get("rootDomainNamingContext")
    _default_detected_domain = __default_domain_obj.Get("defaultNamingContext")

class adsi_base(object):
    default_ssl = False
    default_ldap_server=None
    default_gc_server=None
    default_winnt_server=None
    default_ldap_port=None
    default_gc_port=None
    default_winnt_port=None
    default_username=None
    default_password=None
    default_ldap_protocol='LDAP'
    default_ldap_authentication_flag=0 #No Credentials
    default_domain= _default_detected_domain
    default_forest = _default_detected_forest
