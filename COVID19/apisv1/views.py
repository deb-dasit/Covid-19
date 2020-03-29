from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from .models import *

import datetime
import base64
import hashlib
import json

# Create your views here.


def verify_token(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header:
        auth_method, auth_value = auth_header.split(' ', 1)
    if not auth_value:
        return False
    try:
        access_token = AccessToken.objects.get(access_token=auth_value.strip())
        if access_token.expire_date < timezone.now():
            access_token.delete()
            return {'msg': 'Token expires'}
        access_token.expire_date = datetime.datetime.now() + datetime.timedelta(hours=10)
        access_token.save()
        request.user = access_token.user
        return access_token
    except ObjectDoesNotExist:
        return {'msg': 'Invalid Token'}


def get_token_data(request, user):
    token_data = {
        'user': user,
        'access_token': base64.b64encode((user.password+ str(datetime.datetime.now())).encode()).decode(),
        'refresh_token': hashlib.sha256((user.email + str(datetime.datetime.now())).encode()).hexdigest(),
        'expire_date': datetime.datetime.now() + datetime.timedelta(hours=10)
    }
    return token_data

def get_token(request):
    try:
        token = AccessToken.objects.get(user=request.user)
        return token
    except ObjectDoesNotExist:
        return None


class SignupView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(SignupView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {
            'username': request.POST.get('email'),
            'email': request.POST.get('email'),
            'first_name': request.POST.get('name'),
            'password': request.POST.get('password')
        }
        user = User.objects.create_user(**data)
        try:
            group = Group.objects.get(name=request.POST.get('role'))
            group.user_set.add(user)
            token = self.create_token(request, user)
            if(request.POST.get('role') == 'shopkeeper'):
                shop = Shop()
                shop.name = request.POST.get('shop_name')
                shop.address= request.POST.get('address')
                shop.locality= request.POST.get('locality')
                shop.city= request.POST.get('city')
                shop.state= request.POST.get('state')
                shop.pin= request.POST.get('pincode')
                shop.owner= user
                shop.save()
            return JsonResponse({'status': 200, 'msg': 'Registered successfully', 'access_token': token.access_token, 'refresh_token': token.refresh_token})
        except ObjectDoesNotExist:
            return JsonResponse({'status': 200, 'msg': 'Role doesn\'t exists'})

    def create_token(self, request, user):
        token_data = get_token_data(request, user)
        access_token = AccessToken(**token_data)
        return access_token



class LoginView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.do_login(request):
            token = get_token(request)
            return JsonResponse({'status': 200, 'msg': 'Login success', 'access_token': token.access_token, 'refresh_token': token.refresh_token})
        else:
            return JsonResponse({'status': 200, 'msg': 'Something went wrong. Try again.'})

    def do_login(self, request, token=None):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                request.user = user
                AccessToken.objects.update_or_create(get_token_data(request, user))
                return True
        return False


class ShopsView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(ShopsView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        token = verify_token(request)
        if isinstance(token, AccessToken):
            shops = Shop.objects.all().values().order_by('name')
            print(list(shops))
            return JsonResponse({'status': 200, 'shops': list(shops)})
        return JsonResponse({'status': 403, 'msg': token['msg']})


class UpdateStatus(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateStatus, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = verify_token(request)
        status = request.POST.get('status')
        st = False
        if status.lower() == 'open':
            st = True
        try:
            shop = Shop.objects.get(owner=request.user, id=request.POST.get('shop_id'))
            shop.status = st
            shop.save()
            send_job_notification(shop.status, shop.id)
            return JsonResponse({'status': 200, 'msg': 'Updated successfully'})
        except Exception as e:
            print(e)
            return JsonResponse({'status': 403, 'msg': 'Invalid request'})

from channels.layers import get_channel_layer

def send_job_notification(message, job_id):
    print(message)
    channel_layer = get_channel_layer()
    group_name = 'job_{0}'.format(job_id)
    channel_layer.group_send(
    group_name,
    {
        "type": "websocket.send",
        "message": message,
    })

def send_notification(request):
    return render(request, 'user_list.html')


class AddListView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(AddListView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = verify_token(request)
        print(request.POST)
        try:
            store = Shop.objects.get(pk=request.POST.get('store_id'))
            cart_items = json.loads(request.POST.getlist('cart')[0])
            # print(json.loads(cart_items[0]))
            order = UserOrder(
                user=request.user,
                store=store,
                acceptance_type=request.POST.get('store_acceptance_type'),
                user_finalised=True if request.POST.get('store_acceptance_type')=='confirm_first' else False
            )
            order.save()
            for i in cart_items:
                itm = Items(
                    item=i['item'],
                    quantity=i['quantity']
                )
                itm.save()
                item_order_map = ItemOrderMap.objects.create(order=order, item=itm)
            return JsonResponse({'status': 200, 'msg': 'Sent to store'})
        except ObjectDoesNotExist:
            return JsonResponse({'status': 403, 'msg': 'Invalid store'})
