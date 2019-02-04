from ADQuery import*
from User import *
from pyad import set_defaults

def init(ldap_server, username, password):
    pyad.set_defaults(ldap_server=ldap_server, username=username, password=password)
