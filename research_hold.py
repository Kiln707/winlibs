from winlibs.adsi.NTObjects import *
from winlibs.adsi.Base import ADSIBaseObject

computer = NTComputer('sswanson', options={'server':None})
user = NTUser('sswanson', options={'server':None})
for i in computer:
    j = ADSIBaseObject(adsi_com_object=i)
    for m in j.get_attributes():
        if m not in user.get_attributes():
            print(m)
    break
