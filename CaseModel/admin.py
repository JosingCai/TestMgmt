from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from CaseModel.models import TestCase, ProductDir,Product_Gitlab,Issue_Milestone_Count,Issue_Tag_Count,Issue_Info,Test_Plan_Schedule

# Register your models here.
class TestCase_List(admin.ModelAdmin):
    #list_display = ('case_number','project_id','module', 'case_name','case_type', 'priority', 'pre_condition', 'test_range', 'test_steps', 'expect_result', 'auto', 'case_id', 'fun_developer', 'case_designer', 'case_executor', 'test_time', 'test_result', 'remark') # list
    list_display = ('case_number','module', 'case_name','case_type', 'priority', 'test_steps', 'expect_result','fun_developer', 'test_time', 'test_result') # list
    search_fields = ('case_number','module', 'case_name','case_type', 'priority', 'pre_condition', 'test_range', 'test_steps', 'expect_result', 'auto', 'fun_developer', 'case_designer', 'case_executor', 'test_time', 'test_result', 'remark')
    #list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 10
    list_filter = ['project_id','module', 'test_result'] 
    #ordering设置默认排序字段，负号表示降序排序
    #list_editable 设置默认可编辑字段
    list_editable = ['case_type', 'priority', 'test_result','fun_developer']
    #fk_fields 设置显示外键字段
    #list_display_links设置哪些字段可以点击进入编辑界面
    list_display_links = ['case_number','test_steps', 'expect_result']

    def patch_init(self, reqquest, queryset):
        queryset.update(priority="Level5", test_result="FAIL")

    patch_init.short_description = '修改所选'
    actions = [patch_init]

class ProductDir_List(admin.ModelAdmin):
    list_display = ('pid', 'name_cn', 'name_en','remark') # list
    search_fields = ('pid', 'name_cn', 'name_en','remark')

class Product_Gitlab_List(admin.ModelAdmin):
    list_display = ('repo','product_id', 'rss_token','milestone', 'project_id','remark') # list
    search_fields = ('repo','product_id', 'rss_token','milestone','remark')
    list_per_page = 10
    list_filter = ['project_id','product_id','milestone'] 
    #list_editable = ['product_id', 'milestone']
    list_display_links = ['product_id', 'milestone']

class Issue_Milestone_Count_List(admin.ModelAdmin):
    list_display = ('product','milestone', 'all_count','open_count', 'closed_count','project_id','remark') # list
    search_fields = ('product','milestone', 'all_count','open_count', 'closed_count','remark')
    list_per_page = 10
    list_filter = ['project_id','product','milestone'] 
    #list_editable = ['product','milestone']
    list_display_links = ['product','milestone']

class Issue_Tag_Count_List(admin.ModelAdmin):
    list_display = ('product','milestone', 'tag', 'all_count','open_count', 'closed_count','project_id','remark') # list
    search_fields = ('product','milestone', 'tag','all_count','open_count', 'closed_count','remark')
    list_per_page = 10
    list_filter = ['project','product','milestone'] 
    #list_editable = ['product','milestone']
    list_display_links = ['product','milestone']

class Issue_Info_List(admin.ModelAdmin):
    list_display = ('issue_id', 'product','milestone', 'issue_type','name', 'author','assignees','test', 'updated', 'result','reopen','tag', 'project') # list
    search_fields = ('issue_id', 'issue_type','name','result','reopen','tag')
    list_per_page = 10
    list_filter = ['project_id','product','milestone', 'issue_type', 'result','reopen'] 
    #list_editable = ['product','milestone']
    list_display_links = ['issue_id', 'product','milestone']

class TestPlanSchecdule_Info_List(admin.ModelAdmin):
    list_display = ('task_id','p_start_time', 'p_finish_time','a_start_time', 'a_finish_time','progress','priority', 'executor', 'milestone', 'project') # list
    search_fields = ('task_id', 'priority', 'executor', 'project')
    list_per_page = 10
    list_filter = ['priority','executor','milestone', 'project'] 
    list_editable = ['priority','executor','milestone','p_start_time', 'p_finish_time','a_start_time', 'a_finish_time','progress']
    list_display_links = ['task_id'] 
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'20'})},
    #    models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }


admin.site.register(TestCase,TestCase_List)
admin.site.register(ProductDir,ProductDir_List)
admin.site.register(Product_Gitlab, Product_Gitlab_List)
admin.site.register(Issue_Milestone_Count, Issue_Milestone_Count_List)
admin.site.register(Issue_Tag_Count,Issue_Tag_Count_List)
admin.site.register(Issue_Info,Issue_Info_List)
admin.site.register(Test_Plan_Schedule,TestPlanSchecdule_Info_List)


admin.site.site_title = "TestMgmt"
admin.site.site_header = "TestMgmt"
admin.site.index_title = "管理首页"