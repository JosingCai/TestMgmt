import os
from django.shortcuts import render, redirect
from django.http import HttpResponse,FileResponse
from django.contrib import messages
from django.conf import settings
from rest_framework.decorators import api_view
from CaseModel.models import ProductDir,Product_Gitlab,Issue_Info,Test_Plan_Schedule
from CaseModel.issue import issue_start
from CaseModel.testcase import TestCase as t_TestCase
from CaseModel.models import TestCase as m_TestCase
from CaseModel.testplan import create_gantt


# Create your views here.
@api_view(['GET', 'POST'])
def test_case(request, project,module):
    if request.method == "POST":
        body = dict(request.POST)
        case_number = request.POST.get('case_number')
        case_name = request.POST.get('case_name')
        case_type = request.POST.get('case_type')
        priority = request.POST.get('priority')
        pre_condition = request.POST.get('pre_condition')
        test_range = request.POST.get('test_range')
        test_steps = request.POST.get('test_steps')
        expect_result = request.POST.get('expect_result')
        auto = request.POST.get('auto')
        case_id = request.POST.get('api_related')
        fun_developer = request.POST.get('fun_developer')
        case_designer = request.POST.get('case_designer')
        case_executor = request.POST.get('case_executor')
        test_time = request.POST.get('test_time')
        remark = request.POST.get('remark')
        ret_old = list(m_TestCase.objects.filter(case_number=case_number,project_id=project).values())
        if len(ret_old) > 0:
            obj = m_TestCase.objects.filter(case_number=case_number,project_id=project).update(case_name=case_name,case_type=case_type,priority=priority,pre_condition=pre_condition,test_range=test_range,test_steps=test_steps,expect_result=expect_result,auto=auto,case_id=case_id,fun_developer=fun_developer,case_designer=case_designer,case_executor=case_executor,test_time=test_time,module=module,remark=remark,project_id=project)
        else:
            obj = m_TestCase(case_number=case_number,case_name=case_name,case_type=case_type,priority=priority,pre_condition=pre_condition,test_range=test_range,test_steps=test_steps,expect_result=expect_result,auto=auto,case_id=case_id,fun_developer=fun_developer,case_designer=case_designer,case_executor=case_executor,test_time=test_time,module=module,remark=remark,project_id=project)
            obj.save()
        messages.success(request,"操作成功")
    module_list = list(set(list(m_TestCase.objects.filter(project_id=project).values_list("module"))))
    modules = []
    for item in module_list:
        modules.append(item[0])
    if len(modules) == 0:
        modules = ["新需求"]
        ret_list = []
    else:
        ret_list = list(m_TestCase.objects.filter(project_id=project,module=module).values())
    titles = ["case_number"]
    return render(request, "test_case.html", {"transList": ret_list, "module": module, "modules": modules, "titles":titles, "project": project})

