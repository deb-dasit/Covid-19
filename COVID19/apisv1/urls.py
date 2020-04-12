from django.urls import path
from .views import *

app_name = 'apis'

urlpatterns = [
    path('signup', SignupView.as_view(), name='signupView'),
    path('login', LoginView.as_view(), name='loginView'),
    path('shops', ShopsView.as_view(), name='shopsView'),
    path('updateStatus', UpdateStatus.as_view(), name='updateStatus'),
    path('addList', AddListView.as_view(), name='addListView'),
    path('updateOrder', UpdateOrder.as_view(),name='updateOrder'),
    path('allOrders', AllOrders.as_view(), name='allOrders'),
    path('activeOrders', ActiveOrders.as_view(), name='activeOrders'),
    path('pastOrders', PastOrders.as_view(), name='pastOrders'),
    path('allShops', AllShops.as_view(), name='allShops'),
    path('availableOrders', AvailableOrders.as_view(), name='availableOrders'),
    path('acceptOrders',AcceptOrders.as_view(), name='acceptOrders'),
    path('completeOrder', CompleteOrder.as_view(), name='completeOrder'),
]