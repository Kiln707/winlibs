from wmi import WMI

class WMIRoot():
    _Namespace=None

    def __init__(self, host='localhost', username='', password=''):
        self.wmi
        if host == 'localhost':
            self.wmi = WMI()
        else:
            self.wmi = WMI(host)
