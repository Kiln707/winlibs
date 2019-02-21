from winlibs.NTObjects import NTUser

user = NTUser('sswanson', options={'server':'solano.cc.ca.us'})
print(user.get('name'))
