from winlibs.adsi.NTObjects import *
from winlibs.adsi.Base import ADSIBaseObject

computer = NTComputer('sswanson', options={'server':None})
user = NTUser('sswanson')
group = NTGroup('Administrators', options={'server':None})
domain=NTDomain(options={'server':'NTNET'})
service = NTService('Spooler', options={'server':None})



# ishtar = NTComputer('ishtar')

# print('sessions:')
# for a in ishtar.resources():
#     print(a, a.Path)



# print('Members:')
# for b in ishtar:
#     print(b)

printer = computer.get_object('PrintQueue', 'Adobe PDF')
print(printer)
print(printer.get_attributes())


# for obj in domain:
#      # print(obj.Name)
# #     #ntobj = NTObject(adsi_com_object=obj)
# #     #ntobj = NTObject.get_object(obj)
# #     # print(obj.Name)
#     print(obj)
