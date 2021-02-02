from django import forms
from django.forms import widgets
from blog.models import UserInfo
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
class Userform(forms.Form):
    user=forms.CharField(max_length=32,error_messages={"required":"用户名不能为空!"},label="用户名",widget=widgets.TextInput(attrs={"class":"form-control"}))
    pwd=forms.CharField(max_length=32,error_messages={"required":"密码不能为空!"},label="密码",widget=widgets.PasswordInput(attrs={"class":"form-control"}))
    re_pwd=forms.CharField(max_length=32,error_messages={"required":"密码不能为空!"},label="确认密码",widget=widgets.PasswordInput(attrs={"class":"form-control"}))
    email=forms.EmailField(max_length=32,error_messages={"required":"邮箱不能为空!"},label="邮箱",widget=widgets.EmailInput(attrs={"class":"form-control"}))
    def clean_user(self):
        user1=self.cleaned_data.get("user")
        user2=UserInfo.objects.filter(username=user1).first()
        if not user2:
            return user1
        else:
            raise ValidationError("该用户已注册!")

    def clean(self):
        pwd=self.cleaned_data.get("pwd")
        re_pwd=self.cleaned_data.get("re_pwd")
        if pwd and re_pwd:
            if pwd==re_pwd:
                return self.cleaned_data
            else:
                raise ValidationError("两次密码不一致!")
        else:
            return self.cleaned_data
