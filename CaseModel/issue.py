# issue.py

import  xml.dom.minidom
import sys
import os
import re
import requests
import shutil
import argparse
import xlwt
import xlrd
import importlib,sys 
import datetime
from xlutils.copy import copy as xl_copy
from CaseModel.models import Issue_Tag_Count, Issue_Milestone_Count, Issue_Info
import logging
logger = logging.getLogger(__name__) 

importlib.reload(sys)
# Define Common Variables
GITLABREPO = "http://gitlab.idcos.com"
PRODUCT = "CloudBoot/cloudboot"
#RSS_TOKEN = "Please input yourself rss_token ... "
RSS_TOKEN = "Ywd7gYtsKJGzDQG68ZQb"
#MILESTONE = "Please input milestone your want to count ... "
MILESTONE = "all"
pageMaxNum = 1000
DEBUG = False

def getContent(repo, product, rss_token, milestone):
    if milestone == "all":
        url_head = "%s/%s/issues.atom?feed_token=%s&scope=all&state=" %(repo, product, rss_token)
    else:
        url_head = "%s/%s/issues.atom?feed_token=%s&milestone_title=%s&scope=all&state=" %(repo, product, rss_token, milestone)
    all_url = url_head + "all"
    open_url = url_head + "opened"
    closed_url = url_head + "closed"
    url_dict = {"open": open_url, "all": all_url, "closed": closed_url}
    base_dir = "static/raw"
    for Key in url_dict.keys():
        target_dir = "static/raw/%s" %Key
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
        else:
            shutil.rmtree(target_dir)
            os.mkdir(target_dir)

        for num in range(1, pageMaxNum):
            url = url_dict[Key] + "&page=%d" %num
            logger.info("url: %s" %url)
            resp = requests.get(url)
            logger.info
            if not resp.ok:
                logger.debug(resp.ok)
                break
            if len(resp.text) < 500:
                break
            text = resp.text
            with open('%s/issues-%d.xml'%(target_dir, num), 'w+') as f:
                f.write(text)

            if num > 1:
                with open('%s/issues-%d.xml'%(target_dir, num-1)) as f:
                    b_text = f.read()
                if len(text) == len(b_text):
                    break
    return True

def analysisTag(tagAggregate, product):
    infoList = []
    for item in tagAggregate:
        infoDict = {}
        title = item.getElementsByTagName('title')[0]
        title = title.childNodes[0].data
        infoDict['title'] = title

        updated = item.getElementsByTagName('updated')[0]
        updated = updated.childNodes[0].data
        updated = updated.split('T')[0]
        infoDict['updated'] = updated

        try:
            milestone = item.getElementsByTagName('milestone')[0]
        except:
            infoDict['milestone'] = "未指配"
        else:
            milestone = milestone.childNodes[0].data
            infoDict['milestone'] = milestone

        ID = item.getElementsByTagName('id')[0]
        ID = ID.childNodes[0].data
        ID = ID.split('/')[-1]
        infoDict['id'] = "%s/%s/issues/%s"%(GITLABREPO, product, ID)

        author = item.getElementsByTagName('author')[0]
        authorName = author.getElementsByTagName('name')[0]
        authorName = authorName.childNodes[0].data
        infoDict['author'] = authorName
        
        assigneeList = []
        try:
            assignees = item.getElementsByTagName('assignees')[0]
        except:
            infoDict['assignee'] = ["未指配"]
        else:
            assignees = assignees.getElementsByTagName('assignee')
            for i in range(len(assignees)):
                name = assignees[i].getElementsByTagName('name')
                assignee = name[0].childNodes[0].data
                assigneeList.append(assignee)
        infoDict['assignee'] = assigneeList
        labelList = []
        try:
            labels = item.getElementsByTagName('labels')[0]
        except:
            infoDict['lables'] = ["无标签"]
        else:
            labels = labels.getElementsByTagName('label')
            for i in range(len(labels)):
                label = labels[i].childNodes[0].data
                labelList.append(label)
        infoDict['lables'] = labelList

        if "Bug" in labelList:
            infoDict['type'] = 'BUG' 
        elif '优化' in labelList:
            infoDict['type'] = '优化'
        elif '需求' in labelList:
            infoDict['type'] = '需求'
        elif 'Mark' in labelList:
            infoDict['type'] = 'Mark'
        else:
            infoDict['type'] = '未知'

        infoList.append(infoDict)

    return infoList

