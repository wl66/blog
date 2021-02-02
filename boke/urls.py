"""boke URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,re_path
from blog import views
from  django.views.static import serve
from boke import settings
urlpatterns = [
    path('admin/', admin.site.urls),

    # 登录url
    path('login/', views.login),
    # 验证码url
    path('get_img/', views.get_img),
    # 注册url
    path('register/', views.register),
    # s首页url
    re_path('^$',views.index),
    path('index/', views.index),
    # 注销url
    path('logout/',views.logout),
    # 文章点赞url
    path('digg/',views.digg),
    # 文章评论url
    path('comment/',views.comment),
    path('get_comment_tree/',views.get_comment_tree),
    # 个人后台管理url
    path('myadmin/',views.myadmin),
    re_path('^(?P<way>delete|update|create|show)/(?P<pk>.*)$',views.way),
    # media配置
    re_path(r"media/(?P<path>.*)$",serve,{"document_root":settings.MEDIA_ROOT}),
    # 个人主页url
    re_path("^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)$",views.home_site),
    re_path("^(?P<username>\w+)$",views.home_site),
    # 文章详情页url
    re_path("^(?P<username>\w+)/articles/(?P<article_id>\d+)$",views.article_detail)
]
