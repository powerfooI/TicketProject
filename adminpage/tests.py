import datetime
from django.test import TestCase
from django.utils import timezone
from wechat.models import *
from django.contrib.auth.models import User as DjangoUser
import time


def debug_print(msg):
    print('============DEBUG===========')
    print(msg)
    print('============DEBUG===========')


class LoginUnit(TestCase):
    """
        对login接口的测试，前面是对get方法的测试，后面是对post方法的测试
    """

    def setUp(self):
        DjangoUser.objects.create(username='admin', password='undefined')

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
        response = self.client.post('/api/a/login/', {'password': '123'})
        self.assertNotEqual(response.json()['code'], 0)


class LogoutUnit(TestCase):
    """
        对logout接口的测试。
    """

    def setUp(self):
        self.user = DjangoUser.objects.create(username='admin', password='undefined')

    def test_logout_with_login(self):
        self.client.force_login(self.user)
        response = self.client.post('/api/a/logout/')
        self.assertEqual(response.json()['code'], 0)

    def test_logout_without_login(self):
        response = self.client.post('/api/a/logout/')
        self.assertNotEqual(response.json()['code'], 0)


class ActivityDetailUnit(TestCase):
    """
        对ActivityDetail接口的测试
    """

    def setUp(self):
        self.user = DjangoUser.objects.create(username='admin', password='undefined')
        self.act1 = Activity.objects.create(name='Activity_A1', key='A1',
                                            description='This is activity A1',
                                            start_time=datetime.datetime(2018, 10, 24, 18, 25, 29, tzinfo=timezone.utc),
                                            end_time=datetime.datetime(2018, 10, 25, 18, 25, 29, tzinfo=timezone.utc),
                                            place='place_A1',
                                            book_start=datetime.datetime(2018, 10, 22, 10, 25, 29, tzinfo=timezone.utc),
                                            book_end=datetime.datetime(2018, 10, 23, 10, 25, 29, tzinfo=timezone.utc),
                                            total_tickets=1000,
                                            status=Activity.STATUS_SAVED,
                                            pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                            remain_tickets=999)
        self.act2 = Activity.objects.create(name='Activity_A2', key='A2',
                                            description='This is activity A2',
                                            start_time=datetime.datetime(2018, 10, 24, 18, 25, 29, tzinfo=timezone.utc),
                                            end_time=datetime.datetime(2018, 10, 25, 18, 25, 29, tzinfo=timezone.utc),
                                            place='place_A2',
                                            book_start=datetime.datetime(2018, 10, 22, 10, 25, 29, tzinfo=timezone.utc),
                                            book_end=datetime.datetime(2018, 10, 23, 10, 25, 29, tzinfo=timezone.utc),
                                            total_tickets=1000,
                                            status=Activity.STATUS_PUBLISHED,
                                            pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                            remain_tickets=999)
        self.act_end = Activity.objects.create(name='Activity_A3', key='A3',
                                               description='This is activity A3, started',
                                               start_time=datetime.datetime(2018, 10, 11, 18, 25, 29,
                                                                            tzinfo=timezone.utc),
                                               end_time=datetime.datetime(2018, 10, 12, 18, 25, 29,
                                                                          tzinfo=timezone.utc),
                                               place='place_A2',
                                               book_start=datetime.datetime(2018, 10, 7, 10, 25, 29,
                                                                            tzinfo=timezone.utc),
                                               book_end=datetime.datetime(2018, 10, 8, 10, 25, 29, tzinfo=timezone.utc),
                                               total_tickets=1000,
                                               status=Activity.STATUS_PUBLISHED,
                                               pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                               remain_tickets=999)

    def test_check_details_without_login(self):
        act = Activity.objects.get(key='A1')
        response = self.client.get('/api/a/activity/detail/', {'id': act.id})
        self.assertNotEqual(response.json()['code'], 0)

    def test_check_details_with_login(self):
        self.client.force_login(self.user)
        act = Activity.objects.get(key='A1')
        response = self.client.get('/api/a/activity/detail/', {'id': act.id})
        self.client.logout()
        debug_print(response.json())
        self.assertEqual(response.json()['data']['name'], self.act1.name)
        self.assertEqual(response.json()['data']['key'], self.act1.key)
        self.assertEqual(response.json()['data']['description'], self.act1.description)
        self.assertEqual(response.json()['data']['startTime'], time.mktime(self.act1.start_time.timetuple()))
        self.assertEqual(response.json()['data']['endTime'], time.mktime(self.act1.end_time.timetuple()))
        self.assertEqual(response.json()['data']['place'], self.act1.place)
        self.assertEqual(response.json()['data']['bookStart'], time.mktime(self.act1.book_start.timetuple()))
        self.assertEqual(response.json()['data']['bookEnd'], time.mktime(self.act1.book_end.timetuple()))
        self.assertEqual(response.json()['data']['totalTickets'], self.act1.total_tickets)
        self.assertEqual(response.json()['data']['picUrl'], self.act1.pic_url)
        self.assertEqual(response.json()['data']['bookedTickets'], self.act1.total_tickets - self.act1.remain_tickets)
        self.assertEqual(response.json()['data']['status'], self.act1.status)
        # usedTickets 怎么处理？

    def test_check_details_with_wrong_id(self):
        self.client.force_login(self.user)
        response1 = self.client.get('/api/a/activity/detail/', {'id': -1})
        response2 = self.client.get('/api/a/activity/detail/', {'id': 9999999})
        response3 = self.client.get('/api/a/activity/detail/', {'id': 's'})
        self.client.logout()
        self.assertNotEqual(response1.json()['code'], 0)
        self.assertNotEqual(response2.json()['code'], 0)
        self.assertNotEqual(response3.json()['code'], 0)

    def test_change_details_without_login(self):
        act = Activity.objects.get(key='A1')
        response = self.client.post('/api/a/activity/detail/', {
            'id': act.id,
            'name': 'nazong wash body',
            'key': 'N1',
            'description': 'this is a test description',
            'startTime': '2018-10-20T08:00:00.000Z',
            'endTime': '2018-10-21T08:00:00.000Z',
            'place': '大礼堂',
            'bookStart': '2018-10-18T08:00:00.000Z',
            'bookEnd': '2018-10-19T08:00:00.000Z',
            'totalTickets': 1234,
            'picUrl': '',
            'status': 1,
        })
        self.assertNotEqual(response.json()['code'], 0)

    def test_change_details_correctly_with_login(self):
        self.client.force_login(self.user)
        post_dic = {
            'id': self.act1.id,
            'name': 'nazong wash body',
            'key': 'N1',
            'description': 'this is a test description',
            'startTime': '2018-10-20T08:00:00.000Z',
            'endTime': '2018-10-21T08:00:00.000Z',
            'place': '大礼堂',
            'bookStart': '2018-10-18T08:00:00.000Z',
            'bookEnd': '2018-10-19T08:00:00.000Z',
            'totalTickets': 1234,
            'picUrl': '',
            'status': 0,
        }
        response_post = self.client.post('/api/a/activity/detail/', post_dic)
        response_get = self.client.get('/api/a/activity/detail/', {
            'id': self.act1.id,
        })
        self.client.logout()
        self.assertEqual(response_post.json()['code'], 0)
        self.assertEqual(response_get.json()['data']['name'], post_dic['name'])
        self.assertEqual(response_get.json()['data']['key'], post_dic['key'])
        self.assertEqual(response_get.json()['data']['description'], post_dic['key'])
        self.assertEqual(response_get.json()['data']['startTime'], time.mktime(post_dic['startTime'].timetuple()))
        self.assertEqual(response_get.json()['data']['endTime'], time.mktime(post_dic['endTime'].timetuple()))
        self.assertEqual(response_get.json()['data']['place'], post_dic['place'])
        self.assertEqual(response_get.json()['data']['bookStart'], time.mktime(post_dic['bookStart'].timetuple()))
        self.assertEqual(response_get.json()['data']['bookEnd'], time.mktime(post_dic['bookEnd'].timetuple()))
        self.assertEqual(response_get.json()['data']['totalTickets'], post_dic['totalTickets'])
        self.assertEqual(response_get.json()['data']['picUrl'], post_dic['picUrl'])
        self.assertEqual(response_get.json()['data']['status'], post_dic['status'])

    def test_change_details_with_wrong_id(self):
        self.client.force_login(self.user)
        response_post = self.client.post('/api/a/activity/detail/', {
            'id': 99999,
            'name': 'nazong wash body',
            'key': 'N1',
            'description': 'this is a test description',
            'startTime': '2018-10-20T08:00:00.000Z',
            'endTime': '2018-10-21T08:00:00.000Z',
            'place': '大礼堂',
            'bookStart': '2018-10-18T08:00:00.000Z',
            'bookEnd': '2018-10-19T08:00:00.000Z',
            'totalTickets': 1234,
            'picUrl': '',
            'status': 1,
        })
        self.client.logout()
        self.assertNotEqual(response_post.json()['code'], 0)

    def test_change_details_with_published(self):
        self.client.force_login(self.user)
        response_post = self.client.post('/api/a/activity/detail/', {
            'id': self.act2.id,
            'name': 'nazong wash body',
            'key': 'N1',
            'description': 'this is a test description',
            'startTime': '2018-10-20T08:00:00.000Z',
            'endTime': '2018-10-21T08:00:00.000Z',
            'place': '大礼堂',
            'bookStart': '2018-10-18T08:00:00.000Z',
            'bookEnd': '2018-10-19T08:00:00.000Z',
            'totalTickets': 1234,
            'picUrl': '',
            'status': 0,
        })
        response_get = self.client.get('/api/a/activity/detail/', {
            'id': self.act2.id
        })
        self.client.logout()
        self.assertEqual(response_post.json()['code'], 0)
        self.assertEqual(response_get.json()['code'], 0)
        self.assertEqual(response_get.json()['data']['status'], 1)
