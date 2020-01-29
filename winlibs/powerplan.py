
import win32com.client


class PowerPlan(Computer):

    def __init__(self, mk="//./root/cimv2/power"):
        super(PowerPlan, self).__init__(mk)
        self.power_info = None
        self.power_plan = None

    def get_active_power_plan(self) -> str:

        power_plans = self.wmi.InstancesOf("Win32_powerplan")

        for plan in power_plans:
            if plan.IsActive:
                match = re.search(r'\{(.+?)\}', plan.InstanceID)
                self.power_plan = plan
                return match.group(1)

    def get_power_plan_index(self, guid_id):

        unknown_list = []
        current_power_plan_index = {"AC": {}, "DC": {}}
        power_index = self.wmi.InstancesOf("Win32_powersettingdataindex")
        for power_value in power_index:
            # print(type(power_value))
            # print(dir(power_value))
            match = re.search(guid_id, power_value.InstanceID)
            if match is not None:
                match = re.search(guid_id + r'\}\\(\w{2})\\\{(.+?)\}', power_value.InstanceID)
                power_mode = match.group(1)
                power_tag = match.group(2)
                try:
                    power_word = PowerPlanGUID(power_tag).name
                except Exception as Err:
                    # print("Unknown Tag GUID: " + power_tag)

                    if power_tag not in unknown_list:
                        unknown_list.append(power_tag)
                    continue

                # power_info = {power_word : power_value.settingindexvalue}

                current_power_plan_index[power_mode][power_word] = power_value.settingindexvalue
        self.power_info = current_power_plan_index
        self._json_dump(self.power_info)

    def set_power_plan_value(self, act_plan_guid, power_mode, power_plan_value_guid, value):
        power_index = self.wmi.InstancesOf("Win32_powersettingdataindex")

        for power_setting in power_index:
            match = re.search(act_plan_guid + r'\}\\' + power_mode + r'\\\{' + power_plan_value_guid + r'\}',
                              power_setting.InstanceID)
            # match = re.search(power_plan_value_guid, power_setting.InstanceID)
            if match is not None:
                print(power_setting.InstanceID)
                print(power_setting.settingindexvalue)
                # Properties_
                power_setting.Properties_("SettingIndexValue").Value = value
                # How to make the changed value work
                power_setting.Put_()
                act_method = self.power_plan.Methods_("Activate")
                self.power_plan.ExecMethod_("Activate")

            else:
                pass
