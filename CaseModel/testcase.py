# testcase.py
import datetime
import os
import json
import xmind
from xmind2testcase.zentao import xmind_to_zentao_csv_file
from xmind2testcase.testlink import xmind_to_testlink_xml_file
from xmind2testcase.utils import xmind_testcase_to_json_file
from xmind2testcase.utils import xmind_testsuite_to_json_file
from xmind2testcase.utils import get_xmind_testcase_list
from xmind2testcase.utils import get_xmind_testsuite_list
# from AutoModel.apicase import runTargetAPI
# from CaseModel.excel import Excel
# from django.conf import settings
import logging
from CaseModel.testcase import TestCase as t_TestCase
from CaseModel.models import TestCase as m_TestCase


logger = logging.getLogger(__name__) 

class TestCase(object):
    def __init__(self, project, file_name="default", operate="import"):
        self.project = project
        # Keys = test_report_def.keys()
        count = 0
        if operate == "export":
            cur_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            file_name_tmp = "%s_%s.xls" %(project, cur_time)
            self.test_case_file_name = os.path.join(settings.MEDIA_ROOT,file_name_tmp) 
        else:
            self.test_case_file_name = file_name
        self.handle = Excel(self.test_case_file_name)

    def write_sheet_info(self,sheet_name, *infos):
        self.handle.write_case(sheet_name, *infos)
        self.handle.write_case_count(sheet_name, *infos)
        return True

    def write_issue_info(self,sheet_name, *infos):
        self.handle.write_issue(sheet_name, *infos)
        return True

    def write_testplan_info(self,sheet_name, *infos):
        self.handle.write_testplan(sheet_name, *infos)
        return True

    def write_sumup_info(self):
        self.handle.write_sumup(self.project)
        return True

    def get_file_name(self):
        return self.test_case_file_name

    def get_sheet_names(self):
        sheet_names = self.handle.read_sheet_names()
        index = list(range(len(sheet_names)))
        index_list = []
        for i in index:
            index_dict = {}
            index_dict["index"] = i
            index_dict["name"] = sheet_names[i]
            index_list.append(index_dict)
        return index_list

    def get_sheet_content(self, sheet_name):
        contents = self.handle.read_sheet_content(sheet_name)
        return contents

    def delete_case(self, sheet_name, **request_info):
        case_num = list(request_info.keys())[0]
        status, output = self.handle.delete_excel_row(sheet_name, case_num)
        return status, output

    def modify_case(self, sheet_name, **request_info):
        Keys = list(request_info.keys())
        case_info = []
        for Key in Keys:
            case_info.append(request_info[Key].strip())
        status, output = self.handle.modify_excel_row(sheet_name, case_info[1:])
        return status, output

    def add_case(self, sheet_name, **request_info):
        # case_type_def = {"base_fun": "基本功能测试", "scene": "场景测试", "abnormal": "异常测试", "longtime": "长时间测试", "pressure": "压力测试", "ui_interactive": "UI交互测试", "security": "安全测试"}
        # case_level_def = {"level0": "Level0", "level1": "Level1", "level2": "Level2", "level3": "Level3", "level4": "Level4", "level5": "Level5"}
        # case_auto_test_def = {"yes": "是", "no": "否"}
        # case_test_reulst_def = {"untest": "未测试", "pass": "PASS", "fail": "FAIL", "un_merge": "未合入", "deprecated": "废弃"}

        # request_info["case_type"] = case_type_def[request_info["case_type"]]
        # request_info["priority"] = case_level_def[request_info["priority"]]
        # request_info["auto_test"] = case_auto_test_def[request_info["auto_test"]]
        # request_info["test_result"] = case_test_reulst_def[request_info["test_result"]]

        info_list = [request_info["case_number"].strip(), request_info["case_name"].strip(), request_info["case_type"], request_info["priority"],request_info["pre_condition"], request_info["test_range"], request_info["test_steps"],request_info["expect_result"],request_info["auto"],request_info["case_id"], request_info["fun_developer"], request_info["case_designer"], request_info["case_executor"],request_info["test_time"], request_info["test_result"], request_info["remark"]]

        status, output = self.handle.add_row_data(sheet_name, info_list)
        return status, output

    def split_case(self, sheet_name):
        status, output = self.handle.split_table(sheet_name)
        return status, output

    def run_case(self, sheet_name, **request_info):
        case_num = list(request_info.keys())[0]
        status, output = self.handle.get_case_info(sheet_name, case_num)
        if status:
            isAuto = output[8]
            autoAPI = output[9]
            if isAuto == '是' and len(autoAPI) != 0:
                status, output = runTargetAPI(self.project, autoAPI)
                self.handle.modify_case_status(sheet_name, case_num, status)
                return status, output
            else:
                return False, "%s Not Support Auto Test or Not Related API info, Please Check it " %(case_num)
        return status, output

    def read_all(self):
        index_list = self.get_sheet_names()
        caseinfo_list = []
        for info in index_list:
            retList = self.get_sheet_content(info['name'])
            for item in retList:
                caseinfo_dict = {}
                caseinfo_dict['module'] = info
                caseinfo_dict['project'] = self.project
                try:
                    caseinfo_dict['case_number'] = item[0]
                except:
                    continue
                    caseinfo_dict['case_number'] = ''

                try:
                    caseinfo_dict['case_name'] = item[1]
                except:
                    caseinfo_dict['case_name'] = ''

                try:
                    caseinfo_dict['case_type'] = item[2]
                except:
                    caseinfo_dict['case_type'] = ''

                try:
                    caseinfo_dict['priority'] = item[3]
                except:
                    caseinfo_dict['priority'] = ''

                try:
                    caseinfo_dict['pre_condition'] = item[4]
                except:
                    caseinfo_dict['pre_condition'] = ''

                try:
                    caseinfo_dict['test_range'] = item[5]
                except:
                    caseinfo_dict['test_range'] = ''

                try:
                    caseinfo_dict['test_steps'] = item[6]
                except:
                    caseinfo_dict['test_steps'] = ''

                try:
                    caseinfo_dict['expect_result'] = item[7]
                except:
                    caseinfo_dict['expect_result'] = ''

                try:
                    caseinfo_dict['auto'] = item[8]
                except:
                    caseinfo_dict['auto'] = ''

                try:
                    caseinfo_dict['api_related'] = item[9]
                except:
                    caseinfo_dict['api_related'] = ''

                try:
                    caseinfo_dict['fun_developer'] = item[10]
                except:
                    caseinfo_dict['fun_developer'] = ''

                try:
                    caseinfo_dict['case_designer'] = item[11]
                except:
                    caseinfo_dict['case_designer'] = ''

                try:
                    caseinfo_dict['case_executor'] = item[12]
                except:
                    caseinfo_dict['case_executor'] = ''

                try:
                    caseinfo_dict['test_time'] = datetime.datetime.strptime(item[13], "%Y-%m-%d %H:%M:%S")
                except:
                    caseinfo_dict['test_time'] = None

                try:
                    caseinfo_dict['test_result'] = item[14]
                except:
                    caseinfo_dict['test_result'] = ''
                try:
                    caseinfo_dict['remark'] = item[15]
                except:
                    caseinfo_dict['remark'] = ''
                caseinfo_list.append(caseinfo_dict)

        return caseinfo_list

    def issue_count(self):
        
        pass


