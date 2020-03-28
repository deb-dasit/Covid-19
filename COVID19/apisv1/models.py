from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now=True)


class Stores(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)


class Items(models.Model):
    name = models.CharField(max_length=255)
    mrp = models.DecimalField(decimal_places=2)
    batch_no = models.CharField(max_length=255)
    manf_date = models.DateField()
    exp_date = models.DateField()
    store_id = models.ForeignKey(Stores, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    stock = models.CharField(max_length=255)


