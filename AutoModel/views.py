from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from rest_framework.decorators import api_view
from AutoModel.models import Host, Dependency, Result, Source, TestDetail, ComVar,TestReport
from AutoModel.swagger import AutoSource
from AutoModel.common import raw2dict
from AutoModel.apicase import runTargetAPI,runAPIs
from django.contrib.auth.decorators import login_required

@api_view(['GET', 'POST'])
def host(request):
    if request.method == "POST":
        body = dict(request.POST)
        production = request.POST.get('production')
        ip = request.POST.get('ip')
        protocol = request.POST.get('protocol')
        auth = request.POST.get('auth')
        prepath = request.POST.get('prepath')
        debug = request.POST.get('debug')
        threading = request.POST.get('threading')
        usermode = request.POST.get('usermode')
        dbconfig = request.POST.get('dbconfig')
        token = request.POST.get('token')
        ret_old = list(Host.objects.filter(production=production).values())
        if len(ret_old) > 0:
            obj = Host.objects.filter(production=production).update(ip=ip,protocol=protocol,auth=auth,prepath=prepath,debug=debug,threading=threading,usermode=usermode,dbconfig=dbconfig,token=token)
        else:
            obj = Host(production=production,ip=ip,protocol=protocol,auth=auth,prepath=prepath,debug=debug,threading=threading,usermode=usermode,dbconfig=dbconfig,token=token)
            obj.save()
        messages.success(request,"操作成功")
    ret_list = list(Host.objects.all().values())
    return render(request, "testHost.html", {"transList": ret_list})

@api_view(['GET', 'POST'])
def com_var(request, project):
    if request.method == "POST":
        name = request.POST.get('name')
        value = request.POST.get('value')
        ret_old = list(ComVar.objects.filter(name=name).values())
        if len(ret_old) > 0:
            obj = ComVar.objects.filter(name=name, project=project).update(value=value)
        else:
            obj = ComVar(name=name, project=project,value=value)
            obj.save()
        messages.success(request,"新增成功")
    ret_list = list(ComVar.objects.all().values())
    return render(request, "ComVar.html", {"transList": ret_list, "project": project})

@api_view(['GET', 'POST'])
def case_dep(request, project):
    if request.method == "POST":
        case_id = request.POST.get('case_id')
        runNum = request.POST.get('runNum')
        beforeCase = request.POST.get('beforeCase')
        if len(beforeCase) == 0:
            beforeCase = []
        afterCase = request.POST.get('afterCase')
        if len(afterCase) == 0:
            afterCase = []
        outVars = request.POST.get('outVars')
        if len(outVars) == 0:
            outVars = {}
        chkVars = request.POST.get('chkVars')
        if len(chkVars) == 0:
            chkVars = {}
        param_def = request.POST.get('param_def')
        if len(param_def) == 0:
            param_def = []
        raw = request.POST.get('raw')
        if raw is None:
            raw= ""
        ret_old = list(Dependency.objects.filter(case_id=case_id,project=project).values())
        if len(ret_old) > 0:
            obj = Dependency.objects.filter(case_id=case_id).update(project=project,raw=raw, runNum=runNum, beforeCase=beforeCase, afterCase=afterCase, outVars=outVars, chkVars=chkVars,param_def=param_def)
        else:
            obj = Dependency(case_id=case_id,project=project,raw=raw, runNum=runNum, beforeCase=beforeCase, afterCase=afterCase, outVars=outVars, chkVars=chkVars,param_def=param_def)
            obj.save()
        messages.success(request,"操作成功")
    elif request.method == "GET":
        query_dict = dict(request.query_params)
        if len(query_dict) > 0:
            case_id = list(query_dict.keys())[0]
            ret_list = list(Dependency.objects.filter(case_id=case_id,project=project).values())
        else:
            ret_list = list(Dependency.objects.filter(project=project).values())
    return render(request, "caseDep.html", {"transList": ret_list,"project": project})

@api_view(['POST'])
def case_run(request, project):
    body = dict(request.POST)
    case_id = list(body.keys())[1]
    ret, output = runTargetAPI(module=project, method_API=case_id)
    return render(request, "caseRun.html",{"transList": output,"project": project})

@api_view(['POST'])
def all_case_run(request, project):
    output = runAPIs(project)
    ret_list = list(Dependency.objects.all().values())
    return render(request, "caseRun.html",{"transList": ret_list,"project": project})

@api_view(['POST'])
def dep_remove(request, project):
    body = dict(request.POST)
    case_id = list(body.keys())[1]
    ret = list(Dependency.objects.filter(case_id=case_id,project=project).delete())
    if ret[0] >0 :
        messages.success(request,"操作成功")
    else:
        messages.error(request,"操作失败")
    ret_list = list(Dependency.objects.all().values())
    return render(request, "caseDep.html", {"transList": ret_list,"project": project})

@api_view(['GET'])
def case_result(request, project):
    ret_list = list(Result.objects.filter(project_id=project).values())
    return render(request, "caseResult.html", {"transList": ret_list,"project": project})

@api_view(['GET'])
def result_detail(request, project):
    query_dict = dict(request.query_params)
    if len(query_dict) > 0:
        case_id = list(query_dict.keys())[0]
        ret_list = list(TestDetail.objects.filter(case_id=case_id,project_id=project).values())
    else:
        ret_list = list(TestDetail.objects.filter(project_id=project).values())
    return render(request, "caseResultDetail.html", {"transList": ret_list,"project": project})

@api_view(['GET'])
def case_detail(request, project):
    ret_list = list(Result.objects.filter(project_id=project).values())
    return render(request, "caseAll.html", {"transList": ret_list,"project": project})

@api_view(['GET', "POST"])
def result_report(request, project):
    ret_list = list(TestReport.objects.filter(project_id=project).values())
    return render(request, "testReport.html", {"transList": ret_list,"project": project})

