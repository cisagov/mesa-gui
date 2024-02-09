"""
URL configuration for mesa_gui project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        redirect_authenticated_user=True,
        authentication_form=views.StyledAuthenticationForm), name='login'
    ),
    path('logout/',
        auth_views.LogoutView.as_view(next_page='login'), name='logout'
    ),
    path('', views.home, name="home"),
    path('dashboard/job_table', views.dashboard_job_table, name="dashboard_job_table"),
    path('dashboard/all_checks_card', views.dashboard_all_checks_card, name="dashboard_all_checks_card"),
    
    path('jobs/<int:job_id>/run', views.job_run, name="job_run"),
    path('jobs/run_all', views.job_run_all, name="job_run_all"),
    path('jobs/<int:job_id>/stop', views.job_stop, name="job_stop"),
    path('jobs/stop_all', views.job_stop_all, name="job_stop_all"),
    path('jobs/<int:job_id>/delete-data', views.job_delete_data, name="job_delete_data"),
    path('jobs/<int:job_id>/download-data', views.job_download_data, name="job_download_data"),
    path('jobs/generate_report', views.job_generate_report, name="job_generate_report"),
    path('settings', views.settings, name="settings"),
    path('demo', views.demo, name="demo")
]
