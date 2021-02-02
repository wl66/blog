from django.shortcuts import render, HttpResponse, redirect
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO  # 内存管理工具
from django.http import JsonResponse
from django.contrib import auth
from blog.myforms import Userform
from blog.models import UserInfo
from blog import models
from django.db.models.functions import TruncDay
from django.db.models import Count
import json
from django.db.models import F,Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
import datetime
import random

#登录界面
def login(request):
    # 验证用户名，密码，图片验证码
    if request.method == 'POST':
        response = {"user": None, "msg": None}
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        valid_code = request.POST.get("valid_code").strip()

        yzm_str = request.session.get("yzm_str")
        if valid_code.upper() == yzm_str.upper():
            user = auth.authenticate(username=user, password=pwd)
            if user:
                auth.login(request, user)
                response['user'] = user.username
            else:
                response['msg'] = '用户名或密码错误'
        else:
            response['msg'] = '验证码错误'
        return JsonResponse(response)
    return render(request, 'login.html')

    return render(request,'nrp.html')
# 验证码图片
def get_img(request):
    # 随机颜色
    def get_color():
        rgb_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        if rgb_color == (0, 0, 0):
            get_img()
        else:
            return rgb_color

    # 生成图片 图片存储到内存
    img = Image.new('RGB', (220, 34), color=get_color())
    # f=open('valid_code.png','wb')  图片存到磁盘
    # img.save(f,'png')
    # f=open('valid_code.png','rb')
    # data=f.read()
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('static/fonts/FZSJ-AINDXMM.TTF', size=25)
    yzm_str = ""
    for i in range(0, 4):
        num = str(random.randint(0, 9))
        low_zm = chr(random.randint(97, 122))
        upper_zm = chr(random.randint(65, 90))
        random_char = random.choice([num, low_zm, upper_zm])
        draw.text((i * 20 + 40, 2), random_char, "white", font=font)
        # 保存验证码字符串
        yzm_str += random_char
    print('验证码字符串', yzm_str)
    # 将验证码字符串存到缓存中
    request.session["yzm_str"] = yzm_str
    # 添加噪点噪线
    width = 150
    height = 34
    for i in range(10):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=get_color())
    for i in range(50):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        draw.line((x1, y1), fill=get_color())
        draw.arc((x2, y2, x2 + 4, y2 + 4), 0, 90, fill=get_color())

    f = BytesIO()
    img.save(f, 'png')
    data = f.getvalue()
    return HttpResponse(data)

# 注册界面
def register(request):
    if request.method == 'POST':
        form = Userform(request.POST)
        response = {"user": None, "msg": None}
        if form.is_valid():
            response["user"] = form.cleaned_data.get("user")
            user = form.cleaned_data.get('user')
            pwd = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            avatar_obj = request.FILES.get('avatar')
            extra = {}
            if avatar_obj:
                extra["avatar"] = avatar_obj
                UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)
        else:
            response["msg"] = form.errors
        return JsonResponse(response)
    form = Userform()
    return render(request, 'register.html', {"form": form})

# 注销
def logout(request):
    auth.logout(request)
    return redirect('/login/')

# 首页
def index(request):
    article_list=models.Article.objects.all()
    cur=datetime.datetime.now()
    riqi={'0':'星期一','1':'星期二','2':'星期三','3':'星期四','4':'星期五','5':'星期六','6':'星期日'}
    today = riqi[str(cur.weekday())]
    return render(request, 'index.html',{"article_list":article_list,'cur':cur,'today':today})

# 个人博客
def home_site(request,username,**kwargs):
    user=UserInfo.objects.filter(username=username).first()
    if  not user:
        return render(request,'404.html')
    else:
        # 查询当前站点对象
        blog=user.blog
        if kwargs:
            condition=kwargs.get("condition")
            param=kwargs.get("param")
            if condition=="category":
                article_object = models.Article.objects.filter(user=user).filter(category__title=param)
            elif condition=='tag':
                article_object=models.Article.objects.filter(user=user).filter(tags__title=param)
            else:
                year,month,day=param.split('-')
                article_object = models.Article.objects.filter(user=user).filter(create_time__year=year,create_time__month=month,create_time__day=day)
        else:
            # 查询当前用户对应的所有文章
            article_object=user.article_set.all()

        # 查询当前用户的每一个分类名称以及对应的文章数
        article_list=models.Category.objects.filter(bolg=blog).values("pk").annotate(c=Count("article__title")).values_list("title","c")

        # 查询当前用户的每一个标签名称以及对应的文章数
        tag_list= models.Tag.objects.filter(bolg=blog).values("pk").annotate(c=Count("article")).values_list("title","c")

        # 查询当前用户每一个年月日的名称以及对应的文章数
        # date_list=models.Article.objects.filter(user=user).extra(select={"riqi":"date_formate(create_time,'%%Y-%%m-%%d')"}).values("riqi").annotate(c=Count("nid")).values("riqi","c")
        date_list=models.Article.objects.filter(user=user).annotate(day=TruncDay('create_time')).values('day').annotate(c=Count("nid")).values_list("day","c")
        return render(request,"home_site.html",{"blog":blog,"article_list":article_list,"tag_list":tag_list,"date_list":date_list,"article_object":article_object,"username":username})

