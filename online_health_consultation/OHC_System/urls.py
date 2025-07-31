from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('consult/', views.consult, name='consult'),
    path('tips/', views.tips, name='tips'),
    path('profile/', views.profile, name='profile'),
    path('appointments/', views.appointments, name='appointments'), 
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
]
