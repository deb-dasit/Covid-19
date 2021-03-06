from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import F
from django.db.utils import IntegrityError
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
        'access_token': base64.b64encode(hashlib.sha3_256((user.password + str(datetime.datetime.now())).encode()).hexdigest().encode()).decode(),
        'refresh_token': hashlib.sha256((user.email + str(datetime.datetime.now())).encode()).hexdigest(),
        'expire_date': datetime.datetime.now() + datetime.timedelta(hours=10)
    }
    return token_data


def get_token(request):
    try:
        token = AccessToken.objects.filter(user=request.user).last()
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
        try:
            user = User.objects.create_user(**data)
        except IntegrityError:
            return JsonResponse({'status': 403, 'msg': 'Username already exists'})

        try:
            group = Group.objects.get(name=request.POST.get('role'))
            group.user_set.add(user)
            token = self.create_token(request, user)
            if request.POST.get('role').lower() == 'shop':
                shop = Shop()
                shop.name = request.POST.get('shop_name')
                shop.address = request.POST.get('address')
                shop.locality = request.POST.get('locality')
                shop.city = request.POST.get('city')
                shop.state = request.POST.get('state')
                shop.pin = request.POST.get('pincode')
                shop.owner = user
                shop.save()
            elif request.POST.get('role').lower() == 'user':
                user_det = UserDetails(
                    user=user,
                    address=request.POST.get('address')
                )
                user_det.save()
            return JsonResponse({'status': 200, 'msg': 'Registered successfully', 'access_token': token.access_token,
                                 'refresh_token': token.refresh_token, 'role': token.user.groups.all()[0].name})
        except ObjectDoesNotExist:
            return JsonResponse({'status': 200, 'msg': 'Role doesn\'t exists'})

    def create_token(self, request, user):
        token_data = get_token_data(request, user)
        access_token = AccessToken(**token_data)
        access_token.save()
        return access_token


class LoginView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.do_login(request):
            token = get_token(request)
            return JsonResponse({'status': 200, 'msg': 'Login success', 'access_token': token.access_token,
                                 'refresh_token': token.refresh_token, 'role': token.user.groups.all()[0].name})
        else:
            return JsonResponse({'status': 200, 'msg': 'Username or password invalid. Try again.'})

    def do_login(self, request, token=None):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                request.user = user
                AccessToken.objects.update_or_create(**get_token_data(request, user))
                return True
        return False