@api_view(['GET', 'POST'])
def case_export(request, project):
    module_list = list(set(list(m_TestCase.objects.filter(project_id=project).values_list("module"))))
    modules = []
    for item in module_list:
        modules.append(item[0])
    t_handle = t_TestCase(project,operate="export")
    for item in modules:
        ret_list = list(m_TestCase.objects.filter(module=item,project=project).values())
        if item == None:
            item = "未知"
        t_handle.write_sheet_info(item, *ret_list)
    if request.method == "POST":
        body = dict(request.POST)
        issue_list = list(Issue_Info.objects.filter(milestone=body['milestone'][0],project=project).values())
        t_handle.write_issue_info("issue汇总", *issue_list)    
        testplan_list = list(Test_Plan_Schedule.objects.filter(milestone=body['milestone'][0],project=project).values())
        t_handle.write_testplan_info("测试计划时间表", *testplan_list)

    ret_file_name = t_handle.get_file_name()
    file = open(ret_file_name, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename=' + ret_file_name
    return response

@api_view(['GET'])
def template_download(request, project):
    ret_file_name = os.path.join(settings.MEDIA_ROOT,"yunji_case_template.xls") 
    file = open(ret_file_name, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename=' + ret_file_name
    return response


@api_view(['POST'])
def case_import(request, project):
    if request.method == "POST":    # 请求方法为POST时，进行处理  
        upload_file =request.FILES.get("action", None)    # 获取上传的文件，如果没有文件，则默认为None  
        if not upload_file:  
            return HttpResponse("请先上传文件……")
        file_path = os.path.join(settings.MEDIA_ROOT,upload_file.name) 
        destination = open(file_path,'wb+')    # 打开特定的文件进行二进制的写操作  
        for chunk in upload_file.chunks():      # 分块写入文件  
            destination.write(chunk)  
        destination.close()  

        t_handle = t_TestCase(project=project, file_name=file_path)
        case_list = t_handle.read_all()
        # print("case_list: ",case_list)
        for info in case_list:
            # print("info: ",info)
            ret_old = list(m_TestCase.objects.filter(case_number=info['case_number']).values())
            if len(ret_old) > 0:
                obj = m_TestCase.objects.filter(case_number=info['case_number']).update(case_name=info['case_name'],case_type=info['case_type'],priority=info['priority'],pre_condition=info['pre_condition'],test_range=info['test_range'],test_steps=info['test_steps'],expect_result=info['expect_result'],auto=info['auto'],case_id=info['api_related'], fun_developer=info['fun_developer'], case_designer=info['case_designer'],case_executor=info['case_executor'],test_time=info['test_time'], test_result=info['test_result'],project_id=info['project'],module=info['module']['name'],remark=info['remark'])
            else:
                obj = m_TestCase(case_number=info['case_number'], case_name=info['case_name'],case_type=info['case_type'],priority=info['priority'],pre_condition=info['pre_condition'],test_range=info['test_range'],test_steps=info['test_steps'],expect_result=info['expect_result'],auto=info['auto'],case_id=info['api_related'], fun_developer=info['fun_developer'], case_designer=info['case_designer'],case_executor=info['case_executor'],test_time=info['test_time'], test_result=info['test_result'],project_id=info['project'],module=info['module']['name'],remark=info['remark'])
                obj.save()  
        messages.success(request,"操作成功")

    module_list = list(set(list(m_TestCase.objects.filter(project_id=project).values_list("module"))))
    modules = []
    for item in module_list:
        modules.append(item[0])
    return redirect("/%s/case/%s" %(project, modules[0]))

@api_view(['POST'])
def case_xmindimport(request, project):
    if request.method == "POST":    # 请求方法为POST时，进行处理  
        upload_file =request.FILES.get("action", None)    # 获取上传的文件，如果没有文件，则默认为None  
        if not upload_file:  
            return HttpResponse("请先上传文件……")
        file_path = os.path.join(settings.MEDIA_ROOT,upload_file.name) 
        destination = open(file_path,'wb+')    # 打开特定的文件进行二进制的写操作  
        for chunk in upload_file.chunks():      # 分块写入文件  
            destination.write(chunk)  
        destination.close()  

        t_handle = t_TestCase(project=project, file_name=file_path)
        case_list = t_handle.read_all()
        # print("case_list: ",case_list)
        for info in case_list:
            # print("info: ",info)
            ret_old = list(m_TestCase.objects.filter(case_number=info['case_number']).values())
            if len(ret_old) > 0:
                obj = m_TestCase.objects.filter(case_number=info['case_number']).update(case_name=info['case_name'],case_type=info['case_type'],priority=info['priority'],pre_condition=info['pre_condition'],test_range=info['test_range'],test_steps=info['test_steps'],expect_result=info['expect_result'],auto=info['auto'],case_id=info['api_related'], fun_developer=info['fun_developer'], case_designer=info['case_designer'],case_executor=info['case_executor'],test_time=info['test_time'], test_result=info['test_result'],project_id=info['project'],module=info['module']['name'],remark=info['remark'])
            else:
                obj = m_TestCase(case_number=info['case_number'], case_name=info['case_name'],case_type=info['case_type'],priority=info['priority'],pre_condition=info['pre_condition'],test_range=info['test_range'],test_steps=info['test_steps'],expect_result=info['expect_result'],auto=info['auto'],case_id=info['api_related'], fun_developer=info['fun_developer'], case_designer=info['case_designer'],case_executor=info['case_executor'],test_time=info['test_time'], test_result=info['test_result'],project_id=info['project'],module=info['module']['name'],remark=info['remark'])
                obj.save()  
        messages.success(request,"操作成功")

    module_list = list(set(list(m_TestCase.objects.filter(project_id=project).values_list("module"))))
    modules = []
    for item in module_list:
        modules.append(item[0])
    return redirect("/%s/case/%s" %(project, modules[0]))


@api_view(['POST'])
def case_split(request, project):
    module_def = ["新需求", "new_requirement"]
    if request.method == "POST":
        body = dict(request.POST)
        module_ret = list(set(list(m_TestCase.objects.filter(project_id=project).values_list("module"))))
        modules = []
        module_dict = {}
        for item in module_ret:
            if item[0] not in module_def:
                modules.append(item[0])
        for item in modules:
            case_number_list = list(set(list(m_TestCase.objects.filter(project_id=project, module=item).values_list("case_number"))))
            for num in case_number_list:
                if num[0]:
                    prefix = num[0].split("_")[0]
                    if prefix not in module_dict:
                        module_dict[prefix] = item
        for item in module_def:
            ret_old = list(m_TestCase.objects.filter(module=item).values())
            if len(ret_old) > 0:
                for info in ret_old:
                    case_prefix = info["case_number"].split("_")[0]
                    if case_prefix in module_dict:
                        obj = m_TestCase.objects.filter(case_number=info['case_number'], project=project).update(module=module_dict[case_prefix])
        messages.success(request,"操作成功")
    return redirect("/%s/case/%s" %(project, modules[0]))
                
@api_view(['GET'])
def gitlab_repo(request, project):
    ret_list = Product_Gitlab.objects.filter(project_id=project).values()
    return render(request, "gitlab_repo.html", {"transList": ret_list, "project":project})

@api_view(["GET",'POST'])
def issue_sync(request, project):
    if request.method == "POST":
        body = dict(request.POST)
        repo = request.POST.get('repo')
        product = request.POST.get('product_id')
        rss_token = request.POST.get('rss_token')
        milestone = request.POST.get('milestone')
        issue_start(project, repo, product, rss_token, milestone)
    ret_list = Issue_Info.objects.filter(project_id=project).values()
    return render(request, "issue_list.html", {"transList": ret_list, "project":project})

@api_view(['POST'])
def report_all(request, project):
    ret_list = Product_Gitlab.objects.filter(project_id=project).values()
    return render(request, "gitlab_repo.html", {"transList": ret_list, "project": project})

@api_view(['POST'])
def report_ms(request, project, product,milestone):
    ret_list = Product_Gitlab.objects.filter(project_id=project, product_id=product, milestone=milestone).values()
    if len(ret_list) > 0:
        ms_info = ret_list[0]
        issue_start(project, repo, product, rss_token, milestone)
    else:
        messages.error(request,"请先录入对应版本信息")

    return render(request, "gitlab_repo.html", {"transList": ret_list})

@api_view(['POST'])
def test_plan_schedule(request, project):
    if request.method == "POST":
        body = dict(request.POST)
        create_gantt(project, body['milestone'][0])
    return render(request, "test_plan_schedule.html")
