from django.shortcuts import render,HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
import random,datetime,time,hashlib
from Buyers.models import *
from Shops.models import *
from EarphoneMall.settings import EMAIL_HOST_USER

#COOKIE验证装饰器
def cookieVerify(fun):
    def inner(request,*args,**kwargs):
        username = request.COOKIES.get("username")
        session = request.session.get("username") #获取session
        user = Buyer.objects.filter(username = username).first()
        if user and session == username: #校验session
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect("/login/")
    return inner

#加密函数
def lockpw(pw):
    md5 = hashlib.md5()
    md5.update(pw.encode())
    result = md5.hexdigest()
    return result

#导航页
def daohang(request):
    return render(request,'buyers/daohang.html',locals())


#首页
def index(request):
    return render(request,'buyers/index.html',locals())

#随机验证码函数
def getRandomData():
    result = str(random.randint(1000,9999))
    return result


#发送邮件函数
def sendMessage(request):
    result = {"status": "error","data":""}
    if request.method=='GET' and request.GET:
        receiver = request.GET.get('email')
        try:
            subject = "耳机商城的邮件"
            text_content = ""
            value = getRandomData()
            html_content = """
            <div>
                <p>
                    尊敬的耳机商城用户，您的用户验证码是:%s,打死不要告诉别人。
                </p>
            </div>
            """%value
            message = EmailMultiAlternatives(subject,text_content,EMAIL_HOST_USER,[receiver])
            message.attach_alternative(html_content,"text/html")
            message.send()
        except Exception as e:
            result["data"] = str(e)
        else:
            result["status"] = "success"
            result["data"] = "验证码已发送"
            e = EmailValid()
            e.email_address = receiver
            e.value = value
            e.times = datetime.datetime.now()
            e.save()
        finally:
            return JsonResponse(result)

#注册页面
def register(request):
    result = {"status": "error", "data": ""}
    if request.method == 'POST' and request.POST:
        email = request.POST.get('email')
        username = request.POST.get('username')
        massage = request.POST.get('massage')
        pwd = request.POST.get('password')
        db_email = EmailValid.objects.filter(email_address=email).first()
        if db_email:
            if massage == db_email.value:
                now = time.mktime(
                    datetime.datetime.now().timetuple()
                )
                db_now = time.mktime(db_email.times.timetuple())
                if now - db_now > 86400:
                    result['data'] = '验证码过期'
                    db_email.delete()
                else:
                    b = Buyer()
                    b.username = username
                    b.email = email
                    b.password = lockpw(pwd)
                    b.save()
                    db_email.delete()
                    return HttpResponseRedirect('/login/')
            else:
                result['data'] = '验证码错误'
        else:
            result['data'] = '邮箱不匹配'
    return render(request, 'buyers/register.html', locals())

#登陆
def login(request):
    result = {'statue': 'error', 'data': ''}
    if request.POST and request.method == 'POST':
        email = request.POST.get('email')
        user = Buyer.objects.filter(email=email).first()
        if user:
            pwd = lockpw(request.POST.get('password'))
            if pwd == user.password:
                response = HttpResponseRedirect('/index/') #跳转到首页
                response.set_cookie('user_id', user.id, max_age=3600) #下发cookie
                response.set_cookie('username', user.username, max_age=3600) #下发cookie
                request.session['username'] = user.username #上传session
                return response
            else:
                result['data'] = '密码错误'
        else:
            result['data'] = '用户名不存在'
    return render(request, 'buyers/login.html', locals())

#登出
def logout(request):
    response = HttpResponseRedirect('/index/') #登出后跳转至首页
    response.delete_cookie("user_id") #删除cookie
    response.delete_cookie('username')
    del request.session["username"] #删除session
    return response

#商品列表
def products(request,num):
    num = int(num)
    if num == 0:
        type = {'label':'全部耳机','description':'所有商品，尽情挑选，蓝牙、头戴、入耳、线材应有尽有'}
        goods = Goods.objects.all()
    else:
        type = Types.objects.filter(id=num).first() #取出这个类型的详情
        goods = Goods.objects.filter(types=num)  #取出这个类型的全部商品
    data = []
    for i in goods:
        img = i.image_set.first().img_path  #取出商品的第一张图片路径
        data.append({'img':img,'goods':i})  #将每个商品图片和信息的字典写到data列表中
    return render(request,'buyers/products.html',{'data':data,'type':type})

#商品详情页
def product_details(request,id):
    id = int(id)
    goods = Goods.objects.get(id=id)
    imgs = goods.image_set.all()
    showGoods = Goods.objects.all().order_by('-goods_now_price')[0:3]
    data = []
    for i in showGoods:
        img = i.image_set.first().img_path  # 取出商品的第一张图片路径
        data.append({'img': img, 'goods': i})  # 将每个商品图片和信息的字典写到data列表中
    return render(request,'buyers/product-details.html',locals())


