from winlibs.poweroptions import PowerCFG


p = PowerCFG()
a=0
for s in p.list():
    for i in s.settings():
        print(i._GUID, i._name)
    break
