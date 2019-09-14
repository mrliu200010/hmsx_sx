from captcha.fields import CaptchaField
from django import forms
class RegisterFrom(forms.Form):
    captcha = CaptchaField()