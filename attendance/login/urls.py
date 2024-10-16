from django.urls import path
from .views import *

urlpatterns = [

    path('', register_view.as_view(), name='register_view'),
    path('login/',login_view.as_view(), name='login_view'),
    path('users/',user_view.as_view(),name = 'user_view'),
    path('refresh/',refresh_view.as_view(),name = 'refresh_view'),
    path('logout/',logout_view.as_view(),name = 'logout_view'),


]