def analysisXML(tagAggregates,product):
    infoList = []
    for item in tagAggregates:
        infoDict = {}

        title = item.getElementsByTagName('title')[0]
        title = title.childNodes[0].data
        infoDict['title'] = title

        updated = item.getElementsByTagName('updated')[0]
        updated = updated.childNodes[0].data
        infoDict['updated'] = updated

        try:
            milestone = item.getElementsByTagName('milestone')[0]
        except:
            infoDict['milestone'] = "未指配"
        else:
            milestone = milestone.childNodes[0].data
            infoDict['milestone'] = milestone

        ID = item.getElementsByTagName('id')[0]
        ID = ID.childNodes[0].data
        ID = ID.split('/')[-1]
        infoDict['id'] = "%s/%s/issues/%s"%(GITLABREPO, product,ID)

        author = item.getElementsByTagName('author')[0]
        authorName = author.getElementsByTagName('name')[0]
        authorName = authorName.childNodes[0].data
        infoDict['author'] = authorName

        labelList = []
        try:
            labels = item.getElementsByTagName('labels')[0]
        except:
            infoDict['lables'] = ["无标签"]
        else:
            labels = labels.getElementsByTagName('label')
            for i in range(len(labels)):
                label = labels[i].childNodes[0].data
                labelList.append(label)
            infoDict['lables'] = labelList

        assigneeList = []
        try:
            assignees = item.getElementsByTagName('assignees')[0]
        except:
            infoDict['assignees'] = ["未指配"]
        else:
            items = assignees.getElementsByTagName('assignee')
            for item in items:
                assigneeName = item.getElementsByTagName('name')[0]
                assigneeName = assigneeName.childNodes[0].data
                assigneeList.append(assigneeName)
            infoDict['assignees'] = assigneeList

        infoList.append(infoDict)

    return infoList

def get_sum_up_data(*infoList):
    milestone_dict = {}
    author_dict = {}
    assignee_dict = {}
    for info in infoList:
        if info["milestone"] in milestone_dict.keys():
            milestone_dict[info["milestone"]]["sum"] = milestone_dict[info["milestone"]]["sum"] + 1
        else:
            milestone_dict[info["milestone"]] = {}
            milestone_dict[info["milestone"]]["sum"] = 1
        for lable in info["lables"]:
            if lable in  milestone_dict[info["milestone"]].keys():
                milestone_dict[info["milestone"]][lable] = milestone_dict[info["milestone"]][lable] + 1
            else:
                milestone_dict[info["milestone"]][lable] = 1
        # if info["author"] in milestone_dict[info["milestone"]].keys():
        #     milestone_dict[info["milestone"]][info["author"]] = milestone_dict[info["milestone"]][info["author"]] + 1
        # else:
        #     milestone_dict[info["milestone"]][info["author"]] = 1

        # for assignee in info["assignees"]:
        #     if assignee in milestone_dict[info["milestone"]].keys():
        #         milestone_dict[info["milestone"]][assignee] = milestone_dict[info["milestone"]][assignee] + 1
        #     else:
        #         milestone_dict[info["milestone"]][assignee] = 1

        if info["author"] in author_dict.keys():
            author_dict[info["author"]]["sum"] = author_dict[info["author"]]["sum"] + 1
        else:
            author_dict[info["author"]] = {}
            author_dict[info["author"]]["sum"] = 1

        for lable in info["lables"]:
            if lable in author_dict[info["author"]].keys():
                author_dict[info["author"]][lable] = author_dict[info["author"]][lable] + 1
            else:
                author_dict[info["author"]][lable] = 1

        if info["milestone"] in author_dict[info["author"]].keys():
            author_dict[info["author"]][info["milestone"]] = author_dict[info["author"]][info["milestone"]] + 1
        else:
            author_dict[info["author"]][info["milestone"]] = 1
        for assignee in info["assignees"]:
            if assignee in author_dict[info["author"]].keys():
                author_dict[info["author"]][assignee] = author_dict[info["author"]][assignee] + 1
            else:
                author_dict[info["author"]][assignee] = 1

        for assignee in info["assignees"]:
            if assignee in assignee_dict.keys():
                assignee_dict[assignee]["sum"] = assignee_dict[assignee]["sum"] + 1
            else:
                assignee_dict[assignee] = {}
                assignee_dict[assignee]["sum"] = 1
            for lable in info["lables"]:
                if lable in assignee_dict[assignee].keys():
                    assignee_dict[assignee][lable] = assignee_dict[assignee][lable] + 1
                else:
                    assignee_dict[assignee][lable] = 1
            if info["milestone"] in assignee_dict[assignee].keys():
                assignee_dict[assignee][info["milestone"]] =assignee_dict[assignee][info["milestone"]] + 1
            else:
                assignee_dict[assignee][info["milestone"]] = 1

    return [milestone_dict, author_dict, assignee_dict]

