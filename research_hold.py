import wmi

c = wmi.WMI()
print(dir(c))
for s in c.Win32_Service():
    print(s)

exit(0)
from pyad import pyad

from winlibs.adsi.LDAPObjects import *
from winlibs.adsi.NTObjects import *

u = ADObject('CN=John Doe,OU=Accounts,DC=solano,DC=cc,DC=ca,DC=us')

#print(u.get('distinguishedName'))

#print(u)