# 文章详情页
def article_detail(request,username,article_id):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    article_list = models.Category.objects.filter(bolg=blog).values("pk").annotate(c=Count("article__title")).values_list("title", "c")
    tag_list = models.Tag.objects.filter(bolg=blog).values("pk").annotate(c=Count("article")).values_list("title", "c")
    date_list = models.Article.objects.filter(user=user).annotate(day=TruncDay('create_time')).values('day').annotate(c=Count("nid")).values_list("day", "c")
    article_obj=models.Article.objects.filter(user=user).filter(pk=article_id).first()
    ArticleUpDown_obj=models.ArticleUpDown.objects.filter(article_id=article_id,user_id=user.pk).first()
    comment_list=models.Comment.objects.filter(article_id=article_id,parent_comment_id=None)
    return  render(request,'article_detail.html',locals())

# 点赞
@login_required
def digg(request):
    article_id=request.POST.get("article_id")
    user_id = request.user.pk
    queryset = models.Article.objects.filter(pk=article_id)
    up_down = models.ArticleUpDown.objects.filter(article_id=article_id, user_id=user_id)
    if not up_down:
        models.ArticleUpDown.objects.create(user_id=user_id,article_id=article_id,is_up=True)
        queryset.update(up_count=F("up_count")+1)
    else:
        up_down__zt = up_down.first().is_up
        if up_down__zt:
            queryset.update(up_count=F("up_count") - 1)
            up_down.update(is_up=False)
        else:
            queryset.update(up_count=F("up_count") + 1)
            up_down.update(is_up=True)
    data=queryset.first().up_count
    return JsonResponse({'data':data})

# 写评论
@login_required
def comment(request):
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    pid=request.POST.get("pid")
    user=request.user.pk
    with transaction.atomic():
        comment_obj=models.Comment.objects.create(user_id=user,article_id=article_id,content=content, parent_comment_id=pid)
        models.Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)
    response={}
    response["create_time"]=comment_obj.create_time.strftime("%Y-%m-%d %X")
    response["username"]=request.user.username
    response["content"]=content
    response["pid"] = pid
    return JsonResponse(response)

# 展示评论：评论树
def get_comment_tree(request):
    article_id=request.GET.get("article_id")
    rets=models.Comment.objects.filter(Q(article_id=article_id)&(~Q(parent_comment_id=None)))
    listk=[]
    for ret in rets:
        response={}
        response["create_time"] = ret.create_time.strftime("%Y-%m-%d %X")
        response["username"] = ret.user.username
        response["content"] = ret.content
        response["pk"] = ret.pk
        response['parent_comment_id']=ret.parent_comment_id
        listk.append(response)
    return JsonResponse(listk,safe=False)

@login_required
# 个人后台管理首页
def myadmin(request):
    return render(request,'myadmin.html')

# 后台文章的增删改查
def way(request,way,pk):
    if way=='show':
        user = request.user.pk
        ret = models.Article.objects.filter(user=user).all()
        return render(request, 'show.html', {"ret": ret})
    elif way=='delete':
        article_pk=request.GET.get('article_pk')
        models.Article.objects.filter(pk=article_pk).delete()
        return HttpResponse('ok')
    else:
         if request.method=='GET':
             username = request.user.username
             user = UserInfo.objects.filter(username=username).first()
             blog = user.blog
             category_list = models.Category.objects.filter(bolg=blog).all()
             if way == 'update':
                 ret=models.Article.objects.filter(pk=pk).first()
                 return render(request,'update.html',{"ret":ret,'category_list':category_list})
             else:
                 return render(request, 'create.html', {'category_list': category_list})
         else:
             title = request.POST.get('title')
             desc = request.POST.get('desc')
             content = request.POST.get('content')
             create_time = request.POST.get('create_time')
             category_name = request.POST.get('category')
             ret = models.Category.objects.filter(title=category_name).values('pk')
             for i in ret:
                 category_id = i['pk']
                 if way == 'update':
                     models.Article.objects.filter(pk=pk).update(title=title,desc=desc,content=content,create_time=create_time,category_id=category_id)
                 else:
                     models.Article.objects.create(title=title, user_id=request.user.pk, desc=desc, content=content,create_time=create_time, category_id=category_id)
             return HttpResponse("成功!")





