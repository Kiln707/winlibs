from User import WinUser
#from ADQuery import query

user = WinUser('jdoe', 'solano.cc.ca.us')


print(user.name)
print(user._full_name)
print(user.comment)
#user.full_name = 'yo yo'
print(user.SID)
print(user.last_logon)
print(user.password_is_expired)

user.map_attribute_property('full_name', 'name')
user.map_attribute_property('full_name', 'cn')
user.map_attribute_property('full_name', 'displayName')

print(user.get_attribute_property_map())
