from winlibs.adsi.NTObjects import NTUser, NTComputer

user = NTUser('sswanson')
print(user.FullName)

computer = NTComputer('sswanson')
for a in computer.get_attributes():
    print(a, getattr(computer, a))
