from django.db import models

class User(models.Model):
    gender = [
        ("m", "男"),
        ("f", "女")
    ]

    nick_name = models.CharField(max_length=50, verbose_name="昵称")
    gender = models.CharField(max_length=10, choices=gender, default='m', verbose_name="性别")
    email = models.EmailField(verbose_name="邮箱")

    client_number = models.CharField(max_length=20, verbose_name="账号")
    password = models.CharField(max_length=20, verbose_name="密码")

    objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['client_number'], name='client_number'),
        ]

    def get_id(self):
        return self.client_number

    def __str__(self):
        return "%s (%s)" % (self.client_number, self.nick_name)


class Admin(models.Model):
    genders = [
        ("m", "男"),
        ("f", "女")
    ]

    nick_name = models.CharField(max_length=50, verbose_name="昵称")
    gender = models.CharField(max_length=10, choices=genders, default='m', verbose_name="性别")
    email = models.EmailField(verbose_name="邮箱")

    admin_number = models.CharField(max_length=20, verbose_name="账号")
    password = models.CharField(max_length=20, verbose_name="密码")

    objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['admin_number'], name='admin_number'),
        ]

    def get_id(self):
        return self.admin_number

    def __str__(self):
        return "%s (%s)" % (self.admin_number, self.nick_name)
