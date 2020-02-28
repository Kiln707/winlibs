from wmi import WMI

class WMIRoot():
    _Namespace=None

    def __init__(self, host='localhost', username='', password=''):
        self.wmi = None
        if host == 'localhost':
            self.wmi = WMI()
        else:
            if username:
                self.wmi = WMI(host, user=username, password=password)
            else:
                self.wmi = WMI(host)
