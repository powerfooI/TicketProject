import datetime
from django.test import TestCase
from django.utils import timezone
from wechat.models import *
from django.contrib.auth.models import User as DjangoUser


class LoginUnit(TestCase):
    """
        对login接口的测试，前面是对get方法的测试，后面是对post方法的测试
    """

    def test_login_with_get_method(self):
        self.client.login(username='admin', password='undefined')
        response = self.client.get('/api/a/login/')
        self.assertEqual(response.json()['code'], 0)

    #   后面是对post方法的测试

    def test_login_with_correct_username_and_password(self):
        response = self.client.post('/api/a/login/', {'username': 'admin', 'password': 'undefined'})
        self.assertEqual(response.json()['code'], 0)

    def test_login_with_wrong_username(self):
        response = self.client.post('/api/a/login/', {'username': 'admin12', 'password': 'undefined'})
        self.assertNotEqual(response.json()['code'], 0)

    def test_login_with_wrong_password(self):
        response = self.client.post('/api/a/login/', {'username': 'admin', 'password': 'xxsaa'})
        self.assertNotEqual(response.json()['code'], 0)

    def test_login_with_empty_password(self):
        response = self.client.post('/api/a/login/', {'username': 'admin', 'password': ''})
        self.assertNotEqual(response.json()['code'], 0)

    def test_login_with_empty_username(self):
        response = self.client.post('/api/a/login/', {'username': '', 'password': 'xxsaa'})
        self.assertNotEqual(response.json()['code'], 0)

    def test_login_with_all_empty(self):
        response = self.client.post('/api/a/login/', {'username': '', 'password': ''})
        self.assertNotEqual(response.json()['code'], 0)

    def test_login_with_no_username_arg(self):
        response = self.client.post('/api/a/login/', {'password': ''})
        self.assertNotEqual(response.json()['code'], 0)


class LogoutUnit(TestCase):
    """
        对logout接口的测试。
    """

    def test_logout_with_login(self):
        self.client.login(username='admin', password='undefined')
        response = self.client.post('/api/a/logout/', {})
        self.assertEqual(response.json()['code'], 0)


class ActivityDetailUnit(TestCase):
    """
        对ActivityDetail接口的测试
    """

    def setUp(self):
        Activity.objects.create(name='Activity_A1', key='A1',
                                description='This is activity A1',
                                start_time=datetime.datetime(2018, 10, 21, 18, 25, 29, tzinfo=timezone.utc),
                                end_time=datetime.datetime(2018, 10, 22, 18, 25, 29, tzinfo=timezone.utc),
                                place='place_A1',
                                book_start=datetime.datetime(2018, 10, 18, 10, 25, 29, tzinfo=timezone.utc),
                                book_end=datetime.datetime(2018, 10, 19, 10, 25, 29, tzinfo=timezone.utc),
                                total_tickets=1000,
                                status=Activity.STATUS_PUBLISHED,
                                pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                remain_tickets=999)
        Activity.objects.create(name='Activity_A2', key='A2',
                                description='This is activity A2',
                                start_time=datetime.datetime(2018, 10, 21, 18, 25, 29, tzinfo=timezone.utc),
                                end_time=datetime.datetime(2018, 10, 22, 18, 25, 29, tzinfo=timezone.utc),
                                place='place_A2',
                                book_start=datetime.datetime(2018, 10, 18, 10, 25, 29, tzinfo=timezone.utc),
                                book_end=datetime.datetime(2018, 10, 19, 10, 25, 29, tzinfo=timezone.utc),
                                total_tickets=1000,
                                status=Activity.STATUS_SAVED,
                                pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                remain_tickets=999)

    def test_check_details_without_login(self):
        response = self.client.get('/api/a/activity/detail/', {'id': 2})
        self.assertNotEqual(response.json()['code'], 0)

    def test_check_details_with_login(self):
        act = Activity.objects.first()
        print(type(act))
        self.client.login(username='admin', password='undefined')
        response = self.client.get('/api/a/activity/detail/', {'id': act.id})
        self.client.logout()
        self.assertEqual(response.json()['code'], 0)

    def test_check_details_with_wrong_id(self):
        self.client.login(username='admin', password='undefined')
        response1 = self.client.get('/api/a/activity/detail/', {'id': -1})
        response2 = self.client.get('/api/a/activity/detail/', {'id': 9999999})
        response3 = self.client.get('/api/a/activity/detail/', {'id': 's'})
        self.client.logout()
        self.assertNotEqual(response1.json()['code'], 0)
        self.assertNotEqual(response2.json()['code'], 0)
        self.assertNotEqual(response3.json()['code'], 0)

    def test_change_details_without_login(self):
        act = Activity.objects.first()
        response = self.client.post('/api/a/activity/detail/', {
            'id': act.id,
            'name': 'nazong wash body',
            'key': 'N1',
            'description': '',
            'startTime': '',
            'endTime': '',
            'place': '',
            'bookStart': '',
            'bookEnd': '',
            'totalTickets': '',
            'picUrl': '',
            'status': '',
        })
        self.assertNotEqual(response.json()['code'], 0)

    def test_change_details_with_login(self):
        self.client.login(username='admin', password='undefined')
        act = Activity.objects.first()
        response = self.client.post('/api/a/activity/detail/', {'id': act.id})
        self.client.logout()
        self.assertNotEqual(response.json()['code'], 0)

    def test_change_details_with_wrong_id(self):
        self.client.login(username='admin', password='undefined')
        self.client.logout()

