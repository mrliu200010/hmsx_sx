from django.urls import path
# from django.conf.urls import url
from app1 import views
from app1.views import *
urlpatterns = [
    path('index/', views.index, name='index'),  # 主页面
    path('cart/', views.cart, name='cart'),  # 购物车
    path('detail/', views.detail, name='detail'),  # 商品详情
    path('list/', views.list, name='list'),  # 商品列表
    path('login/', LoginView.as_view(), name='login'),  # 登录
    path('', RegisterView.as_view(), name='register'),  # 注册
    path('active/<token>', ActiveView.as_view(), name='active'),  # 账户激活
    path('place_order/', views.place_order, name='place_order'),  # 提交订单
    path('user_info/', views.user_info, name='user_info'),  # 用户信息
    path('user_order/', views.user_order, name='user_order'),  # 用户订单
    path('user_site/', views.user_site, name='user_site'),  # 用户地址
    path('sms_send/', views.sms_send, name='sms_send'),  # 发送短信接口
    path('sms_check/', views.sms_check, name='sms_check'),  # 短信验证码验证接口
    path('send_message/', views.send_short_message, name='send_message'),  # 短信页面
    path('img_refresh/', views.img_refresh, name='img_refresh'),  # 图片刷新
    path('img_check/', views.img_check, name='img_check'),  # 图文验证
]