def get_issue_data(state, *infos):
    if state == "closed":
        result = "PASS"
    else:
        result = ""
    milestone_dict = {}
    lable_dict = {}
    for info in infos:
        info["result"] = result
        if "ReOpen" in info["lables"]:
            info["ReOpen"] = "是"
        else:
            info["ReOpen"] = "否"
        if info["milestone"] in milestone_dict.keys():
            milestone_dict[info["milestone"]].append(info)
        else:
            milestone_dict[info["milestone"]] = []
            milestone_dict[info["milestone"]].append(info)

    return milestone_dict

def write_excel_count(sheet_name, **info):
    cur_day = datetime.datetime.now().strftime('%Y%m%d')
    excel_file_name = 'issues_count_%s.xls' %cur_day
    #初始化一个excel
    if os.path.exists(excel_file_name):
        wb = xlrd.open_workbook(excel_file_name)
        excel = xl_copy(wb)
    else:
        excel = xlwt.Workbook(encoding='utf-8')
    #新建一个sheet
    sheet = excel.add_sheet(sheet_name)
    #设置样式
    # style = xlwt.XFStyle()#初始化样式
    # font = xlwt.Font()#创建字体
    # font.name = u'微软雅黑' #字体类型
    # font.colour_index = 6   #字体颜色
    # font.underline = True #下划线
    # font.italic = True #斜体
    # font.bold= True
    # font.height = 600    #字体大小   200等于excel字体大小中的10
    # style.font = font   #设定样式    
    # pattern = xlwt.Pattern()  # Create the pattern
    # pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
    # pattern.pattern_fore_colour = 4  # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray, the list goes on...
    # # sheet.col(0).width = 300 #设置某列的单元格宽度
    p_keys = list(info.keys())
    c_keys=[]
    for p_key in p_keys:
        c_keys = c_keys + list(info[p_key].keys())
    c_keys = list(set(c_keys))
    for p_key in p_keys:
        for c_key in c_keys:
            if not c_key in info[p_key]:
                info[p_key][c_key] = ""
    primary_type = sheet_name.split("_")[1]
    sheet.write(0, 0, "%s\\lable" %primary_type)
    for i in range(len(p_keys)):
        sheet.write(i+1, 0, p_keys[i])

    for j in range(len(c_keys)):
        sheet.write(0, j+1, c_keys[j])

    for i in range(len(p_keys)):
        # c_keys = list(info[p_keys[i]].keys())
        for j in range(len(c_keys)):
            sheet.write(i+1, j+1, info[p_keys[i]][c_keys[j]])
    #sheet.write(1,0,'test',style)   #写入带字体样式的内容
    excel.save(excel_file_name)

