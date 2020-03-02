import new
from wmi import WMI
from types import MethodType

class WMIRoot():
    _Namespace=''

    def __init__(self, host='localhost', username='', password='', namespace='', moniker='', privileges=[], find_classes=False):
        self.wmi = None
        if host == 'localhost':
            self.wmi = WMI(namespace=namespace, moniker=moniker, privileges=privileges, find_classes=find_classes)
        else:
            if username:
                self.wmi = WMI(host, user=username, password=password, namespace=namespace, moniker=moniker, privileges=privileges, find_classes=find_classes)
            else:
                self.wmi = WMI(host, namespace=namespace, moniker=moniker, privileges=privileges, find_classes=find_classes)

    def query(self, query):
        self.wmi.query(query)

    def __getattr__(self, aname):
        target = self.wmi
        f = getattr(target, aname)
        if isinstance(f, MethodType):
            # Rebind the method to the target.
            return new.instancemethod(f.im_func, self, target.__class__)
        else:
            return f
