#from winlibs.poweroptions import PowerConfig
# p = PowerConfig()
# a=0
# for s in p.list():
#     #print(s._GUID, s._name)
#     for i in s.subgroup():
#         print(i._GUID, i._name)
#         #break
#     break

#exit(0)
from pyad import pyad

from winlibs.internals.adsi.ADObjects import *
from winlibs.internals.adsi.NTObjects import *

domain = ADDomain(identifier="DC=solano,DC=cc,DC=ca,DC=us")
group = ADGroup(identifier="CN=VJOCTR,OU=Security Groups,DC=solano,DC=cc,DC=ca,DC=us")
user = ADUser(identifier="CN=Steven Swanson,OU=Accounts,DC=solano,DC=cc,DC=ca,DC=us")
computer = ADComputer(identifier="CN=sswanson,OU=NoUpdate,DC=solano,DC=cc,DC=ca,DC=us")
ou = ADOrganizationalUnit(identifier="OU=Security Groups,DC=solano,DC=cc,DC=ca,DC=us")
container = ADObject(identifier="CN=Users,DC=solano,DC=cc,DC=ca,DC=us")
obj = ADSchema(identifier="CN=Schema,CN=Configuration,DC=solano,DC=cc,DC=ca,DC=us")


for o in domain.get_children(recursive=True):
    if not o._objectCategory:
        print(o.get('objectCategory'))
