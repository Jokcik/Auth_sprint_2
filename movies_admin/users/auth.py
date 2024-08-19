import http
import json
import logging
from enum import Enum
import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class Roles(str, Enum):
    ADMIN = 'ADMIN'
    USER = 'USER'


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_API_LOGIN_URL
        payload = {'username': username, 'password': password}
        response = requests.post(url, data=json.dumps(payload))
        if response.status_code != http.HTTPStatus.OK:
            return None
        data = response.json()
        if not data or 'access_token' not in data:
            return None

        access_token = data['access_token']
        url = settings.AUTH_API_GET_USER_URL
        user = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
        user_data = user.json()
        print(user_data)
        try:
            user, created = User.objects.get_or_create(id=user_data['id'])
            user.email = user_data.get('email')
            user.is_admin = any(role.get('name') == Roles.ADMIN.value for role in user_data.get('roles', []))
            user.is_active = user_data.get('is_active')
            user.save()
        except Exception as e:
            logging.exception(e)
            return None
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
