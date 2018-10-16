import datetime
from django.test import TestCase
from django.utils import timezone
from wechat.models import *


class LoginUnit(TestCase):
    """
        对login接口的测试，前面是对get方法的测试，后面是对post方法的测试
    """
    def setUp(self):
        print('login testing...')

    def login_with_get_method(self):
        self.client.post('/a/login', {'username': 'admin', 'password': 'undefined'})
        response = self.client.get('/a/login')
        self.assertEqual(response.status_code, 200)

    #   后面是对post方法的测试

    def login_with_correct_username_and_password(self):
        response = self.client.post('/a/login', {'username': 'admin', 'password': 'undefined'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.code, 0)

    def login_with_wrong_username(self):
        response = self.client.post('/a/login', {'username': 'admin12', 'password': 'undefined'})
        self.assertNotEqual(response.status_code, 200)
        self.assertNotEqual(response.code, 0)

    def login_with_wrong_password(self):
        response = self.client.post('/a/login', {'username': 'admin', 'password': 'xxsaa'})
        self.assertNotEqual(response.status_code, 200)
        self.assertNotEqual(response.code, 0)

    def login_with_empty_password(self):
        response = self.client.post('/a/login', {'username': 'admin', 'password': ''})
        self.assertNotEqual(response.status_code, 200)
        self.assertNotEqual(response.code, 0)

    def login_with_empty_username(self):
        response = self.client.post('/a/login', {'username': '', 'password': 'xxsaa'})
        self.assertNotEqual(response.status_code, 200)
        self.assertNotEqual(response.code, 0)

    def login_with_all_empty(self):
        response = self.client.post('/a/login', {'username': '', 'password': ''})
        self.assertNotEqual(response.status_code, 200)
        self.assertNotEqual(response.code, 0)

    def login_with_no_username_arg(self):
        response = self.client.post('/a/login', {'password': ''})
        self.assertNotEqual(response.status_code, 200)
        self.assertNotEqual(response.code, 0)


class LogoutUnit(TestCase):
    """
        对logout接口的测试。
    """
    def setUp(self):
        print('logout testing...')

    def logout_with_login(self):
        response = self.client.post('/a/logout', {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.code, 0)
