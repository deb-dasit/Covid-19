from django.urls import path
from .views import *

app_name = 'apis'

urlpatterns = [
    path('signup', SignupView.as_view(), name='signupView'),
    path('login', LoginView.as_view(), name='loginView'),
    path('shops', ShopsView.as_view(), name='shopsView'),
    path('', user_list, name='uuu')
]