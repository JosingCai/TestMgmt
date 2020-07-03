from django.conf.urls import url
from AutoModel import views as views

app_name = 'auto'
urlpatterns = [
    # api源信息
    url(r'source/', views.source),
    url(r'source_auto/', views.source_auto),
    url(r'source_change/', views.source_change),
    url(r'source_change_one/', views.source_change_one),

    # api用例信息
    url(r'case_dep/', views.case_dep),
    url(r'case_result/', views.case_result),
    url(r'comVar/', views.com_var),
    url(r'result_detail/', views.result_detail),
    url(r'result_report/', views.result_report),
    url(r'case_detail/', views.case_detail),
    url(r'dep_remove/', views.dep_remove),
    url(r'case_run/', views.case_run),
    url(r'case_run_all/', views.all_case_run),
]