def xmind(case_type="testcase_json"):
    case_type_define = ["json", "zentao_csv", "testlink_xml", "testsuite_json", "testsuites", "testcase_json", "testcases"]
    xmind_file = 'static/files/BOOT3X_V3.9.0_V2.19.0.xmind'
    logger.info('Start to convert XMind file: %s' % xmind_file)
    if case_type == "testcase_json":
        testcase_json_file = xmind_testcase_to_json_file(xmind_file)
        logger.info('Convert XMind file to testcase json file successfully: %s' % testcase_json_file)
    elif case_type == "zentao_csv":
        zentao_csv_file = xmind_to_zentao_csv_file(xmind_file)
        logger.info('Convert XMind file to zentao csv file successfully: %s' % zentao_csv_file)
    elif case_type == "testlink_xml":
        testlink_xml_file = xmind_to_testlink_xml_file(xmind_file)
        logger.info('Convert XMind file to testlink xml file successfully: %s' % testlink_xml_file)
    elif case_type == "testsuite_json":
        testsuite_json_file = xmind_testsuite_to_json_file(xmind_file)
        logger.info('Convert XMind file to testsuite json file successfully: %s' % testsuite_json_file)
    elif case_type == "testsuites":
        testsuites = get_xmind_testsuite_list(xmind_file)
        logger.info('Convert XMind to testsuits dict data:\n%s' % json.dumps(testsuites, indent=2, separators=(',', ': '), ensure_ascii=False))
    elif case_type == "testcases":
        testcases = get_xmind_testcase_list(xmind_file)
        logger.info('Convert Xmind to testcases dict data:\n%s' % json.dumps(testcases, indent=4, separators=(',', ': ')))
    elif case_type == "json":
        xmind_file = 'xmind_testcase_template.xmind'
        workbook = xmind.load(xmind_file)
        logger.info('Convert XMind to Json data:\n%s' % json.dumps(workbook.getData(), indent=2, separators=(',', ': '), ensure_ascii=False))

    logger.info('Finished conversion, Congratulations!')
    return True

