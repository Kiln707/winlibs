from .wmic import WMIRoot

class OperatingSystem(WMIRoot):
     def __init__(self, host='localhost', username='', password='', find_classes=False):
         super().__init__(self, host=host, username=username, password=password, find_classes=find_classes)
         self.bootDevice = ''
         self.buildNumber = ''
         self.buildType = ''
         self.caption = ''
         self.codeSet = ''
         self.countryCode = ''
         self.creationClassName = ''
         self.csCreationClassName = ''
         self.csdVersion = ''
         self.csdVersion = ''

    def _setInformation(self):
        pass

    def reboot(self):
        pass

    def setDateTime(self):
        pass

    def shutdown(self):
        pass