def getCount(project,product,milestone):
    state_list = ["open", "closed", "all"]
    for state in state_list:
        obj = os.popen('ls static/raw/%s/' %state)
        string = obj.read()
        files = string.split('\n')
        infoList = []
        for file_name in files:
            if len(file_name) == 0:
                continue
            dom = xml.dom.minidom.parse('static/raw/%s/%s'%(state, file_name))
            root = dom.documentElement
            entries = root.getElementsByTagName('entry')
            infos = analysisXML(entries,product)
            infoList = infoList + infos
        sum_up_data_list = get_sum_up_data(*infoList)
        if milestone == "all":
            milestone_list = sum_up_data_list[0].keys()
            for milestone_sub in milestone_list:
                ret_old = list(Issue_Milestone_Count.objects.filter(product=product,milestone=milestone_sub,project_id=project).values())
                if state == "all":
                    if len(ret_old) > 0:
                        obj = Issue_Milestone_Count.objects.filter(product=product,project_id=project,milestone=milestone_sub).update(all_count=sum_up_data_list[0][milestone_sub]['sum'])
                    else:
                        obj = Issue_Milestone_Count(product=product,project_id=project,milestone=milestone_sub, all_count=sum_up_data_list[0][milestone_sub]['sum'])
                        obj.save()
                    for item in sum_up_data_list[0][milestone_sub].keys():
                        if item != "sum":
                            ret_lable = list(Issue_Tag_Count.objects.filter(product=product,milestone=milestone_sub,project_id=project, tag=item).values())
                            if len(ret_lable) > 0:
                                obj = Issue_Tag_Count.objects.filter(product=product,project_id=project,milestone=milestone_sub,tag=item).update(all_count=sum_up_data_list[0][milestone_sub][item])
                            else:
                                obj = Issue_Tag_Count(product=product,project_id=project,milestone=milestone_sub, tag=item, all_count=sum_up_data_list[0][milestone_sub][item])
                                obj.save()
                elif state == "open":
                    if len(ret_old) > 0:
                        obj = Issue_Milestone_Count.objects.filter(product=product,project_id=project,milestone=milestone_sub).update(open_count=sum_up_data_list[0][milestone_sub]['sum'])
                    else:
                        obj = Issue_Milestone_Count(product=product,project_id=project,milestone=milestone_sub, open_count=sum_up_data_list[0][milestone_sub]['sum'])
                        obj.save()
                    for item in sum_up_data_list[0][milestone_sub].keys():
                        if item != "sum":
                            ret_lable = list(Issue_Tag_Count.objects.filter(product=product,milestone=milestone_sub,project_id=project, tag=item).values())
                            if len(ret_lable) > 0:
                                obj = Issue_Tag_Count.objects.filter(product=product,project_id=project,milestone=milestone_sub,tag=item).update(open_count=sum_up_data_list[0][milestone_sub][item])
                            else:
                                obj = Issue_Tag_Count(product=product,project_id=project,milestone=milestone_sub, tag=item, open_count=sum_up_data_list[0][milestone_sub][item])
                                obj.save()
                elif state == "closed":
                    if len(ret_old) > 0:
                        obj = Issue_Milestone_Count.objects.filter(product=product,project_id=project,milestone=milestone_sub).update(closed_count=sum_up_data_list[0][milestone_sub]['sum'])
                    else:
                        obj = Issue_Milestone_Count(product=product,project_id=project,milestone=milestone_sub, closed_count=sum_up_data_list[0][milestone_sub]['sum'])
                        obj.save()
                    for item in sum_up_data_list[0][milestone_sub].keys():
                        if item != "sum":
                            ret_lable = list(Issue_Tag_Count.objects.filter(product=product,milestone=milestone_sub,project_id=project, tag=item).values())
                            if len(ret_lable) > 0:
                                obj = Issue_Tag_Count.objects.filter(product=product,project_id=project,milestone=milestone_sub,tag=item).update(closed_count=sum_up_data_list[0][milestone_sub][item])
                            else:
                                obj = Issue_Tag_Count(product=product,project_id=project,milestone=milestone_sub, tag=item, closed_count=sum_up_data_list[0][milestone_sub][item])
                                obj.save()
        else:
            ret_old = list(Issue_Milestone_Count.objects.filter(product=product,milestone=milestone,project_id=project).values())
            if state == "all":
                if len(ret_old) > 0:
                    obj = Issue_Milestone_Count.objects.filter(product=product,project_id=project,milestone=milestone).update(all_count=sum_up_data_list[0][milestone]['sum'])
                else:
                    obj = Issue_Milestone_Count(product=product,project_id=project,milestone=milestone, all_count=sum_up_data_list[0][milestone]['sum'])
                    obj.save()
                for item in sum_up_data_list[0][milestone].keys():
                    if item != "sum":
                        ret_lable = list(Issue_Tag_Count.objects.filter(product=product,milestone=milestone,project_id=project, tag=item).values())
                        if len(ret_lable) > 0:
                            obj = Issue_Tag_Count.objects.filter(product=product,project_id=project,milestone=milestone,tag=item).update(all_count=sum_up_data_list[0][milestone][item])
                        else:
                            obj = Issue_Tag_Count(product=product,project_id=project,milestone=milestone, tag=item, all_count=sum_up_data_list[0][milestone][item])
                            obj.save()
            elif state == "open":
                if len(ret_old) > 0:
                    obj = Issue_Milestone_Count.objects.filter(product=product,project_id=project,milestone=milestone).update(open_count=sum_up_data_list[0][milestone]['sum'])
                else:
                    obj = Issue_Milestone_Count(product=product,project_id=project,milestone=milestone, open_count=sum_up_data_list[0][milestone]['sum'])
                    obj.save()
                for item in sum_up_data_list[0][milestone].keys():
                    if item != "sum":
                        ret_lable = list(Issue_Tag_Count.objects.filter(product=product,milestone=milestone,project_id=project, tag=item).values())
                        if len(ret_lable) > 0:
                            obj = Issue_Tag_Count.objects.filter(product=product,project_id=project,milestone=milestone,tag=item).update(open_count=sum_up_data_list[0][milestone][item])
                        else:
                            obj = Issue_Tag_Count(product=product,project_id=project,milestone=milestone, tag=item, open_count=sum_up_data_list[0][milestone][item])
                            obj.save()
            elif state == "closed":
                if len(ret_old) > 0:
                    obj = Issue_Milestone_Count.objects.filter(product=product,project_id=project,milestone=milestone).update(closed_count=sum_up_data_list[0][milestone]['sum'])
                else:
                    obj = Issue_Milestone_Count(product=product,project_id=project,milestone=milestone, closed_count=sum_up_data_list[0][milestone]['sum'])
                    obj.save()
                for item in sum_up_data_list[0][milestone].keys():
                    if item != "sum":
                        ret_lable = list(Issue_Tag_Count.objects.filter(product=product,milestone=milestone,project_id=project, tag=item).values())
                        if len(ret_lable) > 0:
                            obj = Issue_Tag_Count.objects.filter(product=product,project_id=project,milestone=milestone,tag=item).update(closed_count=sum_up_data_list[0][milestone][item])
                        else:
                            obj = Issue_Tag_Count(product=product,project_id=project,milestone=milestone, tag=item, closed_count=sum_up_data_list[0][milestone][item])
                            obj.save()
        # write_excel_count("%s_milestone" %state, **sum_up_data_list[0])
        # write_excel_count("%s_author" %state, **sum_up_data_list[1])
        # write_excel_count("%s_assignee" %state, **sum_up_data_list[2])