#购物车添加ajax
def addCart(request,id):
    result = {'data': ''}
    id = int(id)
    goods = Goods.objects.get(id=id)
    userId = request.COOKIES.get('user_id')
    if not userId: #如果未登陆
        result['data'] = 0
        return JsonResponse(result)
    else: #如果以登陆
        if request.GET and request.method == 'GET':
            count = request.GET.get('count')
            buyCar = BuyCar.objects.filter(user=userId, goods_id=id).first()
            if buyCar:
                buyCar.goods_num += int(count)
                buyCar.save()
            else:
                buyCar = BuyCar()
                buyCar.goods_id = goods.id
                buyCar.goods_name = goods.goods_name
                buyCar.goods_price = goods.goods_now_price
                buyCar.goods_picture = goods.image_set.first().img_path
                buyCar.goods_num = int(count)
                buyCar.user = Buyer.objects.get(id=userId)
                buyCar.save()
            result['data'] = 1
        return JsonResponse(result)

#购物车
@cookieVerify
def cart(request,num):
    num = int(num)
    if num != 0:
        ordergoods = OrderGoods.objects.filter(order=num)
        ordergoods.delete()
        order = Order.objects.get(id=num)
        address = order.order_address_id
        order.delete()
        db_address = Address.objects.get(id=address)
        db_address.delete()

    userId = request.COOKIES.get('user_id')
    buycarGoos = BuyCar.objects.filter(user=userId)
    alltotal = 0
    data = []
    for i in buycarGoos:
        goods = Goods.objects.get(id=i.goods_id)
        total = i.goods_num * i.goods_price
        alltotal += total
        data.append({'total': total, 'goods': i, 'js': goods.goods_id})

    return render(request,'buyers/cart.html',locals())

#删除购物车函数
@cookieVerify
def delete_car_goods(request,id):
    userId = request.COOKIES.get('user_id')
    goods = BuyCar.objects.filter(user=int(userId),id=int(id))
    goods.delete()
    return HttpResponseRedirect("/buyers/cart/")

#确认订单
@cookieVerify
def enterorder(request):
    alltotal = 0
    data = []
    userId = request.COOKIES.get('user_id')
    if request.method == 'POST' and request.POST:
        countLIST = request.POST.getlist('quantity')
        for i in range(0,len(countLIST)):
            buycar = BuyCar.objects.filter(user=userId)[i]
            buycar.goods_num = countLIST[i]
            buycar.save()
            total = int(buycar.goods_price)*int(buycar.goods_num)
            data.append({'total':total,'goods':buycar})
            alltotal += total
    return render(request,'buyers/enterorder.html',locals())

#确认支付
def enterpay(request):
    if request.POST and request.method == 'POST':
        alltotal = 0
        goods_list = []
        userId = request.COOKIES.get('user_id')

        #取出购物车中用户确定要购买的商品
        buycar = BuyCar.objects.filter(user=userId)
        for goods in buycar:
            total = int(goods.goods_price) * int(goods.goods_num)
            goods_list.append({'total': total, 'goods': goods})
            alltotal += total

        #把地址存入地址表
        address = Address()
        address.address = request.POST.get('address')
        address.username = request.POST.get('name')
        address.phone = request.POST.get('phone')
        address.buyer = Buyer.objects.get(id = userId)
        address.save()

        #在订单表中生成订单
        order = Order()
        # 订单编号 日期(年月日时分秒) + 随机 + 用户id
        now = datetime.datetime.now()
        order.order_num = now.strftime("%Y%m%d%H%M%S") + str(random.randint(10000, 99999)) + userId
        # 状态 未支付 1 支付成功 2 配送中 3 交易完成 4 已取消 0
        order.order_time = now
        order.order_statue = 1
        order.total = alltotal
        order.user = Buyer.objects.get(id = userId)
        order.order_address = address
        order.save()

        #订单商品
        for good in goods_list: #循环保存订单当中的商品
            g = good["goods"]
            g_o = OrderGoods()
            g_o.good_id = g.goods_id
            g_o.good_name = g.goods_name
            g_o.good_price = g.goods_price
            g_o.good_num = g.goods_num
            g_o.goods_picture = g.goods_picture
            g_o.order = order
            g_o.save()
    return render(request,'buyers/enterpay.html',locals())

