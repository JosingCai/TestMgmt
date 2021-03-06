#common.py

import  xml.dom.minidom
import xlwt
import xlrd
import os
import logging
from xlutils.copy import copy as xl_copy
from AutoModel.models import Dependency, Result, TestDetail
from AutoModel.report import pie_charts
from CaseModel.models import Issue_Milestone_Count

logger = logging.getLogger(__name__) 

class Excel(object):
    """docstring for Excel"""
    #formatting_info=True原样打开
    def __init__(self, file_name):
        self.file_name = file_name
        self.sum_up_sheet = "测试结果总览"

    def write_sumup(self, project): # *issue_infos, *api_infos
        if os.path.exists(self.file_name):
            wb = xlrd.open_workbook(self.file_name)
            excel = xl_copy(wb)
        else:
            excel = xlwt.Workbook(encoding='utf-8')
            sheet_sum_up = excel.add_sheet(self.sum_up_sheet)
            items_sum_up = ["模块名称", "用例总数", "未合入/未测试", "PASS数", "FAIL数", "PASS率", "备注"]
            for i in range(len(items_sum_up)):
                sheet_sum_up.write(0, i, items_sum_up[i])
        sheet_name = "汇总数据"
        sheet_sum_up = excel.add_sheet(sheet_name)
        issue_items = ["版本分支", "产品", "总数", "Open状态数", "Closed状态数", "项目", "备注"]
        for i in range(len(issue_items)):
            sheet_sum_up.write(0, i, issue_items[i])
        issue_infos = list(Issue_Milestone_Count.objects.filter(project=project).values())
        for i in range(len(issue_infos)):
            issue_state_rate = {}
            value_list = [issue_infos[i]['milestone'], issue_infos[i]['product'], issue_infos[i]['all_count'], issue_infos[i]['open_count'], issue_infos[i]['closed_count'], issue_infos[i]['project_id'], issue_infos[i]['remark']]
            for j in range(len(value_list)):
                sheet_sum_up.write(i+1, j, value_list[j])

            issue_state_rate["Open"] = issue_infos[i]['open_count']
            issue_state_rate["Closed"] = issue_infos[i]['closed_count']
            pie_charts(project, "%s %s %s Issue状态"%(issue_infos[i]['project_id'], issue_infos[i]['product'], issue_infos[i]['milestone']), **issue_state_rate)

        api_items = ["API总数", "可自动化总数", "未自动化总数", "自动测试", "未测试", "成功", "失败", "自动化率", "成功率", "失败率"]
        row_index = 1 + len(issue_infos) + 1 
        for i in range(len(api_items)):
            sheet_sum_up.write(row_index, i, api_items[i])
        api_case_list = list(Dependency.objects.filter(project=project).values())
        for api in api_case_list:
            if len(list(TestDetail.objects.filter(project=project, testResult="success", case_id=api["case_id"]).values())) > 0:
                obj = Result.objects.filter(case_id=api["case_id"],project_id=project).update(result="PASS")

        countDict = {}
        countDict["allCount"] = len(list(Dependency.objects.filter(project=project).values()))
        countDict["unautomatableCount"] = len(list(Dependency.objects.filter(project=project, runNum=0).values()))
        countDict["automatableCount"] = countDict["allCount"] - countDict["unautomatableCount"]
        countDict["passCount"] = len(list(Result.objects.filter(project=project, result="PASS").values()))
        countDict["failCount"] = len(list(Result.objects.filter(project=project, result="FAIL").values()))
        countDict["unTestCount"] = countDict["allCount"] - (countDict["passCount"] + countDict["failCount"])
        countDict["autoTestCount"] = countDict["passCount"] + countDict["failCount"]
        if countDict["allCount"] == 0:
            countDict["autoPer"] = 0
        else:
            countDict["autoPer"] = '{:.2%}'.format(round(countDict["automatableCount"], 2) / round(countDict["allCount"], 2))
        if countDict["autoTestCount"] == 0:
            countDict["passPer"] = 0
        else:
            countDict["passPer"] = '{:.2%}'.format(round(countDict["passCount"], 2) / round(countDict["autoTestCount"], 2))
        if countDict["autoTestCount"] == 0:
            countDict["failPer"] = 0
        else:
            countDict["failPer"] = '{:.2%}'.format(round(countDict["failCount"], 2) / round(countDict["autoTestCount"], 2))
        api_value_list = [countDict["allCount"], countDict["automatableCount"], countDict["unautomatableCount"], countDict["autoTestCount"], countDict["unTestCount"], countDict["passCount"], countDict["failCount"],  countDict["autoPer"], countDict["passPer"], countDict["failPer"]]

        row_index = row_index + 1
        for i in range(len(api_value_list)):
            sheet_sum_up.write(row_index, i, api_value_list[i])

        api_run_rate = {}
        api_run_rate["Pass"] = countDict["passCount"]
        api_run_rate["Fail"] = countDict["failCount"]
        api_run_rate["Untest"] = countDict["unTestCount"]
        pie_charts(project, "%s API运行结果"%project, **api_run_rate)

        row_index = row_index + 1
        single_api_items = ["API", "API功能", "run次数", "pass次数","fail次数", "未测试次数", "测试结果","失败原因"]
        for i in range(len(single_api_items)):
            sheet_sum_up.write(row_index, i, single_api_items[i])
        api_infos = list(Dependency.objects.filter(project=project).values())
        for api in api_infos:
            dictInfo = {}
            dictInfo["FailReason"] = ""
            api_function = api['raw'].split("|")[0]
            dictInfo["testTimes"] = len(list(TestDetail.objects.filter(project=project, case_id=api["case_id"]).values()))
            dictInfo["passTimes"] = len(list(TestDetail.objects.filter(project=project, testResult="success", case_id=api["case_id"]).values()))
            dictInfo["failTimes"] = len(list(TestDetail.objects.filter(project=project, testResult="failure", case_id=api["case_id"]).values()))
            dictInfo["untestTimes"] = len(list(TestDetail.objects.filter(project=project, testResult="untested", case_id=api["case_id"]).values()))
            if dictInfo["passTimes"] > 0:
                dictInfo["TestResult"] = "PASS"
            elif dictInfo["failTimes"] == 0:
                dictInfo["TestResult"] = "UnTest"
            else:
                dictInfo["TestResult"] = "FAIL"
            fail_ret = list(TestDetail.objects.filter(project=project, testResult="failure", case_id=api["case_id"]).values('failReason'))
            for item in fail_ret:
                dictInfo["FailReason"] = dictInfo["FailReason"] + item["failReason"]
            api_single_value = [api["case_id"], api_function, dictInfo["testTimes"], dictInfo["passTimes"], dictInfo["failTimes"], dictInfo["untestTimes"], dictInfo["TestResult"], dictInfo["FailReason"]]
            row_index = row_index + 1
            for i in range(len(api_single_value)):
                 sheet_sum_up.write(row_index, i, api_single_value[i])
        excel.save(self.file_name)
        return True
        
    def write_case(self, sheet_name, *infos):
        if os.path.exists(self.file_name):
            wb = xlrd.open_workbook(self.file_name)
            excel = xl_copy(wb)
        else:
            excel = xlwt.Workbook(encoding='utf-8')
            # sheet_sum_up = excel.add_sheet(self.sum_up_sheet)
            # items_sum_up = ["模块名称", "用例总数", "未合入/未测试", "PASS数", "FAIL数", "PASS率", "备注"]
            # for i in range(len(items_sum_up)):
            #     sheet_sum_up.write(0, i, items_sum_up[i])
        sheet = excel.add_sheet(sheet_name)
        item_list = ["用例编号", "用例名称", "测试类型", "优先级", "预置条件", "测试范围", "测试步骤",  "预期结果", "自动化", "关联API", "功能开发者", "用例设计者", "测试执行者", "测试日期", "测试结果", "备注"]
        for i in range(len(item_list)):
            sheet.write(0, i, item_list[i])
        for i in range(len(infos)):
            value_list = [infos[i]['case_number'], infos[i]['case_name'], infos[i]['case_type'], infos[i]['priority'], infos[i]['pre_condition'], infos[i]['test_range'], infos[i]['test_steps'], infos[i]['expect_result'], infos[i]['auto'], str(infos[i]['case_id']), infos[i]['fun_developer'], infos[i]['case_designer'],infos[i]['case_executor'],str(infos[i]['test_time']),infos[i]['test_result'],infos[i]['remark']]
            for j in range(len(value_list)):
                sheet.write(i+1, j, value_list[j])
        excel.save(self.file_name)
        return True

    def write_issue(self, sheet_name, *infos):
        if os.path.exists(self.file_name):
            wb = xlrd.open_workbook(self.file_name)
            excel = xl_copy(wb)
        else:
            excel = xlwt.Workbook(encoding='utf-8')
        sheet = excel.add_sheet(sheet_name)
        item_list = ["版本", "No.", "类型", "名称", "提交人", "解决人", "回归人", "更新时间", "回归结果", "是否ReOpen", "标签"]
        for i in range(len(item_list)):
            sheet.write(0, i, item_list[i])
        for i in range(len(infos)):
            value_list = [infos[i]['milestone'], infos[i]['issue_id'], infos[i]['issue_type'], infos[i]['name'], infos[i]['author'], infos[i]['assignees'], infos[i]['test'], infos[i]['updated'], infos[i]['result'], infos[i]['reopen'], infos[i]['tag']]
            for j in range(len(value_list)):
                sheet.write(i+1, j, value_list[j])
        excel.save(self.file_name)
        return True

    def write_testplan(self, sheet_name, *infos):
        if os.path.exists(self.file_name):
            wb = xlrd.open_workbook(self.file_name)
            excel = xl_copy(wb)
        else:
            excel = xlwt.Workbook(encoding='utf-8')
        sheet = excel.add_sheet(sheet_name)
        item_list = ["版本", "任务名称", "优先级", "计划开始时间", "计划结束时间", "实际开始时间", "时间结束时间", "完成进度","执行人员", "备注"]
        for i in range(len(item_list)):
            sheet.write(0, i, item_list[i])
        for i in range(len(infos)):
            if infos[i]['p_start_time'] is not None:
                p_start_time = infos[i]['p_start_time'].strftime("%Y/%m/%d")
            else:
                p_start_time = ""
            if infos[i]['a_start_time'] is not None:
                a_start_time = infos[i]['a_start_time'].strftime("%Y/%m/%d")
            else:
                a_start_time = ""
            if infos[i]['p_finish_time'] is not None:
               p_finish_time = infos[i]['p_finish_time'].strftime("%Y/%m/%d")
            else:
                p_finish_time = ""
            if infos[i]['a_finish_time'] is not None:
                a_finish_time = infos[i]['a_finish_time'].strftime("%Y/%m/%d")
            else:
                a_finish_time = ""
            value_list = [infos[i]['milestone'], infos[i]['task_id'], infos[i]['priority'], p_start_time, p_finish_time, a_start_time, a_finish_time, infos[i]['progress'], infos[i]['executor'], infos[i]['remark']]
            for j in range(len(value_list)):
                sheet.write(i+1, j, value_list[j])
        excel.save(self.file_name)
        return True

    def write_case_count(self, module, *infos):
        # sheet_name_list = self.read_sheet_names()
        # if self.sum_up_sheet not in sheet_name_list:

        pass_count = 0
        fail_count = 0
        other_count = 0
        all_count = 0
        for item in infos:
            if len(item['case_number']) == 0:
                continue
            all_count += 1
            if item['test_result'] == "PASS":
                pass_count += 1
            elif item['test_result'] == "FAIL":
                fail_count += 1
            else:
                other_count += 1
        pass_per = round(pass_count / all_count * 100, 2)
        info_list = [module, all_count, other_count, pass_count, fail_count, pass_per]
        status, output = self.add_row_data(self.sum_up_sheet, info_list)
        return status, output

    def read_sheet_names(self):
        table_obj = xlrd.open_workbook(self.file_name)
        sheet_names = table_obj.sheet_names()
        return sheet_names
        #return sheet_names[4:]

    def get_sheet_index(self, sheet_name):
        table_obj = xlrd.open_workbook(self.file_name)
        sheet_names = table_obj.sheet_names()
        count = 0
        for item in sheet_names:
            if sheet_name == item:
                sheet_index = count
                break
            count = count + 1
            if count == len(sheet_names):
                return False, "Not Found tabel %s, Please Check it ~" %sheet_name
        return True, sheet_index

    def read_sheet_all_content(self, sheet_name): 
        table_obj = xlrd.open_workbook(self.file_name)
        content = table_obj.sheet_by_name(sheet_name)
        ord_list=[]
        for rownum in range(content.nrows):
            ord_list.append(content.row_values(rownum))
        #返回的类型是一个list
        return ord_list

    def read_sheet_content(self, sheet_name):
        table_obj = xlrd.open_workbook(self.file_name)
        sheet_obj = table_obj.sheet_by_name(sheet_name)
        row_num = sheet_obj.nrows
        col_num = sheet_obj.ncols
        # titles = sheet_obj.row_values(rowx=5)  # 默认设置为1，除去title
        value_list = []
        for row in range(1, row_num):
            values = sheet_obj.row_values(rowx=row)
            value_list.append(values)
        return value_list

    def get_case_info(self, sheet_name, case_num):
        cases = self.read_sheet_content(sheet_name)
        count = 0
        for case in cases:
            if case[0] == case_num:
                return True, case
            else:
                count = count + 1
            if count == len(cases):
                return False, "Not Fount %s Case, Please check it ~" %case_num

    def delete_excel_row(self, sheet_name, case_num):
        table_obj = xlrd.open_workbook(self.file_name)
        sheet = table_obj.sheet_by_name(sheet_name)
        col_val = sheet.col_values(0)
        count = 0
        for item in col_val:
            if item == case_num:
                row_index = count
                break
            count = count + 1
            if count == len(col_val):
                return False, "Not Fount %s Case, Please Check it ~ " %case_num
        read_all = self.read_sheet_all_content(sheet_name)
        read_all.pop(row_index)
        status, sheet_index = self.get_sheet_index(sheet_name)
        if not status:
            return False, sheet_index
        new_wb = xl_copy(table_obj)
        new_sheet = new_wb.get_sheet(sheet_index)
        for m in range(len(read_all)):
            for n in range(len(read_all[m])):
                new_sheet.write(m, n, read_all[m][n])
        new_wb.save(self.file_name)
        return True, "Delete %s Success……" %case_num

    def modify_excel_row(self, sheet_name, case_info):
        table_obj = xlrd.open_workbook(self.file_name)
        sheet = table_obj.sheet_by_name(sheet_name)
        col_val=sheet.col_values(0)#第一列的值
        count = 0
        for item in col_val:
            if item == case_info[0]:
                row_index = count
                break
            count = count + 1
            if count == len(col_val):
                return False, "Not Fount %s Case, Please Check it ~ " %case_info[0]
        status, sheet_index = self.get_sheet_index(sheet_name)
        if not status:
            return False, sheet_index
        new_wb = xl_copy(table_obj)
        new_sheet = new_wb.get_sheet(sheet_index)
        for i in range(len(case_info)):
            new_sheet.write(row_index, i, case_info[i])
        new_wb.save(self.file_name)
        return True, "Modify %s Success……" %case_info[0]

    def add_row_data(self, sheet_name, info_list):
        table_obj = xlrd.open_workbook(self.file_name)
        sheet = table_obj.sheet_by_name(sheet_name)
        nrows = sheet.nrows
        new_wb = xl_copy(table_obj)  # 将原有的Excel，拷贝一个新的副本
        status, sheet_index = self.get_sheet_index(sheet_name)
        if not status:
            return False, sheet_index
        new_sheet = new_wb.get_sheet(sheet_index) # 重新在新的Excel中获取
        for i in range(len(info_list)):
            new_sheet.write(nrows,i,info_list[i])
        new_wb.save(self.file_name)
        return True, 'Add %s Success……' %info_list[0]

    def delete_all_case(self, sheet_name):
        table_obj = xlrd.open_workbook(self.file_name)
        sheet = table_obj.sheet_by_name(sheet_name)
        read_all = self.read_sheet_all_content(sheet_name)
        length = len(read_all)
        if length > 6:
            for i in range(length-1, 5, -1):
                read_all.pop(i)
        status, sheet_index = self.get_sheet_index(sheet_name)
        if not status:
            return False, sheet_index
        new_wb = xl_copy(table_obj)
        new_sheet = new_wb.get_sheet(sheet_index)
        for m in range(len(read_all)):
            for n in range(len(read_all[m])):
                new_sheet.write(m, n, read_all[m][n])
        new_wb.save(self.file_name)
        return True, "Delete Data Success …… "

    def split_table(self, sheet_name):
        content = self.read_sheet_content(sheet_name)
        sheet_def = {"Sum_Up": "概览", "Host_Apply": "主机交付", "IDC_Mgmt": "数据中心", "Device_Mgmt": "设备管理", "Hardware_Mgmt": "硬件管理", "InstallOS_Mgmt": "装机管理", "Image_Mgmt": "镜像管理", "OOB_Mgmt": "带外管理", "Task_Mgmt": "任务管理", "Proxy_Mgmt": "分布式管理", "Asset_Mgmt": "资产管理", "ACL_Mgmt": "安全审计", "Report_Mgmt": "报表管理", "User_Mgmt": "用户管理", "System_Mgmt": "系统管理", "Notice_Mgmt": "通知中心", "Env_Config": "环境配置与日志", "Auth_Mgmt": "权限管理-UAM", "Data_Sync": "数据对接"}
        sheet_keys = sheet_def.keys()
        undef_list = []
        for items in content[6:]:
            count = 0
            for sheet_key in sheet_keys:
                case_id = items[0].upper()
                if case_id.startswith(sheet_key.upper()):
                    status, output = self.add_row_data(sheet_def[sheet_key], items)
                    break
                else:
                    count = count + 1
                if count == len(sheet_keys):
                    undef_list.append(items)
        status, output = self.delete_all_case(sheet_name)
        if len(undef_list) > 0:
            for items in undef_list:
                status, output = self.add_row_data(sheet_name, items)
                
    def modify_case_status(self, sheet_name, case_num, status):
        curTime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        cases = self.read_sheet_content(sheet_name)
        count = 0
        if status:
            result = "PASS"
        else:
            result = "FAIL"
        for case_info in cases:
            if case_info[0] == case_num:
                case_info[12] = "Robot"
                case_info[13] = curTime
                case_info[14] = result
                status, oupput = self.modify_excel_row(sheet_name, case_info)
                return status, oupput
            else:
                count = count + 1
            if count == len(cases):
                return False, "Not Fount %s Case, Please check it ~" %case_num


        return True, "Split Case Info Succuss …… "

