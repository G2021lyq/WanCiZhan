"""WanCiZhan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import users.views
import vocabularies.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', users.views.home, name="login"),
    path('back/', users.views.back, name="back"),
    path('login/', users.views.home, name="login"),
    path('login/<slug:kind>', users.views.login, name="login"),
    path('register/<slug:kind>', users.views.register, name='register'),
    path('logout', users.views.logout, name='logout'),
    path('updata/<slug:kind>', users.views.update, name="update"),

    path('vocabulary/<slug:kind>', vocabularies.views.home, name="vocabulary"),
    path('vocabulary/<slug:kind>/history', vocabularies.views.history, name='history'),
    path('vocabulary/<slug:kind>/collections', vocabularies.views.collections, name='collections'),
    path('voabulary/<slug:kind>/vocabularyTest', vocabularies.views.vocabularyTest, name='vocabularyTest'),
    path('check', vocabularies.views.check, name='check'),
    path('vocabulary/<slug:kind>/show_score', vocabularies.views.show_score, name='show_score'),
]