#支付跳转函数
from alipay import AliPay
def paydata(order_num,count):
    alipay_public_key_string = '''-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArl5uPfSOBWUyLKRVaOSppfvisqHaVkRhkqvVLDph6GCIVGfhYj3XPXzIriKhs7rx0492Z6xMaDqKQrfvMVt+MobEuqEP81e2Yn8uapG0xaT6zNhOmTLHoqhlytzM1XFdz9PMgAK2HIrSUgclwn7RTN0YkTpZbuYj2928UL9x+bQOvzA4Ccyt28WVRxDOgFrxhfZGoEoobchWlwS9O0w8JsqPhP8udVL8tlSO/qUKvqwVYbmhCj4cneLQM9KcYg75AXb+pniJnP7+jnXnCjH+vn3E5sGQSJHPrS6rPDEFvsxU9dbWjNPP02agTUE+2qxHgmIoS8HkSmDYds3yvSUDmQIDAQAB
    -----END PUBLIC KEY-----'''

    app_private_key_string = '''-----BEGIN RSA PRIVATE KEY-----
    MIIEpQIBAAKCAQEArl5uPfSOBWUyLKRVaOSppfvisqHaVkRhkqvVLDph6GCIVGfhYj3XPXzIriKhs7rx0492Z6xMaDqKQrfvMVt+MobEuqEP81e2Yn8uapG0xaT6zNhOmTLHoqhlytzM1XFdz9PMgAK2HIrSUgclwn7RTN0YkTpZbuYj2928UL9x+bQOvzA4Ccyt28WVRxDOgFrxhfZGoEoobchWlwS9O0w8JsqPhP8udVL8tlSO/qUKvqwVYbmhCj4cneLQM9KcYg75AXb+pniJnP7+jnXnCjH+vn3E5sGQSJHPrS6rPDEFvsxU9dbWjNPP02agTUE+2qxHgmIoS8HkSmDYds3yvSUDmQIDAQABAoIBAH85BQSNT6YeHMq3qF2dIS6rJs+hChYRVIPYffQEMPWEoVO8a5TrfAUv65gqSoNBbjonHYQtEZ6mv8RIQexoTh59eEKXS3UIVVluZCZ7Y0MlyZv2YvqiM0i5x3OJQKanTYRai4YG9GrE2wngjytmrj1/v/IOebxRjG5aTZE47eb6xctkLxlzuIJ8JYY7Dw0mDhEH4UEp5lUflIYiwmfocU8QlbKV7VIe47TEbTGi7z/HPQgTzK371KqhKHhWiEwuzt/oRWf+RYnxaKda5LeaXVZeaQ/z1VNNIBRaxFE2gWId2Mtw7liOxaYXRKT+yGuPpHKx1caSuSPeOgsB9BJR0kUCgYEA1GXxHwsPaHnoWOSXA+qTLoDDbP1ZH7sDsPsstZDzt3kQPWxMqUQQqrVVK7rCCk/O1NMCxnwB2oCw8NVIqOd6PyJHj7SRkUFZp9PDfbNjrIA+mOTORKOzLOGjeOkuHr3hi/T4BIjf5Sev9DZHTJIHrTqoIff7BGhLlwsrdaOY2UsCgYEA0inznNEhupiXjo1KuD9VNOIfBhElxWQS7Qd8F7DiLY3uuBQ7/SdMyw3MNiYaaIAs+G98nfPPKriX8k2GT/+YG/xumF2NO7I80zy7KLuYWFprZZnsHVgYNUKgvebfO4Zxkk7ZYdHbcDGh8Edri5jbmKU+jdxHUrfBHdfzoow7DCsCgYEAsMIVpAwESqIJZtD1jGDPE8g82psMbIeqTsL5NjDnYizyAuv58HOgmzBFLRtDGGnKavsgOCZDNKAcoJAe49GfvqK8gy92ZTfJcQ2ehyGfNZOUhJEFx8Gj/xnYfWsw4oyLA3peXQe7rG0W1VnGhEaS9Or3uS0yTTyui4jUJhZ7wXkCgYEAt2wh0CW+GEsBS0sJgZDU3tjTVso0eviChBjaNxsL69JKHKKcUK+yGC4sor3Soo3rsdArpPebQZ/mDXWX2c4rhZFlPNm5X/aJm5sPhddkeQhBX2Vda6btSd6ix9rtzdfi21yx4Ov1ZxAKU9khha6dSbY+yDUOkqUJiPBnFODq0A0CgYEAt4BFldNtyCyxcXG4atS2P1reQZGRyFDtYB99YJthI8qi9XtUfVFuxORJIPKetc9/0UNbpNOfLlwxo3EAmFn1npl/DsG4UdMM35J7u/OjMkzx2bhObuHcImZNVnswv5T+IRRb2Gw24IsYT954LaJVec7vbwNN0BZVcQwEcN29W2g=
    -----END RSA PRIVATE KEY-----'''

    alipay = AliPay(
        appid="2016092400585866",  # 支付宝app的id
        app_notify_url=None,  # 回调视图
        app_private_key_string=app_private_key_string,  # 私钥字符
        alipay_public_key_string=alipay_public_key_string,  # 公钥字符
        sign_type="RSA2",  # 加密方法
    )

    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=str(order_num),
        total_amount=str(count),  #将Decimal类型转换为字符串交给支付宝
        subject="商贸商城",
        return_url='/index/',
        notify_url=None  # 可选, 不填则使用默认notify url
    )
    return  "https://openapi.alipaydev.com/gateway.do?" + order_string

#支付
def payVerify(request,num):
    order = Order.objects.get(id=int(num))
    order_num = order.order_num
    order_count = order.total
    url = paydata(order_num,order_count)
    return HttpResponseRedirect(url)



#404
# def page_not_found(request):
#     return render_to_response('buyer/404.html')