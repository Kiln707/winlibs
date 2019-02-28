from winlibs.adsi.NTObjects import *
from winlibs.adsi.Base import ADSIBaseObject

computer = NTComputer('sswanson')
user = NTUser('sswanson')
group = NTGroup('Administrators', options={'server':None})
domain=NTDomain(options={'server':'NTNET'})
service = NTService('Spooler', options={'server':None})



# ishtar = NTComputer('ishtar')

ishtar = NTFileService(computer='ISHTAR')
print('sessions:')
for a in ishtar.resources():
    print(a, a.get_attributes())



# print('Members:')
# for b in ishtar:
#     print(b)

# printer = ishtar.get_object('PrintQueue', 'Adobe PDF'))
# print(printer.get_attributes())


# for obj in domain:
#      # print(obj.Name)
# #     #ntobj = NTObject(adsi_com_object=obj)
# #     #ntobj = NTObject.get_object(obj)
# #     # print(obj.Name)
#     print(obj)
