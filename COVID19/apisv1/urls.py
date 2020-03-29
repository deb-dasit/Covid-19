from django.urls import path
from .views import *

app_name = 'apis'

urlpatterns = [
    path('signup', SignupView.as_view(), name='signupView'),
    path('login', LoginView.as_view(), name='loginView'),
    path('shops', ShopsView.as_view(), name='shopsView'),
    path('updateStatus', UpdateStatus.as_view(), name='updateStatus'),
    path('addList', AddListView.as_view(), name='addListView')
]