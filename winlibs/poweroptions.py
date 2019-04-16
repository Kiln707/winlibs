import subprocess

class PowerObj():
    _cmd='powercfg'
    def __init__(self, guid, name):
        self._GUID=guid
        self._name=name

    @staticmethod
    def _run(cmd):
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stderr:
            raise Exception(result.stderr)
        return result.stdout.decode('UTF-8')

    @classmethod
    def query(cls, GUID=None):
        if GUID:
            cmd = ' '.join([cls._cmd,'/QUERY', GUID])
        else:
            cmd = ' '.join([cls._cmd,'/QUERY'])
        return cls._run(cmd)

class PowerConfig(PowerObj):
    def __init__(self):
        super().__init__(0, 'Power Configuration')

    @classmethod
    def from_str(cls, cfg_str):
        print(cfg_str)
        #for line in cfg_str:
        #    print(line)


    def list(self):
        results = self._run(' '.join([self._cmd, '/L']))
        for line in results:
            if 'Power Scheme GUID:' in line:
                s = line.split(' ')
                yield PowerScheme(s[3], s[5].strip('()'))

class PowerScheme(PowerObj):
    def __init__(self, guid, name):
        super().__init__(guid, name)

    def settings(self):
        for setting in self._query():
            if 'Power Setting' in setting and 'GUID' in setting:
                s = setting.split(' ')
                yield PowerSetting(s[7], ' '.join(s[9:]).strip('(),\''))

    def subgroup(self):
        for setting in self._query():
            if 'Subgroup' in setting:
                s = setting.split(' ')
                yield PowerSubgroup(s[4],s[6].strip('()'))

class PowerSubgroup(PowerObj):
    def __init__(self, guid, name):
        super().__init__(guid, name)

    def settings(self):
        for setting in self._query():
            if 'Power Setting' in setting:
                yield PowerSetting(s[3],s[5].strip('()'))

class PowerSetting(PowerObj):
    def __init__(self, guid, name):
        super().__init__(guid, name)
