from django.shortcuts import render  # render
import re  # 正则
from django.shortcuts import HttpResponse  #HttpResponse对象
from django.shortcuts import redirect  # 重定向
from django.shortcuts import reverse  # 反转
# from app1.models import *
from django.views.generic import View  #
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from hmsx_sx1 import settings
from itsdangerous import SignatureExpired
from celery_tasks.tasks import send_active_email
from django.contrib.auth import authenticate
from django.contrib.auth import  login
from django.contrib.auth.models import User
from django.core.cache import cache
from send_message import *
from resutful import *
from app1.forms import RegisterFrom
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
import json
# from django.core.mail import send_mail
#注册
info={"confirm":''}
class RegisterView(View):
    def get(self,request):
        '''显示注册页面'''
        return render(request,'register.html')
    def post(self,request):
        '''处理用户注册数据'''
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        if not all([username, password, email]):
            return render(request, 'register.html', {'error_msg': '数据不完整'})
        if not re.match(r"^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            return render(request, 'register.html', {"error_msg": "邮箱格式不正确"})
        if allow != "on":
            return render(request, "register.html", {"error_msg": "请勾选同意"})
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, "register.html", {"error_msg": "用户名已存在"})
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()
        serializer = Serializer(settings.SECRET_KEY, 3600)# 有效期1小时
        info = {"confirm": user.id}
        token = serializer.dumps(info)
        token_=token.decode('utf-8')
        send_active_email.delay(email,username,token_)
#         subject = "海马生鲜欢迎你"  # 邮件标题
#         message = "how are you"  # 邮件正文
#         sender = settings.EMAIL_FROM  # 发件人
#         receiver = [email] # 收件人
#         html_message='''
#      <h1>%s 恭喜您成为海马生鲜注册会员</h1><br/><h3>请您在1小时内点击以下链接进行账户激
#             活</h3><a
#             href="http://127.0.0.1:8000/active/%s">http://127.0.0.1:8000/active/%s</a>
#             ''' % (username, token_, token_)
#         send_mail(subject, message, sender, receiver,html_message=html_message)
        return redirect(reverse("index"))


#账户激活
class ActiveView(View):
    '''激活账户'''
    def get(self,request,token):
        '''进行用户激活'''
        serializer = Serializer(settings.SECRET_KEY, 3600)
        # print('6'*9)
        try:
            info = serializer.loads(token)
            # 获取用户id
            user_id = info['confirm']
            # 根据用户id 获取该用户对象
            user = User.objects.get(id=user_id)
            # 设置该用户对象中的is_active字段的值为1
            user.is_active = 1
            user.save()
            # 使用反向解析跳转到登录页
            return redirect(reverse("login"))
        except SignatureExpired as e:
            # 出现异常表示链接失效
            return HttpResponse("激活链接已过期")



#登录
class LoginView(View):
    def get(self,request):
        '''显示登录页面'''
        register_form = RegisterFrom()
        if 'username' in request.COOKIES:
            username = request.COOKIES.get("username")
            checked = "checked"
        else:
            username = ''
            checked = ''
        return render(request, "login.html", {"username": username, "checked": checked,"register_form":register_form})

    def post(self,request):
        '''登录'''
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        if not all([username, password]):
            return render(request, "login.html", {"error_msg": "数据不完整"})
        user = authenticate(username=username, password=password) # 正确返回user对象，不正确返回None
        if user is not None:
            # 用户名密码正确
            if user.is_active==1:
                # 用户已激活
                # 将用户登录成功后状态保存在session，使用django认证系统中的login方法
                login(request, user)
                # 重定向到主页
                response = redirect(reverse("index"))
                # 判断用户是否记勾选记住用户名
                remember = request.POST.get("remember")
                if remember == "on":
                    # 表示勾选了,将用户名保存在cookie中
                    response.set_cookie("username", username, max_age=7 * 24 * 3600)
                else:
                    # 删除cookie
                    response.delete_cookie("username")
                    # 重定向到主页
                return response
            else:
                # 用户未激活
                return render(request, "login.html", {"error_msg": "账户未激活"})
        else:
            # 用户名或密码错误
            return render(request, "login.html", {"error_msg": "用户名或密码错误"})


#主页面
def index(request):
    '''显示主页面'''
    return render(request,'index.html')

#发送短信接口
def sms_send(request):
    phone = request.GET.get('phone')# 1.获取手机号
    print(phone)
    code = get_code(6, True)#生成6位验证码，调用自己写的方法
    print(code)
    cache.set(phone, code, 60)#缓存到redis数据库,60秒有效期
    # print("789789789")
    #判断缓存中是否有phone
    cache.has_key(phone)
    #获取redis验证码
    cache.get(phone)
    # print("qwerttt")
    result = send_sms(phone, code) #发送短信，调用自己写的方法
    return HttpResponse(result)

#短信验证码验证接口
def sms_check(request):
    # 1.获取电话和手动输入的验证码
    phone = request.GET.get('phone')
    code = request.GET.get('code')
    # print(phone,"123456789")
    # 要先定义一个假的，要不然直接就是None,如果没有获取到redis里存储的验证码，也会是None,到时就会匹配成功
    cache_code = "1"
    #2.获取redis中保持的code
    if cache.has_key(phone):  #判断缓存中是否包含 phone 键
        # 获取redis验证码
        cache_code = cache.get(phone)
    # 3.判断返回数据
    print(code)
    print(cache_code)
    if code == cache_code:  # 匹对成功
        return ok('ok',data=None)
    else:
        return params_error("验证码错误",data=None)

#图像验证码刷新
def img_refresh(request):
    # is_ajax()会判断请求头里 'HTTP_X_REQUESTED_WITH'的值。如果
    # 请求方式不为ajax，那么请求头里是不含
    # 'HTTP_X_REQUESTED_WITH'的。如果是ajax请求，is_ajax()
    # 则会返回True.
    if not request.is_ajax():
        return HttpResponse('不是ajax请求')
    new_kew = CaptchaStore.generate_key()
    to_json_response = {
        'hashkey': new_kew,
        'image_url': captcha_image_url(new_kew)}
    return HttpResponse(json.dumps(to_json_response))

#验证图形验证码
def img_check(request):
    # print('13216461')
    if request.is_ajax():
        result =CaptchaStore.objects.filter(response=request.GET.get('response'),hashkey = request.GET.get('hashkey'))
        if result:
            data = {'status': 1}
        else:
            data = {'status': 0}
        return JsonResponse(data)
    else:
        data = {'status': 0}
        return JsonResponse(data)


#短信
def send_short_message(request):
    return render(request,'send_message.html')

#购物车
def cart(request):
    '''显示购物车'''
    return render(request,'cart.html')

#商品详情
def detail(request):
    '''显示商品详情'''
    return render(request,'detail.html')

#商品列表
def list(request):
    '''显示商品列表'''
    return render(request,'list.html')


#提交订单
def place_order(request):
    '''显示提交页面'''
    return render(request,'place_order.html')

#用户信息
def user_info(request):
    '''显示用户信息'''
    return render(request,'user_center_info.html')

#用户订单
def user_order(request):
    '''显示用户订单'''
    return render(request,'user_center_order.html')

#用户地址
def user_site(request):
    '''显示用户地址'''
    return render(request,'user_center_site.html')


