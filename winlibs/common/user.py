from ..adsi import ADUser, NTUser

class User():
    def __init__(self):
        self.ad_account = None#ADUser
        self.local_account = None#NTUser
