from django.db import models
from django.contrib.auth.models import User

import datetime

# Create your models here.


class Shop(models.Model):
    '''
    Shop details model
    '''
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    locality = models.CharField(max_length=100)
    address = models.TextField()
    pin = models.CharField(max_length=6)
    status = models.BooleanField(default=1)
    timestamp = models.DateTimeField(auto_now=True)



class VolunteerShops(models.Model):
    '''
    Map between Volunteer and shop(s)
    '''
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)


class Items(models.Model):
    '''
    Item list
    '''
    item = models.CharField(max_length=255)
    quantity = models.CharField(max_length=5)


class UserOrder(models.Model):
    '''
    Map between User and Item, along with the status of the order from user and shopkeeper respectively
    Order_status: 0: hold
                  1: confirm
                  2: reject
                  5: done / packed
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey(Shop, on_delete=models.CASCADE)
    order_status = models.IntegerField(default=0)
    acceptance_type = models.CharField(max_length=25)
    user_finalised = models.BooleanField(default=0)
    timestamp = models.DateTimeField(auto_now=True)


class ItemOrderMap(models.Model):
    '''
    Map between order and cart list
    '''
    order = models.ForeignKey(UserOrder, on_delete=models.CASCADE)
    item = models.ForeignKey(Items, on_delete=models.CASCADE)


class ItemComments(models.Model):
    '''
    Comments on any item of an order
    '''
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    comments = models.TextField()
    comment_for = models.CharField(max_length=12)
    status = models.BooleanField(default=0)
    timestamp = models.DateTimeField(auto_now=True)


class VolunteerOrder(models.Model):
    '''
    Map between Volunteer and Order
    status: 0 - on process
            1 - delivered
    '''
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(UserOrder, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)


class Feedback(models.Model):
    '''
    User's feedback on the order
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    order = models.ForeignKey(UserOrder, on_delete=models.CASCADE)
    feedback = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)


class AccessToken(models.Model):
    '''
    Class for storing the access_token, expiry_date, refresh_token of a user
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.CharField(max_length=255)
    expire_date = models.DateTimeField(default='django.utils.timezone.now')


class UserDetails(models.Model):
    '''
    Class to store the address of a user of type User
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    contact = models.CharField(max_length=10, default='XXXXXX')