@api_view(['GET', 'POST'])
def source(request, project):
    if request.method == "POST":
        APIFunction = str(request.POST.get('APIFunction'))
        protocol = str(request.POST.get('protocol'))
        http_method = str(request.POST.get('http_method'))
        path = str(request.POST.get('path'))
        header = str(request.POST.get('header'))
        pathVar = str(request.POST.get('pathVar'))
        queryParam = str(request.POST.get('queryParam'))
        body = str(request.POST.get('body'))
        response = str(request.POST.get('response'))
        case_id = "%s_%s" %(http_method, path)
        raw = APIFunction + "|" + protocol + "|" + http_method + "|" + path+ "|" + header + "|" + pathVar + "|" + queryParam + "|" + body + "|" + response
        ret_old = list(Dependency.objects.filter(case_id=case_id,project_id=project).values())
        if len(ret_old) > 0:
            obj = Dependency.objects.filter(case_id=case_id,project_id=project).update(raw=raw)
        else:
            runNum = 1
            beforeCase = []
            afterCase = []
            outVars = {}
            chkVars = {}
            param_def = []
            obj = Dependency(case_id=case_id,project_id=project,raw=raw, runNum=runNum, beforeCase=beforeCase, afterCase=afterCase, outVars=outVars, chkVars=chkVars,param_def=param_def)
            obj.save()
        messages.success(request,"新增成功")
    dependancy_list = list(Dependency.objects.filter(project_id=project).values_list("raw"))
    ret_list = raw2dict(dependancy_list)
    return render(request, "source.html", {"transList": ret_list, "project": project})

@api_view(['POST'])
def source_auto(request, project):
    project = project.upper()
    if request.method == "POST":
        auto_obj = AutoSource(project)
        raw_list = auto_obj.createAutoData()
        change_list = []
        for info in raw_list:
            api_list = info.split("|")
            case_id = "%s_%s" %(api_list[2], api_list[3])
            ret_old = list(Dependency.objects.filter(case_id=case_id,project=project).values())
            change_dict = {}
            if len(ret_old) > 0:
                change_dict["old_raw"] = ret_old[0]['raw'].replace("'", "\"")
                change_dict["section"] = case_id
                change_dict["new_raw"] = info.replace("'", "\"")
                if change_dict["old_raw"] != change_dict["new_raw"]:
                    change_list.append(change_dict)
            else:
                runNum = 1
                beforeCase = []
                afterCase = []
                outVars = {}
                chkVars = {}
                param_def = []
                obj = Dependency(case_id=case_id,project_id=project,raw=info, runNum=runNum, beforeCase=beforeCase, afterCase=afterCase, outVars=outVars, chkVars=chkVars,param_def=param_def)
                obj.save()
        if len(change_list) > 0:
            return render(request, "source_change.html", {"project":project, "transList":change_list})
    return redirect("/%s/api/source/" %project)
    

@api_view(['POST'])
def source_change(request, project):
    project = project.upper()
    if request.method == "POST":
        transList = eval(request.POST.get('value'))
        for info in transList:
            case_id = info['section']
            # ret_old = list(Dependency.objects.filter(case_id=case_id,project_id=project).values())
            # if len(ret_old) >= 0:
            obj = Dependency.objects.filter(case_id=case_id,project_id=project).update(raw=info['new_raw'])
            # else:
            #     runNum = 1
            #     beforeCase = []
            #     afterCase = []
            #     outVars = {}
            #     chkVars = {}
            #     param_def = []
            #     obj = Dependency(case_id=case_id,project_id=project,raw=info["new_raw"], runNum=runNum, beforeCase=beforeCase, afterCase=afterCase, outVars=outVars, chkVars=chkVars,param_def=param_def)
            #     obj.save()
    return redirect("/%s/api/source/" %project)

@api_view(['POST'])
def source_change_one(request, project):
    project = project.upper()
    if request.method == "POST":
        case_id = request.POST.get('section')
        # old_raw = request.POST.get('old_raw')
        new_raw = request.POST.get('new_raw')
        # ret_old = list(Dependency.objects.filter(case_id=case_id,project_id=project).values())
        # if len(ret_old) >= 0:
        obj = Dependency.objects.filter(case_id=case_id,project_id=project).update(raw=new_raw)
        # else:
        #     runNum = 1
        #     beforeCase = []
        #     afterCase = []
        #     outVars = {}
        #     chkVars = {}
        #     param_def = []
        #     obj = Dependency(case_id=case_id,project_id=project,raw=new_raw, runNum=runNum, beforeCase=beforeCase, afterCase=afterCase, outVars=outVars, chkVars=chkVars,param_def=param_def)
        #     obj.save()
    return redirect("/%s/api/source/" %project)
    
@api_view(['POST'])
def host_remove(request):
    info = request.data.get('data')
    inf = request.data
    host_list = list(Host.objects.all().values())
    return render(request, "testHost.html", {"transList": host_list})

def case(request):
    pass

def sync_case_dep(request):
    pass


def login_info(request):
    context = {}
    return render(request, 'index.html', context)

def login(request):
    if request.method == "POST":
        user_name = request.POST.get('form_user_name', '')
        # 对应前端的<input name="form_user_name">
        password = request.POST.get('form_password', '')
        # 对应前端的<input name="form_password">
        user = auth.authenticate(username=user_name, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            request.session['user'] = user_name
            return redirect('/home/')
        else:
            return render(request, 'login.html', {'error': '用户名或密码错误！'})
    return render(request, 'login.html')

@login_required
# 要求用户登录
def home(request):
    return render(request, "home.html")

@login_required
def logout(request):
    auth.logout(request)
    return render(request, 'login.html')
