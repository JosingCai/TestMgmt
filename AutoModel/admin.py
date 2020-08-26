from django.contrib import admin
from AutoModel.models import Host, Dependency, Result, Source, TestDetail, ComVar
 
# Register your models here.

class Result_List(admin.ModelAdmin):
    list_display = ('case_id', 'requestVars','result', 'outVars','project') # list
    search_fields = ('case_id', 'requestVars','result', 'outVars')
    list_per_page = 100
    list_filter = ['project','result']

class Source_List(admin.ModelAdmin):
    list_display = ('case_id', 'APIFunction','protocol', 'http_method', 'path', 'header', 'pathVar', 'queryParam', 'body', 'response') # list
    search_fields = ('case_id', 'APIFunction','protocol', 'http_method', 'path', 'header', 'pathVar', 'queryParam', 'body', 'response')
    list_per_page = 40

class ComVar_List(admin.ModelAdmin):
    list_display = ('name', 'value','project') # list
    search_fields = ('name', 'value')
    list_per_page = 100
    list_filter = ['project']

class TestDetail_List(admin.ModelAdmin):
    list_display = ('case_id', 'APIFunction','url', 'body', 'response', 'failReason', 'testTime', 'testResult', 'project') # list
    search_fields = ('case_id', 'APIFunction','url', 'body', 'response', 'failReason', 'testTime', 'testResult')
    list_per_page = 100
    list_filter = ['project', 'testResult', 'case_id']

class Host_List(admin.ModelAdmin):
    list_display = ('project_id','ip', 'protocol', 'auth', 'prepath', 'testmode','debug', 'threading', 'usermode') # list
    search_fields = ('project_id','ip', 'protocol', 'auth', 'prepath', 'debug', 'threading', 'usermode')
    list_per_page = 10


class Dependency_List(admin.ModelAdmin):
    list_display = ('case_id','beforeCase', 'afterCase', 'outVars', 'chkVars', 'runNum', 'param_def','raw','project') # list
    search_fields = ('case_id','raw', 'beforeCase', 'afterCase', 'outVars', 'chkVars', 'runNum')
    list_per_page = 100
    list_filter = ['runNum','project']

admin.site.register(Host,Host_List)
admin.site.register(Dependency,Dependency_List)
admin.site.register(Result,Result_List)
admin.site.register(Source,Source_List)
admin.site.register(ComVar,ComVar_List)
admin.site.register(TestDetail,TestDetail_List)

admin.site.site_title = "TestMgmt"
admin.site.site_header = "TestMgmt"
admin.site.index_title = "管理首页"