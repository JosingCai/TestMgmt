from django.conf.urls import url
from CaseModel import views as views

app_name = 'case'
urlpatterns = [
    # case信息
    url(r'xmindimport/', views.case_xmindimport),
    url(r'import/', views.case_import),
    url(r'export/', views.case_export),
    url(r'download/', views.template_download),
    url(r'split/', views.case_split),
    url(r'repo_list/', views.gitlab_repo),
    url(r'repo_issue/', views.issue_sync),
    url(r'test_report/', views.report_all),
    url(r'test_plan/', views.test_plan_schedule),
    url(r'report/(?P<milsestone>\w+)/', views.report_ms),
    url(r'(?P<module>\w+)/', views.test_case),
]   