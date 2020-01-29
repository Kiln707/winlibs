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

from winlibs.adsi.LDAPObjects import *
from winlibs.adsi.NTObjects import *

domain = ADDomain(identifier="DC=solano,DC=cc,DC=ca,DC=us")
group = ADGroup(identifier="CN=VJOCTR,OU=Security Groups,DC=solano,DC=cc,DC=ca,DC=us")
user = ADUser(identifier="CN=Steven Swanson,OU=Accounts,DC=solano,DC=cc,DC=ca,DC=us")
computer = ADComputer(identifier="CN=sswanson,OU=NoUpdate,DC=solano,DC=cc,DC=ca,DC=us")
ou = ADOrganizationalUnit(identifier="OU=Security Groups,DC=solano,DC=cc,DC=ca,DC=us")
domain_attrs = domain.get_mandatory_attributes()
user_attrs = user.get_mandatory_attributes()
group_attrs = group.get_mandatory_attributes()
computer_attrs = computer.get_mandatory_attributes()
ou_attrs = ou.get_mandatory_attributes()

# attribs = []
# for attr in domain.get_mandatory_attributes():
#     if attr not in user_attrs and attr not in group_attrs and attr not in ou_attrs and attr not in computer_attrs:
#         attribs.append(attr)
#
# print("','".join(attribs))

for attr in user_attrs:
    print(attr, user.get(attr))
for attr in computer_attrs:
    print(attr, computer.get(attr))
