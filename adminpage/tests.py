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
        对login接口的测试，前面是对get方法的测试，后面是对post方法的测试.
        函数名即测试内容。
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
        self.act_saved = Activity.objects.create(name='Activity_A1', key='A1',
                                                 description='This is activity A1',
                                                 start_time=datetime.datetime(2018, 10, 24, 18, 25, 29,
                                                                              tzinfo=timezone.utc),
                                                 end_time=datetime.datetime(2018, 10, 25, 18, 25, 29,
                                                                            tzinfo=timezone.utc),
                                                 place='place_A1',
                                                 book_start=datetime.datetime(2018, 10, 22, 10, 25, 29,
                                                                              tzinfo=timezone.utc),
                                                 book_end=datetime.datetime(2018, 10, 23, 10, 25, 29,
                                                                            tzinfo=timezone.utc),
                                                 total_tickets=1000,
                                                 status=Activity.STATUS_SAVED,
                                                 pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                                 remain_tickets=999)
        self.act_published = Activity.objects.create(name='Activity_A2', key='A2',
                                                     description='This is activity A2',
                                                     start_time=datetime.datetime(2018, 10, 24, 18, 25, 29,
                                                                                  tzinfo=timezone.utc),
                                                     end_time=datetime.datetime(2018, 10, 25, 18, 25, 29,
                                                                                tzinfo=timezone.utc),
                                                     place='place_A2',
                                                     book_start=datetime.datetime(2018, 10, 22, 10, 25, 29,
                                                                                  tzinfo=timezone.utc),
                                                     book_end=datetime.datetime(2018, 10, 23, 10, 25, 29,
                                                                                tzinfo=timezone.utc),
                                                     total_tickets=1000,
                                                     status=Activity.STATUS_PUBLISHED,
                                                     pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                                     remain_tickets=999)
        self.act_start = Activity.objects.create(name='Activity_A3', key='A3',
                                                 description='This is activity A3, started',
                                                 start_time=datetime.datetime(2018, 10, 11, 18, 25, 29,
                                                                              tzinfo=timezone.utc),
                                                 end_time=datetime.datetime(2018, 12, 12, 18, 25, 29,
                                                                            tzinfo=timezone.utc),
                                                 place='place_A2',
                                                 book_start=datetime.datetime(2018, 10, 7, 10, 25, 29,
                                                                              tzinfo=timezone.utc),
                                                 book_end=datetime.datetime(2018, 10, 8, 10, 25, 29,
                                                                            tzinfo=timezone.utc),
                                                 total_tickets=1000,
                                                 status=Activity.STATUS_PUBLISHED,
                                                 pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                                 remain_tickets=999)
        self.act_end = Activity.objects.create(name='Activity_A4', key='A4',
                                               description='This is activity A4, ended',
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
        self.act_book_start = Activity.objects.create(name='Activity_A5', key='A5',
                                                      description='This is activity A5, book started',
                                                      start_time=datetime.datetime(2018, 11, 25, 18, 25, 29,
                                                                                   tzinfo=timezone.utc),
                                                      end_time=datetime.datetime(2018, 11, 26, 18, 25, 29,
                                                                                 tzinfo=timezone.utc),
                                                      place='place_A2',
                                                      book_start=datetime.datetime(2018, 10, 7, 10, 25, 29,
                                                                                   tzinfo=timezone.utc),
                                                      book_end=datetime.datetime(2018, 11, 24, 10, 25, 29,
                                                                                 tzinfo=timezone.utc),
                                                      total_tickets=1000,
                                                      status=Activity.STATUS_PUBLISHED,
                                                      pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                                      remain_tickets=999)

    def test_check_details_without_login(self):
        response = self.client.get('/api/a/activity/detail/', {'id': self.act_published.id})
        self.assertNotEqual(response.json()['code'], 0)

    def test_check_details_with_login(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/a/activity/detail/', {'id': self.act_published.id})
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
        response = self.client.post('/api/a/activity/detail/', {
            'id': self.act_published.id,
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
            'id': self.act_saved.id,
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
            'id': self.act_saved.id,
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
            'id': self.act_published.id,
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
            'id': self.act_published.id
        })
        self.client.logout()
        self.assertEqual(response_post.json()['code'], 0)
        self.assertEqual(response_get.json()['code'], 0)
        self.assertEqual(response_get.json()['data']['status'], self.act_published.status)
        self.assertEqual(response_get.json()['data']['name'], self.act_published.name)
        self.assertEqual(response_get.json()['data']['place'], self.act_published.place)
        self.assertEqual(time.strptime(response_get.json()['data']['bookStart'], "%Y-%m-%dT%H:%M:%S.000Z"),
                         self.act_published.book_start)

    def test_change_details_with_started(self):
        self.client.force_login(self.user)
        response_post = self.client.post('/api/a/activity/detail/', {
            'id': self.act_start.id,
            'name': 'modify test',
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
            'id': self.act_start.id
        })
        self.client.logout()
        self.assertEqual(response_post.json()['code'], 0)
        self.assertEqual(response_get.json()['code'], 0)
        self.assertEqual(time.strptime(response_get.json()['data']['bookEnd'], "%Y-%m-%dT%H:%M:%S.000Z"),
                         self.act_start.book_end)

    def test_change_details_with_ended(self):
        self.client.force_login(self.user)
        response_post = self.client.post('/api/a/activity/detail/', {
            'id': self.act_start.id,
            'name': 'modify test',
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
            'id': self.act_start.id
        })
        self.client.logout()
        self.assertEqual(response_post.json()['code'], 0)
        self.assertEqual(response_get.json()['code'], 0)
        self.assertEqual(time.strptime(response_get.json()['data']['startTime'], "%Y-%m-%dT%H:%M:%S.000Z"),
                         self.act_end.start_time)
        self.assertEqual(time.strptime(response_get.json()['data']['endTime'], "%Y-%m-%dT%H:%M:%S.000Z"),
                         self.act_end.end_time)

    def test_change_details_with_book_started(self):
        self.client.force_login(self.user)

        response_post = self.client.post('/api/a/activity/detail/', {
            'id': self.act_start.id,
            'name': 'modify test',
            'key': 'N1',
            'description': 'this is a test description',
            'startTime': '2018-10-20T08:00:00.000Z',
            'endTime': '2018-10-21T08:00:00.000Z',
            'place': '大礼堂',
            'bookStart': '2018-10-18T08:00:00.000Z',
            'bookEnd': '2018-10-19T08:00:00.000Z',
            'totalTickets': 99999,
            'picUrl': '',
            'status': 0,
        })
        response_get = self.client.get('/api/a/activity/detail/', {
            'id': self.act_start.id
        })
        self.client.logout()
        self.assertEqual(response_post.json()['code'], 0)
        self.assertEqual(response_get.json()['code'], 0)
        self.assertEqual(response_get.json()['data']['totalTickets'], self.act_book_start.total_tickets)


# 以下为课上所做
class ActivityListUnit(TestCase):
    """
        对activity list接口的测试
    """

    def setUp(self):
        self.user = DjangoUser.objects.create(username='username', password='password')
        self.act_delete = Activity.objects.create(name='Activity_delete', key='delete',
                                                  description='This is activity A1',
                                                  start_time=datetime.datetime(2018, 10, 21, 18, 25, 29,
                                                                               tzinfo=timezone.utc),
                                                  end_time=datetime.datetime(2018, 10, 22, 18, 25, 29,
                                                                             tzinfo=timezone.utc),
                                                  place='place_A1',
                                                  book_start=datetime.datetime(2018, 10, 18, 10, 25, 29,
                                                                               tzinfo=timezone.utc),
                                                  book_end=datetime.datetime(2018, 10, 19, 10, 25, 29,
                                                                             tzinfo=timezone.utc),
                                                  total_tickets=1000,
                                                  status=Activity.STATUS_DELETED,
                                                  pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                                  remain_tickets=999)
        self.act_save = Activity.objects.create(name='Activity_save', key='save',
                                                description='This is activity A2',
                                                start_time=datetime.datetime(2018, 10, 21, 18, 25, 29,
                                                                             tzinfo=timezone.utc),
                                                end_time=datetime.datetime(2018, 10, 22, 18, 25, 29,
                                                                           tzinfo=timezone.utc),
                                                place='place_A1',
                                                book_start=datetime.datetime(2018, 10, 18, 10, 25, 29,
                                                                             tzinfo=timezone.utc),
                                                book_end=datetime.datetime(2018, 10, 19, 10, 25, 29,
                                                                           tzinfo=timezone.utc),
                                                total_tickets=1000,
                                                status=Activity.STATUS_SAVED,
                                                pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                                remain_tickets=999)
        self.act_publish = Activity.objects.create(name='Activity_publish', key='publish',
                                                   description='This is activity A1',
                                                   start_time=datetime.datetime(2018, 10, 21, 18, 25, 29,
                                                                                tzinfo=timezone.utc),
                                                   end_time=datetime.datetime(2018, 10, 22, 18, 25, 29,
                                                                              tzinfo=timezone.utc),
                                                   place='place_A1',
                                                   book_start=datetime.datetime(2018, 10, 18, 10, 25, 29,
                                                                                tzinfo=timezone.utc),
                                                   book_end=datetime.datetime(2018, 10, 19, 10, 25, 29,
                                                                              tzinfo=timezone.utc),
                                                   total_tickets=1000,
                                                   status=Activity.STATUS_PUBLISHED,
                                                   pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                                   remain_tickets=999)

    def test_fetch_list_without_login(self):
        response = self.client.get('/api/a/activity/list/')
        self.assertNotEqual(response.json()['code'], 0)

    def test_fetch_list_with_login(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/a/activity/list/')
        self.assertEqual(len(response.json()['data']), 2)
        for record in response.json()['data']:
            self.assertGreaterEqual(record['id'], 0)


class ActivityDeleteUnit(TestCase):
    """
        对activity delete接口的测试
        疑问1：应该修改delete函数，不应该直接删除数据库中的记录
    """

    def setUp(self):
        self.user = DjangoUser.objects.create(username='username', password='password')
        self.act_delete = Activity.objects.create(name='Activity_delete', key='delete',
                                                  description='This is activity A1',
                                                  start_time=datetime.datetime(2018, 10, 21, 18, 25, 29,
                                                                               tzinfo=timezone.utc),
                                                  end_time=datetime.datetime(2018, 10, 22, 18, 25, 29,
                                                                             tzinfo=timezone.utc),
                                                  place='place_A1',
                                                  book_start=datetime.datetime(2018, 10, 18, 10, 25, 29,
                                                                               tzinfo=timezone.utc),
                                                  book_end=datetime.datetime(2018, 10, 19, 10, 25, 29,
                                                                             tzinfo=timezone.utc),
                                                  total_tickets=1000,
                                                  status=Activity.STATUS_DELETED,
                                                  pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                                  remain_tickets=999)
        self.act_save = Activity.objects.create(name='Activity_save', key='save',
                                                description='This is activity A2',
                                                start_time=datetime.datetime(2018, 10, 21, 18, 25, 29,
                                                                             tzinfo=timezone.utc),
                                                end_time=datetime.datetime(2018, 10, 22, 18, 25, 29,
                                                                           tzinfo=timezone.utc),
                                                place='place_A1',
                                                book_start=datetime.datetime(2018, 10, 18, 10, 25, 29,
                                                                             tzinfo=timezone.utc),
                                                book_end=datetime.datetime(2018, 10, 19, 10, 25, 29,
                                                                           tzinfo=timezone.utc),
                                                total_tickets=1000,
                                                status=Activity.STATUS_SAVED,
                                                pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                                remain_tickets=999)
        self.act_publish = Activity.objects.create(name='Activity_publish', key='publish',
                                                   description='This is activity A1',
                                                   start_time=datetime.datetime(2018, 10, 21, 18, 25, 29,
                                                                                tzinfo=timezone.utc),
                                                   end_time=datetime.datetime(2018, 10, 22, 18, 25, 29,
                                                                              tzinfo=timezone.utc),
                                                   place='place_A1',
                                                   book_start=datetime.datetime(2018, 10, 18, 10, 25, 29,
                                                                                tzinfo=timezone.utc),
                                                   book_end=datetime.datetime(2018, 10, 19, 10, 25, 29,
                                                                              tzinfo=timezone.utc),
                                                   total_tickets=1000,
                                                   status=Activity.STATUS_PUBLISHED,
                                                   pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                                   remain_tickets=999)

    def test_delete_without_login(self):
        response = self.client.post('/api/a/activity/delete/', {
            'id': self.act_save.id,
        })
        self.assertNotEqual(response.json()['code'], 0)

    def test_delete_with_wrong_id(self):
        self.client.force_login(self.user)
        response = self.client.post('/api/a/activity/delete/', {
            'id': 99999,
        })
        self.assertNotEqual(response.json()['code'], 0)

    def test_delete_deleted_activity(self):
        self.client.force_login(self.user)
        response = self.client.post('/api/a/activity/delete/', {
            'id': self.act_delete,
        })
        self.assertNotEqual(response.json()['code'], 0)

    def test_delete_saved_activity(self):
        self.client.force_login(self.user)
        self.client.post('/api/a/activity/delete/', {
            'id': self.act_save.id,
        })
        deleted_act = Activity.objects.get(id=self.act_save.id)
        self.assertEqual(deleted_act.status, Activity.STATUS_DELETED)

    def test_delete_published_activity(self):
        self.client.force_login(self.user)
        self.client.post('/api/a/activity/delete/', {
            'id': self.act_publish.id,
        })
        deleted_act = Activity.objects.get(id=self.act_publish.id)
        self.assertEqual(deleted_act.status, Activity.STATUS_DELETED)


class ActivityCreateUnit(TestCase):
    """
        对activity create接口的测试
        疑问1： 上传的数据如何转换称时间戳？
    """

    def setUp(self):
        self.user = DjangoUser.objects.create(username='username', password='password')

    def test_create_without_login(self):
        response = self.client.post('/api/a/activity/create/', {
            'name': 'test_test1',
            'key': 'test_key1',
            'description': 'test_desc1',
            'place': 'test_place1',
            'picUrl': '',
            'startTime': '2018-10-19T08:00:00.000Z',
            'endTime': '2018-10-20T08:00:00.000Z',
            'bookStart': '2018-10-17T08:00:00.000Z',
            'bookEnd': '2018-10-18T08:00:00.000Z',
            'totalTickets': 1000,
            'status': 0,
        })
        self.assertNotEqual(response.json()['code'], 0)

    def test_create_with_login(self):
        self.client.force_login(self.user)
        response = self.client.post('/api/a/activity/create/', {
            'name': 'test_name1',
            'key': 'test_key1',
            'description': 'test_desc1',
            'place': 'test_place1',
            'picUrl': '',
            'startTime': '2018-10-19T08:00:00.000Z',
            'endTime': '2018-10-20T08:00:00.000Z',
            'bookStart': '2018-10-17T08:00:00.000Z',
            'bookEnd': '2018-10-18T08:00:00.000Z',
            'totalTickets': 1000,
            'status': 0,
        })
        self.assertEqual(response.json()['code'], 0)
        created_act = Activity.objects.get(name='test_name1', key='test_key1')
        self.assertEqual(created_act.place, 'test_place1')
        self.assertEqual(created_act.id, response.json()['data']['id'])


class ActivityCheckinUnit(TestCase):
    """
        对activity checkin接口的测试
        疑问1：未发布也能检票？
        疑问2：错误的票-人对应，是直接发挥非0code错误还是返回一个可读的信息？
    """

    def setUp(self):
        self.manager_user = DjangoUser.objects.create(username='username', password='password')
        self.act_save = Activity.objects.create(name='Activity_save', key='save',
                                                description='This is activity A2',
                                                start_time=datetime.datetime(2018, 10, 21, 18, 25, 29,
                                                                             tzinfo=timezone.utc),
                                                end_time=datetime.datetime(2018, 10, 22, 18, 25, 29,
                                                                           tzinfo=timezone.utc),
                                                place='place_A1',
                                                book_start=datetime.datetime(2018, 10, 10, 10, 25, 29,
                                                                             tzinfo=timezone.utc),
                                                book_end=datetime.datetime(2018, 10, 19, 10, 25, 29,
                                                                           tzinfo=timezone.utc),
                                                total_tickets=1000,
                                                status=Activity.STATUS_SAVED,
                                                pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                                remain_tickets=999)
        self.act_publish = Activity.objects.create(name='Activity_publish', key='publish',
                                                   description='This is activity A1',
                                                   start_time=datetime.datetime(2018, 10, 21, 18, 25, 29,
                                                                                tzinfo=timezone.utc),
                                                   end_time=datetime.datetime(2018, 10, 22, 18, 25, 29,
                                                                              tzinfo=timezone.utc),
                                                   place='place_A1',
                                                   book_start=datetime.datetime(2018, 10, 10, 10, 25, 29,
                                                                                tzinfo=timezone.utc),
                                                   book_end=datetime.datetime(2018, 10, 19, 10, 25, 29,
                                                                              tzinfo=timezone.utc),
                                                   total_tickets=1000,
                                                   status=Activity.STATUS_PUBLISHED,
                                                   pic_url='http://47.95.120.180/media/img/8e7cecab01.jpg',
                                                   remain_tickets=999)
        self.user1 = User.objects.create(open_id='open_id_first', student_id='student_id_first')
        self.user2 = User.objects.create(open_id='open_id_second', student_id='student_id_second')
        self.ticket_valid = Ticket.objects.create(student_id='student_id_first', unique_id='unique_id_first',
                                                  activity_id=self.act_save.id, status=Ticket.STATUS_VALID)
        self.ticket_used = Ticket.objects.create(student_id='student_id_second', unique_id='unique_id_second',
                                                 activity_id=self.act_publish.id, status=Ticket.STATUS_USED)
        self.ticket_cancelled = Ticket.objects.create(student_id='student_id_second', unique_id='unique_id_third',
                                                      activity_id=self.act_publish.id, status=Ticket.STATUS_CANCELLED)

    def test_check_in_without_login(self):
        response = self.client.post('/api/a/activity/checkin/', {
            'actId': self.act_publish.id,
            'ticket': self.ticket_used.unique_id,
        })
        self.assertEqual(response.json()['code'], 0)

    def test_check_in_with_wrong_act_id(self):
        self.client.force_login(self.manager_user)
        response = self.client.post('/api/a/activity/checkin/', {
            # 'actId': self.act_publish.id,
            'ticket': self.ticket_used.unique_id,
            'actId': 123123,
        })
        self.assertNotEqual(response.json()['code'], 0)

    def test_check_in_with_wrong_unique_id(self):
        self.client.force_login(self.manager_user)
        response = self.client.post('/api/a/activity/checkin/', {
            'actId': self.act_publish.id,
            'ticket': '123123'
            # 'ticket': self.ticket2.unique_id,
        })
        self.assertNotEqual(response.json()['code'], 0)

    def test_check_in_with_wrong_student_id(self):
        self.client.force_login(self.manager_user)
        response = self.client.post('/api/a/activity/checkin/', {
            'actId': self.act_publish.id,
            'studentId': 'student_id_second',
        })
        self.assertNotEqual(response.json()['code'], 0)

    def test_check_in_with_used_ticket(self):
        self.client.force_login(self.manager_user)
        response = self.client.post('/api/a/activity/checkin/', {
            'actId': self.act_publish.id,
            'ticket': self.ticket_used.unique_id,
        })
        self.assertNotEqual(response.json()['code'], 0)

    def test_check_in_with_cancelled_ticket(self):
        self.client.force_login(self.manager_user)
        response = self.client.post('/api/a/activity/checkin/', {
            'actId': self.act_publish.id,
            'ticket': self.ticket_cancelled.unique_id,
        })
        self.assertNotEqual(response.json()['code'], 0)

    def test_check_in_with_valid_ticket(self):
        self.client.force_login(self.manager_user)
        response = self.client.post('/api/a/activity/checkin/', {
            'actId': self.act_save.id,
            'ticket': self.ticket_valid.unique_id,
        })
        self.assertEqual(response.json()['code'], 0)
