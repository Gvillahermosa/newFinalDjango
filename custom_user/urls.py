from django.urls import path
from . import views

app_name = 'custom_user'

urlpatterns = [
    path('index/', views.index, name='index'),  # Changed 'login/' to '' for the index page
    path('register/', views.register, name='register'),
    path('login_user/', views.login_user, name='login'),  # Changed 'login/' to 'login_user/'
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login_admin/', views.login_admin, name='login_admin'),
    path('logout/', views.logout_user, name='logout'),
]
