"""CaseMgmt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from AutoModel import views as auto_views
from CaseModel import views as case_views
 
urlpatterns = [
    # 登录页面
    url(r'^admin/', admin.site.urls),

    # 首页
    url(r'^$', auto_views.host),
    url(r'^host/', auto_views.host),
    url(r'^host_remove/', auto_views.host_remove),

    # # api信息
    url(r'^(?P<project>\w+)/api/', include('AutoModel.urls')),
    
    # test用例信息
    url(r'^(?P<project>\w+)/case/', include('CaseModel.urls')),
]