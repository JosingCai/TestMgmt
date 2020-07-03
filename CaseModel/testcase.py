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
from AutoModel.apicase import runTargetAPI
from CaseModel.excel import Excel
from django.conf import settings

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
        # print(status, output)
        return status, output

    def modify_case(self, sheet_name, **request_info):
        Keys = list(request_info.keys())
        case_info = []
        for Key in Keys:
            case_info.append(request_info[Key].strip())
        status, output = self.handle.modify_excel_row(sheet_name, case_info[1:])
        # print(status, output)
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
    xmind_file = 'docs/xmind_testcase_template.xmind'
    print('Start to convert XMind file: %s' % xmind_file)
    if case_type == "testcase_json":
        testcase_json_file = xmind_testcase_to_json_file(xmind_file)
        print('Convert XMind file to testcase json file successfully: %s' % testcase_json_file)
    elif case_type == "zentao_csv":
        zentao_csv_file = xmind_to_zentao_csv_file(xmind_file)
        print('Convert XMind file to zentao csv file successfully: %s' % zentao_csv_file)
    elif case_type == "testlink_xml":
        testlink_xml_file = xmind_to_testlink_xml_file(xmind_file)
        print('Convert XMind file to testlink xml file successfully: %s' % testlink_xml_file)
    elif case_type == "testsuite_json":
        testsuite_json_file = xmind_testsuite_to_json_file(xmind_file)
        print('Convert XMind file to testsuite json file successfully: %s' % testsuite_json_file)
    elif case_type == "testsuites":
        testsuites = get_xmind_testsuite_list(xmind_file)
        print('Convert XMind to testsuits dict data:\n%s' % json.dumps(testsuites, indent=2, separators=(',', ': '), ensure_ascii=False))
    elif case_type == "testcases":
        testcases = get_xmind_testcase_list(xmind_file)
        print('Convert Xmind to testcases dict data:\n%s' % json.dumps(testcases, indent=4, separators=(',', ': ')))
    elif case_type == "json":
        workbook = xmind.load(xmind_file)
        print('Convert XMind to Json data:\n%s' % json.dumps(workbook.getData(), indent=2, separators=(',', ': '), ensure_ascii=False))

    print('Finished conversion, Congratulations!')
        
