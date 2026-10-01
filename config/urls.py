"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import path, include
from discord_bot import dashboard as db
urlpatterns = [
    path('admin/', admin.site.urls),
     # Authentication
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="dashboard/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    # Dashboard
    path(
        "dashboard/",
        db.dashboard,
        name="dashboard",
    ),

    path(
        "dashboard/logs/<int:pk>/",
        db.log_detail,
        name="log_detail",
    ),

    path(
        "dashboard/logs/<int:pk>/retry/",
        db.retry_one,
        name="retry_one",
    ),

    # Rules
    path(
        "dashboard/rules/",
        db.RuleList.as_view(),
        name="rules",
    ),

    path(
        "dashboard/rules/new/",
        db.RuleCreate.as_view(),
        name="rule_new",
    ),

    path(
        "dashboard/rules/<int:pk>/",
        db.RuleUpdate.as_view(),
        name="rule_edit",
    ),

    path(
        "dashboard/rules/<int:pk>/delete/",
        db.RuleDelete.as_view(),
        name="rule_delete",
    ),

    # Root
    path("",lambda request: redirect("dashboard"),),
    
    #discord
    path("", include("discord_bot.urls")),
]
