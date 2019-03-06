from winlibs.poweroptions import PowerCFG


p = PowerCFG()
a=0
for s in p.list():
    for i in s.settings():
        pass
#        print(i._GUID, i._name)
    break

from pyad import pyad

from winlibs.adsi.LDAPObjects import *
from winlibs.adsi.NTObjects import *

u = LDAPBaseObject('CN=John Doe,OU=Accounts,DC=solano,DC=cc,DC=ca,DC=us')


print(u.get('distinguishedName'))

print(u)
