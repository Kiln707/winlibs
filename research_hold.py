from winlibs.poweroptions import PowerCFG


p = PowerCFG()
a=0
for s in p.list():
    #print(s._GUID, s._name)
    for i in s.settings():
        pass
        print(i._GUID, i._name)
        #break
    break

exit(0)
from pyad import pyad

from winlibs.adsi.LDAPObjects import *
from winlibs.adsi.NTObjects import *

u = ADObject('CN=John Doe,OU=Accounts,DC=solano,DC=cc,DC=ca,DC=us')

#print(u.get('distinguishedName'))

#print(u)
