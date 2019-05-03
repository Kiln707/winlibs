import subprocess

class PowerObj():
    _cmd='powercfg'
    def __init__(self, guid, name):
        self._GUID=guid
        if guid and not name:
            print(self.query())
        self._name=name

    def query(self):
        return self._query(GUID=self._GUID).split('\r\n')

    @staticmethod
    def _run(cmd):
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stderr:
            raise Exception(result.stderr)
        return result.stdout.decode('UTF-8')

    @classmethod
    def _query(cls, GUID=None):
        if GUID:
            cmd = ' '.join([cls._cmd,'/QUERY', GUID])
        else:
            cmd = ' '.join([cls._cmd,'/QUERY'])
        return cls._run(cmd)

class PowerConfig(PowerObj):
    def __init__(self):
        super().__init__(0, 'Power Configuration')

    def list(self):
        results = self._run(' '.join([self._cmd, '/L']))
        for line in results.split('\n'):
            if 'Power Scheme GUID:' in line:
                s = line.split(' ')
                yield PowerScheme(s[3], s[5].strip('()'))

class PowerScheme(PowerObj):
    def __init__(self, guid, name):
        super().__init__(guid, name)

    # def settings(self):
    #     for setting in self.query():
    #         if 'Power Setting' in setting and 'GUID' in setting:
    #             s = setting.split(' ')
    #             yield PowerSetting(s[7], ' '.join(s[9:]).strip('(),\''))

    def subgroup(self):
        for setting in self.query():
            if 'Subgroup' in setting:
                s = setting.split(' ')
                yield PowerSubgroup(s[4],s[6].strip('()'))

class PowerSubgroup(PowerObj):
    def __init__(self, guid, name):
        super().__init__(guid, name)

    def settings(self):
        for setting in self.query():
            print(setting)
            if 'Power Setting' in setting:
                yield PowerSetting(s[3],s[5].strip('()'))

class PowerSetting(PowerObj):
    def __init__(self, guid, name):
        super().__init__(guid, name)
