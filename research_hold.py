from winlibs.adsi.NTObjects import *
from winlibs.adsi.Base import ADSIBaseObject

computer = NTComputer('sswanson')
user = NTUser('sswanson')
group = NTGroup('Administrators', options={'server':None})
domain=NTDomain(options={'server':'NTNET'})
service = NTService('Spooler', options={'server':None})

ishtar = domain.get_computer('ISHTAR')

for obj in domain:
     # print(obj.Name)
#     #ntobj = NTObject(adsi_com_object=obj)
#     #ntobj = NTObject.get_object(obj)
#     # print(obj.Name)
    print(obj)
