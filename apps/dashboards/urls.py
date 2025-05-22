from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('analytics/', views.analytics, name='analytics'),
    path('crm/', views.crm, name='crm'),
    path('ecommerce/', views.ecommerce, name='ecommerce'),
]
