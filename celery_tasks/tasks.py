from celery import Celery
import time
from hmsx_sx1 import settings
from django.core.mail import send_mail
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hmsx_sx1.settings")
django.setup()
app = Celery("celery_tasks.tasks", broker="redis://127.0.0.1:6379/4")
@app.task
def send_active_email(to_email, username, token):
    """发送用户激活邮件"""
    subject = "天天生鲜欢迎你" # 邮件标题
    message = ''# 邮件正文
    sender = settings.EMAIL_FROM # 发件人
    receiver = [to_email] # 收件人
    html_message = """
              <h1>%s 恭喜您成为天天生鲜注册会员</h1><br/><h3>请您在1小时内点击以下
    链接进行账户激活</h3><a
    href="http://127.0.0.1:8000/active/%s">http://127.0.0.1:8000/active/%s</a>
    """ % (username, token, token)
    send_mail(subject, message, sender, receiver, html_message=html_message)
    # 为了体现出celery异步完成发送邮件，这里睡眠5秒
    time.sleep(5)



