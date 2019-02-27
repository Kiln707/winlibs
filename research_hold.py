from winlibs.adsi.NTObjects import *
from winlibs.adsi.Base import ADSIBaseObject

computer = NTComputer('sswanson')
user = NTUser('sswanson')
group = NTGroup('Administrators', options={'server':None})
domain=NTDomain(options={'server':'NTNET'})
service = NTService('Spooler', options={'server':None})

# for obj in computer:
for obj in domain:
    # print(obj.Name)
    #ntobj = NTObject(adsi_com_object=obj)
    #ntobj = NTObject.get_object(obj)
    print(obj.Name)
    print(obj)

    # if obj._class == 'Service':
    #     for o in obj.get_attributes():
    #         print(o, getattr(obj, o))
    #     break
    # print(ntobj.get_attributes())
