# usr/bin/env python
# -*- coding:utf-8- -*-
from django import forms
from users.models import User, Admin


class UserLoginForm(forms.Form):
    uid = forms.CharField(label='账号', max_length=20)
    password = forms.CharField(label='密码', max_length=20, widget=forms.PasswordInput)


class AdminLoginForm(forms.Form):
    uid = forms.CharField(label='账号', max_length=20)
    password = forms.CharField(label='密码', max_length=20, widget=forms.PasswordInput)


class UserRegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="确认密码")

    class Meta:
        model = User
        fields = ('nick_name',
                  'password',
                  'confirm_password',
                  'gender',
                  'email',
                  )

    def clean(self):
        cleaned_data = super(UserRegisterForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if confirm_password != password:
            self.add_error('confirm_password', 'Password does not match.')

        return cleaned_data


class UserUpdateForm(UserRegisterForm):
    class Meta:
        model = User
        fields = ('nick_name',
                  'password',
                  'confirm_password',
                  'gender',
                  'email')
