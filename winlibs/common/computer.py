class Computer():

    def __init__(self, host='localhost', username='', password='', ):
        self.wmi = WMIRoot(host=host)