def write_excel_issue(sheet_name, *infos):
    cur_day = datetime.datetime.now().strftime('%Y%m%d')
    excel_file_name = 'issues_count_%s.xls' %cur_day
    if os.path.exists(excel_file_name):
        wb = xlrd.open_workbook(excel_file_name)
        excel = xl_copy(wb)
    else:
        excel = xlwt.Workbook(encoding='utf-8')
    sheet = excel.add_sheet(sheet_name)
    item_list = ["版本", "No.", "类型", "名称", "提交人", "解决人", "回归人", "更新时间", "回归结果", "是否ReOpen", "标签"]
    for i in range(len(item_list)):
        sheet.write(0, i, item_list[i])
    for i in range(len(infos)):
        value_list = [infos[i]['milestone'], infos[i]['issue_id'], infos[i]['type'], infos[i]['title'], infos[i]['author'], infos[i]['assignee'], infos[i]['author'], infos[i]['updated'], infos[i]['result'], infos[i]['ReOpen'], infos[i]['lables']]
        for j in range(len(value_list)):
            sheet.write(i+1, j, value_list[j])
    excel.save(excel_file_name)

def get_issue(project,product):
    #state_list = ["all", "open", "closed"]
    state_list = ["open", "closed"]
    for state in state_list:
        all_dict = {}
        obj = os.popen('ls static/raw/%s/' %state)
        string = obj.read()
        files = string.split('\n')
        infoList = []
        for file_name in files:
            if len(file_name) == 0:
                continue
            dom = xml.dom.minidom.parse('static/raw/%s/%s'%(state, file_name))
            root = dom.documentElement
            entries = root.getElementsByTagName('entry')
            infos = analysisTag(entries, product)
            infoList = infoList + infos
        milestone_dict = get_issue_data(state, *infoList)
        all_dict.update(milestone_dict)
        for ms in all_dict:
            for issue in all_dict[ms]:
                # write_excel_issue(key, *all_list[0][key])
                ret_lable = list(Issue_Info.objects.filter(product=product,milestone=issue['milestone'],project_id=project, issue_id=issue["id"]).values())
                if len(ret_lable) > 0:
                    obj = Issue_Info.objects.filter(product=product,project_id=project,milestone=issue['milestone'],issue_id=issue["id"]).update(issue_id=issue['id'], issue_type=issue['type'],name=issue['title'], author=issue['author'],assignees=issue['assignee'],test=issue['author'], updated=issue['updated'], result=issue['result'],reopen=issue['ReOpen'],tag=issue['lables'])
                else:
                    obj = Issue_Info(product=product,project_id=project,milestone=issue['milestone'],issue_id=issue['id'],  issue_type=issue['type'],name=issue['title'], author=issue['author'],assignees=issue['assignee'],test=issue['author'], updated=issue['updated'], result=issue['result'],reopen=issue['ReOpen'],tag=issue['lables'])
                    obj.save()
    return True

def issue_start(project, repo, product, rss_token, milestone):
    getContent(repo, product,rss_token, milestone)
    getCount(project,product,milestone)
    get_issue(project,product)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Auto Count GitLab Issues")
    parser.add_argument('-r','--gitlab_repo', dest="repo", action="store", default="%s" %GITLABREPO, help="Default value is %s" %GITLABREPO)
    parser.add_argument('-t','--rss_token', dest="token", action="store", default="%s" %RSS_TOKEN, help="Default value is %s" %RSS_TOKEN)
    parser.add_argument('-p','--product', dest="product", action="store", default="%s" %PRODUCT, help="Default value is %s" %PRODUCT)
    parser.add_argument('-m','--milestone', dest="milestone", action="store", default="%s" %MILESTONE, help="[ all/milestone_info ], [ all ] will cover all milestones, Default value is %s" %MILESTONE)
    parser.add_argument('-d','--debug', dest="debug", action="store", default='N' , help="[Y/N] Y as Yes, N as Not, default value is N")
    args = parser.parse_args()
    if args.debug.upper() == "Y":
        DEBUG = True
    issue_start(args.repo, args.product, args.token, args.milestone)