class ShopsView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(ShopsView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        token = verify_token(request)
        if isinstance(token, AccessToken):
            if request.user.groups.all()[0].id == 1:
                shops = Shop.objects.filter(owner=request.user).annotate(owner_name=F('owner__first_name')).values().order_by('name')
            else:
                shops = Shop.objects.all().annotate(owner_name=F('owner__first_name')).values().order_by('name')
            return JsonResponse({'status': 200, 'shops': list(shops)})
        return JsonResponse({'status': 403, 'msg': token['msg']})


class UpdateStatus(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateStatus, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = verify_token(request)
        if not isinstance(token, AccessToken):
            return JsonResponse({'status': 403, 'msg': token['msg']})
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
        except:
            return JsonResponse({'status': 403, 'msg': 'Invalid request'})


from channels.layers import get_channel_layer


def send_job_notification(message, job_id):
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
        if not isinstance(token, AccessToken):
            return JsonResponse({'status': 403, 'msg': token['msg']})
        try:
            store = Shop.objects.get(pk=request.POST.get('store_id'))
            cart_items = json.loads(request.POST.getlist('cart')[0])
            order = UserOrder(
                user=request.user,
                store=store,
                acceptance_type=request.POST.get('store_acceptance_type'),
                user_finalised=True if request.POST.get('store_acceptance_type') == 'confirm_first' else False
            )
            order.save()
            for i in cart_items:
                itm = Items(
                    item=i['item'],
                    quantity=i['quantity']
                )
                itm.save()
                ItemOrderMap.objects.create(order=order, item=itm)
            return JsonResponse({'status': 200, 'msg': 'Sent to store'})
        except ObjectDoesNotExist:
            return JsonResponse({'status': 403, 'msg': 'Invalid store'})


class UpdateOrder(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateOrder, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = verify_token(request)
        if not isinstance(token, AccessToken):
            return JsonResponse({'status': 403, 'msg': token['msg']})
        if request.user.groups.all()[0].id != 1:
            return JsonResponse({'status': 200, 'msg': 'Not authorized'})
        try:
            user_order = UserOrder.objects.get(pk=request.POST.get('user_order'), store=Shop.objects.get(pk=request.POST.get('store_id')))
            user_order.order_status = request.POST.get('order_status')
            user_order.save()
            return JsonResponse({'status': 200, 'msg': 'Order updated successfully'})
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'Invalid order'})


class AllOrders(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(AllOrders, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        token = verify_token(request)
        if not isinstance(token, AccessToken):
            return JsonResponse({'status': 403, 'msg': token['msg']})
        if request.user.groups.all()[0].id == 1:
            shops = Shop.objects.filter(owner=request.user)
            if not shops:
                return JsonResponse({'status': 200, 'msg': 'No shop(s) regirstered'})
            orders = UserOrder.objects.filter(store__in=shops).select_related('store').order_by('-timestamp')
        elif request.user.groups.all()[0].id == 3:
            orders = UserOrder.objects.filter(user=request.user).select_related('store').order_by('-timestamp')
        else:
            v_orders = VolunteerOrder.objects.filter(volunteer=request.user).values('order')
            orders = UserOrder.objects.filter(pk__in=v_orders)
        order_list = []
        for i in orders:
            user_address = None
            try:
                user_details = UserDetails.objects.get(user=i.user)
                user_address = user_details.address
            except ObjectDoesNotExist:
                pass
            try:
                vol_order = VolunteerOrder.objects.get(order=i)
                order_status = 'Out for delivery' if vol_order.status == 0 else 'Delivered'
            except ObjectDoesNotExist:
                order_status = 'Hold' if i.order_status == 0 else 'Confirm' if i.order_status == 1 else 'Reject' if i.order_status == 2 else 'Packed'
            cart_items = ItemOrderMap.objects.filter(order=i).annotate(item_name=F('item__item')).annotate(item_quantity=F('item__quantity')).values('item_name', 'item_quantity')
            tmp = {
                'id': i.id,
                'user': i.user.first_name,
                'user_address': user_address,
                'shop': [
                    {
                        'store_id': i.store.id,
                        'name': i.store.name,
                        'owner': i.store.owner.first_name,
                        'state': i.store.state,
                        'city': i.store.city,
                        'locality': i.store.locality,
                        'address': i.store.address,
                        'pin': i.store.pin
                    }
                ],
                'items': list(cart_items),
                'order_status': order_status,
                'acceptance_type': 'availability',
                'user_finalised': True,
                'timestamp': i.timestamp.strftime('%d/%m/%Y %H:%M:%S')
            }
            order_list.append(tmp)
        return JsonResponse({'status': 200, 'data': order_list})


class ActiveOrders(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(ActiveOrders, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        token = verify_token(request)
        if not isinstance(token, AccessToken):
            return JsonResponse({'status': 403, 'msg': token['msg']})
        if request.user.groups.all()[0].id == 1:
            shops = Shop.objects.filter(owner=request.user)
            if not shops:
                return JsonResponse({'status': 200, 'msg': 'No shop(s) regirstered'})
            orders = UserOrder.objects.filter(store__in=shops, order_status__in=[0, 1]).select_related('store').order_by('-timestamp')
        elif request.user.groups.all()[0].id == 3:
            orders = UserOrder.objects.filter(user=request.user, order_status=1).select_related('store').order_by(
                '-timestamp')
        else:
            v_orders = VolunteerOrder.objects.filter(volunteer=request.user, status=0).values('order')
            orders = UserOrder.objects.filter(pk__in=v_orders)
        order_list = []
        for i in orders:
            user_address = None
            try:
                user_details = UserDetails.objects.get(user=i.user)
                user_address = user_details.address
            except ObjectDoesNotExist:
                pass
            try:
                vol_order = VolunteerOrder.objects.get(order=i)
                order_status = 'Out for delivery' if vol_order.status == 0 else 'Delivered'
            except ObjectDoesNotExist:
                order_status = 'Hold' if i.order_status == 0 else 'Confirm' if i.order_status == 1 else 'Reject' if i.order_status == 2 else 'Packed'
            cart_items = ItemOrderMap.objects.filter(order=i).annotate(item_name=F('item__item')).annotate(
                item_quantity=F('item__quantity')).values('item_name', 'item_quantity')
            tmp = {
                'id': i.id,
                'user': i.user.first_name,
                'user_address': user_address,
                'shop': [
                    {
                        'store_id': i.store.id,
                        'name': i.store.name,
                        'owner': i.store.owner.first_name,
                        'state': i.store.state,
                        'city': i.store.city,
                        'locality': i.store.locality,
                        'address': i.store.address,
                        'pin': i.store.pin
                    }
                ],
                'items': list(cart_items),
                'order_status': order_status,
                'acceptance_type': 'availability',
                'user_finalised': True,
                'timestamp': i.timestamp.strftime('%d/%m/%Y %H:%M:%S')
            }
            order_list.append(tmp)
        return JsonResponse({'status': 200, 'data': order_list})


class PastOrders(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(PastOrders, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        token = verify_token(request)
        if not isinstance(token, AccessToken):
            return JsonResponse({'status': 403, 'msg': token['msg']})
        if request.user.groups.all()[0].id == 1:
            shops = Shop.objects.filter(owner=request.user)
            if not shops:
                return JsonResponse({'status': 200, 'msg': 'No shop(s) regirstered'})
            orders = UserOrder.objects.filter(store__in=shops, order_status__in=[2, 5]).select_related('store').order_by('-timestamp')
        elif request.user.groups.all()[0].id == 3:
            orders = UserOrder.objects.filter(user=request.user, order_status__in=[2, 5]).select_related('store').order_by('-timestamp')
        else:
            v_orders = VolunteerOrder.objects.filter(volunteer=request.user, status=1).values('order')
            orders = UserOrder.objects.filter(pk__in=v_orders)
        order_list = []
        for i in orders:
            user_address = None
            try:
                user_details = UserDetails.objects.get(user=i.user)
                user_address = user_details.address
            except ObjectDoesNotExist:
                pass
            try:
                vol_order = VolunteerOrder.objects.get(order=i)
                order_status = 'Out for delivery' if vol_order.status == 0 else 'Delivered'
            except ObjectDoesNotExist:
                order_status = 'Hold' if i.order_status == 0 else 'Confirm' if i.order_status == 1 else 'Packed' if i.order_status == 5 else 'Reject'
            cart_items = ItemOrderMap.objects.filter(order=i).annotate(item_name=F('item__item')).annotate(
                item_quantity=F('item__quantity')).values('item_name', 'item_quantity')
            tmp = {
                'id': i.id,
                'user': i.user.first_name,
                'user_address': user_address,
                'shop': [
                    {
                        'store_id': i.store.id,
                        'name': i.store.name,
                        'owner': i.store.owner.first_name,
                        'state': i.store.state,
                        'city': i.store.city,
                        'locality': i.store.locality,
                        'address': i.store.address,
                        'pin': i.store.pin
                    }
                ],
                'items': list(cart_items),
                'order_status': order_status,
                'acceptance_type': 'availability',
                'user_finalised': True,
                'timestamp': i.timestamp.strftime('%d/%m/%Y %H:%M:%S')
            }
            order_list.append(tmp)
        return JsonResponse({'status': 200, 'data': order_list})


class AllShops(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(AllShops, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        token = verify_token(request)
        if not isinstance(token, AccessToken):
            return JsonResponse({'status': 403, 'msg': token['msg']})
        if request.user.groups.all()[0].id == 1:
            shop = Shop.objects.filter(owner=request.user).order_by('name')
        elif request.user.groups.all()[0].id == 2:
            shop = Shop.objects.all().order_by('name')
        else:
            return JsonResponse({'status': 403, 'msg': 'Not authorized'})
        shops = []
        for i in shop:
            tmp = {
                'id': i.id,
                'name': i.name,
                'owner': i.owner.first_name,
                'state': i.state,
                'city': i.city,
                'locality': i.locality,
                'address': i.address,
                'pin': i.pin
                }
            shops.append(tmp)
        return JsonResponse({'status': 200, 'data': shops})


class AvailableOrders(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(AvailableOrders, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        token = verify_token(request)
        if not isinstance(token, AccessToken):
            return JsonResponse({'status': 403, 'msg': token['msg']})
        if request.user.groups.all()[0].id != 2:
            return JsonResponse({'status': 403, 'msg': 'Not authorized'})
        try:
            stores = VolunteerShops.objects.filter(volunteer=request.user).values('shop')
        except ObjectDoesNotExist:
            return JsonResponse({'status': 200, 'msg': 'No shop(s) registered'})
        volunteer_orders = UserOrder.objects.filter(store__in=stores, order_status=5).select_related('store').order_by('timestamp')
        order_list = []
        for i in volunteer_orders:
            user_address = None
            try:
                user_details = UserDetails.objects.get(user=i.user)
                user_address = user_details.address
            except ObjectDoesNotExist:
                pass
            try:
                vol_order = VolunteerOrder.objects.get(order=i)
                order_status = 'Out for delivery' if vol_order.status == 0 else 'Delivered'
            except ObjectDoesNotExist:
                order_status = 'Hold' if i.order_status == 0 else 'Confirm' if i.order_status == 1 else 'Packed' if i.order_status == 5 else 'Reject'
            if order_status == 'Delivered':
                continue
            cart_items = ItemOrderMap.objects.filter(order=i).annotate(item_name=F('item__item')).annotate(
                item_quantity=F('item__quantity')).values('item_name', 'item_quantity')
            tmp = {
                'id': i.id,
                'user': i.user.first_name,
                'user_address': user_address,
                'shop': [
                    {
                        'store_id': i.store.id,
                        'name': i.store.name,
                        'owner': i.store.owner.first_name,
                        'state': i.store.state,
                        'city': i.store.city,
                        'locality': i.store.locality,
                        'address': i.store.address,
                        'pin': i.store.pin
                    }
                ],
                'items': list(cart_items),
                'order_status': order_status,
                'acceptance_type': 'availability',
                'user_finalised': True,
                'timestamp': i.timestamp.strftime('%d/%m/%Y %H:%M:%S')
            }
            order_list.append(tmp)
        return JsonResponse({'status': 200, 'data': order_list})


class AcceptOrders(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(AcceptOrders, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = verify_token(request)
        if not isinstance(token, AccessToken):
            return JsonResponse({'status': 403, 'msg': token['msg']})
        if request.user.groups.all()[0].id != 2:
            return JsonResponse({'status': 403, 'msg': 'Not authorized'})
        try:
            user_order = UserOrder.objects.get(pk=request.POST.get('user_order'))
        except ObjectDoesNotExist:
            return JsonResponse({'status': 200, 'msg': 'Order delivered or invalid'})
        updated, volunteer_orders = VolunteerOrder.objects.update_or_create(
            volunteer=request.user,
            order=user_order
        )
        return JsonResponse({'status': 200, 'msg': 'Order accepted'})


class CompleteOrder(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(CompleteOrder, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = verify_token(request)
        if not isinstance(token, AccessToken):
            return JsonResponse({'status': 403, 'msg': token['msg']})
        if request.user.groups.all()[0].id != 2:
            return JsonResponse({'status': 403, 'msg': 'Not authorized'})
        try:
            user_order = UserOrder.objects.get(pk=request.POST.get('user_order'))
        except ObjectDoesNotExist:
            return JsonResponse({'status': 200, 'msg': 'Order delivered or invalid'})
        try:
            volunteer_order = VolunteerOrder.objects.get(order=user_order)
            volunteer_order.status = 1
            volunteer_order.save()
            return JsonResponse({'status': 200, 'msg': 'Order delivered successfully'})
        except ObjectDoesNotExist:
            return JsonResponse({'status': 200, 'msg': 'Order delivered or invalid'})


class AddVolunteerToShop(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(AddVolunteerToShop, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = verify_token(request)
        if not isinstance(token, AccessToken):
            return JsonResponse({'status': 403, 'msg': token['msg']})
        if request.user.groups.all()[0].id != 2:
            return JsonResponse({'status': 403, 'msg': 'Not authorized'})
        shops = json.loads(request.POST.get('shops'))
        for i in shops:
            created, volunteer_shop = VolunteerShops.objects.get_or_create(
                volunteer=request.user,
                shop=Shop.objects.get(pk=i)
            )
        return JsonResponse({'status': 200, 'msg': 'Shop(s) mapped successfully'})


class Profile(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(Profile, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        token = verify_token(request)
        if not isinstance(token, AccessToken):
            return JsonResponse({'status': 403, 'msg': token['msg']})
        shops = []
        userDetails = {'name': token.user.first_name + ' ' + token.user.last_name, 'role': token.user.groups.all()[0].name}
        profile_data = {}
        if request.user.groups.all()[0].id == 1:
            shop_list = Shop.objects.filter(owner=request.user)
            for i in shop_list:
                tmp = {
                    'store_id': i.id,
                    'name': i.name,
                    'state': i.state,
                    'city': i.city,
                    'locality': i.locality,
                    'address': i.address,
                    'pin': i.pin
                }
                shops.append(tmp)
        elif request.user.groups.all()[0].id == 2:
            shop_list = VolunteerShops.objects.filter(volunteer=request.user).select_related('shop')
            for i in shop_list:
                tmp = {
                    'store_id': i.shop.id,
                    'name': i.shop.name,
                    'state': i.shop.state,
                    'city': i.shop.city,
                    'locality': i.shop.locality,
                    'address': i.shop.address,
                    'pin': i.shop.pin,
                    'status': 'Open' if i.shop.status == 1 else 'Closed'
                }
                shops.append(tmp)
        try:
            user_details = UserDetails.objects.get(user=request.user)
            userDetails['contact'] = user_details.contact
            userDetails['address'] = user_details.address
        except ObjectDoesNotExist:
            pass
        profile_data['user_details'] = userDetails
        profile_data['shops'] = shops
        return JsonResponse({'status': 200, 'data': profile_data})


class UpdateProfile(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateProfile, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = verify_token(request)
        if not isinstance(token, AccessToken):
            return JsonResponse({'status': 403, 'msg': token['msg']})
        updated, obj = UserDetails.objects.update_or_create(
            user=request.user,
            address=request.POST.get('address'),
            contact=request.POST.get('contact')
        )
        msg = 'Profile added successfully'
        if updated:
            msg = 'Profile updated successfully'
        return JsonResponse({'status': 200, 'msg': msg})