def xmind_convert():
    # 用例执行类型
    execution_type = {1:"no", 2:"yes"}
    # 优先级
    importance = {1:"高",2:"中", 3:"低"}
    #用例状态
    case_status = {1:"草稿", 2:"待评审", 3:"评审中", 4:"重做", 5:"废弃", 6:"feature", 7:"终稿"}
    #case_number_def = {"Sum_Up": "概览", "Host_Apply": "主机交付", "IDC_Mgmt": "数据中心", "Device_Mgmt": "设备管理", "Hardware_Mgmt": "硬件管理", "InstallOS_Mgmt": "装机管理", "Image_Mgmt": "镜像管理", "OOB_Mgmt": "带外管理", "Task_Mgmt": "任务管理", "Proxy_Mgmt": "分布式管理", "Asset_Mgmt": "资产管理", "ACL_Mgmt": "安全审计", "Report_Mgmt": "报表管理", "User_Mgmt": "用户管理", "System_Mgmt": "系统管理", "Notice_Mgmt": "通知中心", "Env_Config": "环境配置与日志", "Auth_Mgmt": "权限管理-UAM", "Data_Sync": "数据对接", "新需求": "new_requirement"}
    case_number_def = {"global": "全局", "Task": "任务", "Alarm": "告警", "Audit": "审计", "OpenAPI": "扩展", "Report": "报表", "SumUp": "概览", "InstallOS": "装机", "Device": "设备", "Setting": "设置", "Assert": "资产", "NewRequirement": "新需求", "Other": "未分类"}
    test_result = {0:"未执行", 1:"PASS", 2:"FAIL", 3:"BLOCKED",4:"SKIPPED"}
    with open(file_name) as f:
        context = f.read()
        context = json.load(context)
    list_info = context[0]["sub_suites"]
    for module_dict in list_info:
        module_name = module_dict["name"]
        if "新需求" in module_name:
            items = module_name.split("-")
            module_name = items[0]
            version = items[1]
            module_key = "NewRequirement_%s"%version
        elif module_name in module_dict.values():
            module_key = list(case_number_def.keys())[list(case_number_def.values()).index(module_name)]
            module_key = "%s_3.0.0" %module_key
        else:
            module_key = "Other"
        for info in module_dict["testcase_list"]:
            count = 1
            case_number = "%s_%d" %(module_key, count)
            if info["importance"] == 1:
                case_type = "基本功能测试"
                priority = "Level0"
            elif info["importance"] == 2:
                case_type = "场景测试"
                priority = "Level1"
            elif info["importance"] == 3:
                case_type = "异常测试"
                priority = "Level2"
            else:
                case_type = "未知类型"
                priority = "Level3"
            auto = execution_type[info['auto']]
            result = test_result[info['result']]
            test_steps = ""
            expect_result = ""
            step_count = 1
            for step_dict in info["steps"]
                test_steps = test_steps + "%d: %s\n" %(step_count,step_dict["action"])
                expect_result = expect_result + "%d: %s\n" %(step_count, step_dict["expectedresults"])
                step_count = step_count + 1

            ret_old = list(m_TestCase.objects.filter(case_number=case_number).values())
            if len(ret_old) > 0:
                obj = m_TestCase.objects.filter(case_number=case_number).update(case_name=info['name'],case_type=case_type,priority=priority,pre_condition=info['preconditions'],test_range="",test_steps=test_steps,expect_result=expect_result,auto=auto, test_result=result,project_id=info['project'],module=module_name,remark="")
            else:
                obj = m_TestCase(case_number=case_number, case_name=info['name'],case_type=case_type,priority=priority,pre_condition=info['preconditions'],test_range="",test_steps=test_steps,expect_result=expect_result,auto=auto,case_id="", fun_developer="", case_designer="",case_executor="",test_time="", test_result=result,project_id=info['project'],module=module_name,remark="")
                obj.save() 

            count = count + 1 






if __name__ == '__main__':
    #xmind("testcase_json")
    xmind("testsuite_json")
    # xmind("testcases")

