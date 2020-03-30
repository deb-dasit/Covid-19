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
        print(request.POST)
        data = {
            'username': request.POST.get('email'),
            'email': request.POST.get('email'),
            'first_name': request.POST.get('name'),
            'password': request.POST.get('password')
        }
        print(data)
        user = User.objects.create_user(**data)
        try:
            group = Group.objects.get(name=request.POST.get('role'))
            group.user_set.add(user)
            token = self.create_token(request, user)
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
            return JsonResponse({'status': 200, 'shops': list(shops)})
        return JsonResponse({'status': 403, 'msg': token['msg']})


def user_list(request):
    return JsonResponse({'ggg':'lllll'})