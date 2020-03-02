from .wmic import WMIRoot

class OperatingSystemWMI(WMIRoot):
     def __init__(self, host='localhost', username='', password='', find_classes=False):
         super().__init__(self, host=host, username=username, password=password, find_classes=find_classes)
         
