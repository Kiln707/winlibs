from winlibs.adsi.NTObjects import *

user = NTUser('sswanson')
print(user.FullName)

service = NTFileService('Assessment', options={'server':'ISHTAR'})

print(service.get_attributes())
