from winlibs.adsi.NTObjects import *
from winlibs.adsi.Base import ADSIBaseObject

computer = NTComputer('sswanson')
user = NTUser('sswanson')
for i in computer:
    j = ADSIBaseObject(adsi_com_object=i)
    for m in dir(user):
        if m not in dir(j):
            print(m)
    break
