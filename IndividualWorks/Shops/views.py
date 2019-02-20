from django.shortcuts import render,HttpResponseRedirect
import hashlib,os
from Shops.models import *
from EarphoneMall.settings import MEDIA_ROOT


#加密函数
def lockpw(pw):
    md5 = hashlib.md5()
    md5.update(pw.encode())
    result = md5.hexdigest()
    return result

#cookie验证装饰器
def cookieVerify(fun):
    def inner(request,*args,**kwargs):
        username = request.COOKIES.get("username") #获取cookies中的username
        session = request.session.get("nickname")  # 获取session中的username
        db_user = Seller.objects.filter(username=username).first()
        if db_user and db_user.nickname == session:  # 校验session和cookies
            return fun(request, *args, **kwargs) #通过按照原函数返回
        else:
            return HttpResponseRedirect("/shops/login/") #校验失败跳转至登录页
    return inner

#登录页函数
def login(request):
    result = {'status':'error','data':''}  #状态标记，用来返回给前端页面登陆不成功的原因
    if request.method == 'POST' and request.POST: #如果请求方式为POST且有请求内容
        username = request.POST.get('username') #username是前台页面input标签中name属性所写内容
        db_user = Seller.objects.filter(username=username).first() #使用filter的方法取出数据库中字段与前台输入相符的人
        if db_user:  #如果在数据库中取到了，说明有此用户
            db_password = db_user.password  #取该用户储存在数据库的密码
            password = lockpw(request.POST.get('password')) #取该用户页面输入的密码并加密
            if db_password == password:
                #这里要给返回值设置cookie和session，所以需要把返回值先赋值
                response = HttpResponseRedirect('/shops/') #登陆成功跳转至首页
                response.set_cookie('username',db_user.username,max_age=3600) #设置寿命为1小时的cookie
                request.session['nickname'] = db_user.nickname #设置session
                return response
            else: #如果密码不一致
                result['data'] = '密码错误'
        else: #如果取出的用户为空
            result['data'] = '该商家不存在'
    return render(request,'shops/login.html',locals())

#登出函数
def loginout(request):
    response = HttpResponseRedirect('/shops/login/')
    response.delete_cookie('username')
    del request.session['nickname']
    return response


#首页
@cookieVerify
def index(request):
    return render(request,'shops/index.html',locals())

#商品添加页
@cookieVerify
def goodsAdd(request):
    doType = ''
    types = Types.objects.all()
    if request.method == 'POST' and request.POST:
        g = Goods() #实例化数据表
        g.goods_name = request.POST.get('goodsname')
        g.goods_id = request.POST.get('goodsid')
        g.goods_price = request.POST.get('goodsprice')
        g.goods_now_price = request.POST.get('goodsnowprice')
        g.goods_num = request.POST.get('goodsnum')
        g.goods_description = request.POST.get('goodsdescription')
        g.goods_content = request.POST.get('goodscontent')
        g.taobao = request.POST.get('taobao')
        g.types = Types.objects.get(id=int(request.POST.get('goodstypes')))
        g.seller = Seller.objects.get(nickname=request.POST.get('seller'))
        g.save() #保存数据信息
        for i in request.FILES.getlist('goodsimages'):  #把图片循环出来
            img = Image() #实例化图片表
            img.img_path = 'shops/images/goods/'+i.name #name是文件名，内置方法
            img.img_label = request.POST.get('goodsname')
            img.goods = g
            img.save()
            path = os.path.join(MEDIA_ROOT,'shops/images/goods/{}'.format(i.name)).replace('\\','/')
            with open(path, "wb")  as f:  #wb是以二进制打开
                for j in i.chunks():  #解析图片为2进制文件，全部内容写入到静态文件夹。
                    f.write(j)
    return render(request,'shops/goods_add.html',locals())

#商品修改页
@cookieVerify
def goodsChange(request,id):
    doType = 'change'
    types = Types.objects.all()
    g = Goods.objects.get(id=int(id))
    if request.method == 'POST' and request.POST:
        g = Goods.objects.get(id = int(id)) #实例化数据表
        g.goods_name = request.POST.get('goodsname')
        g.goods_id = request.POST.get('goodsid')
        g.goods_price = request.POST.get('goodsprice')
        g.goods_now_price = request.POST.get('goodsnowprice')
        g.goods_num = request.POST.get('goodsnum')
        g.goods_description = request.POST.get('goodsdescription')
        g.goods_content = request.POST.get('goodscontent')
        g.taobao = request.POST.get('taobao')
        g.types = Types.objects.get(id=int(request.POST.get('goodstypes')))
        g.seller = Seller.objects.get(nickname=request.POST.get('seller'))
        g.save() #保存数据信息
        for i in request.FILES.getlist('goodsimages'):  #把图片循环出来
            img = Image.objects.get(goods=g) #实例化图片表
            img.img_path = 'shops/images/goods/'+i.name #name是文件名，内置方法
            img.img_label = request.POST.get('goodsname')
            img.goods = g
            img.save()
            path = os.path.join(MEDIA_ROOT,'shops/images/goods/{}'.format(i.name)).replace('\\','/')
            with open(path, "wb")  as f:  #wb是以二进制打开
                for j in i.chunks():  #解析图片为2进制文件，全部内容写入到静态文件夹。
                    f.write(j)
    return render(request,'shops/goods_add.html',locals())

#商品删除
@cookieVerify
def goodsDel(request,id):
    goods = Goods.objects.get(id=int(id))
    imgs = goods.image_set.all()  #获取商品的所有照片
    for i in imgs:  #删除存在静态文件夹中的图片
        os.remove(os.path.join(MEDIA_ROOT,str(i.img_path).replace('\\','/')))
    imgs.delete() #先删除外键表
    goods.delete()  # 再删除主键表数据
    return HttpResponseRedirect("/shops/goodslist/") #跳转到商品列表页





#商品类型添加页
@cookieVerify
def goodsTypeAdd(request):
    if request.method == 'POST' and request.POST:
        types = Types()
        types.label = request.POST.get('typelabel')
        types.description = request.POST.get('typedescription')
        types.save()
    return render(request, 'shops/goodstype_add.html', locals())

#商品列表页
@cookieVerify
def goodsList(request):
    goods = Goods.objects.all()
    return render(request, 'shops/goods_list.html', locals())

#商品详情页
@cookieVerify
def goodsDetails(request,id):
    goods = Goods.objects.get(id=int(id)) #获取商品信息
    goodsImage = Image.objects.filter(goods=int(id)) #获取商品图片
    return render(request,'shops/goods_details.html',locals())