from django.test import TestCase
import datetime
from django.utils import timezone
from wechat.models import *
from django.test import Client

# Create your tests here.

class UserBindTestCase(TestCase):
	def setUp(self):
		User.objects.create(open_id='student',student_id='2016013666')
		User.objects.create(open_id='social_people')

		User.objects.create(open_id='right_bind')
		User.objects.create(open_id='wrong_bind')
		User.objects.create(open_id='has_bind',student_id='2016013667')

	#def tearDown(self):
		#a = User.objects.get(open_id='student')
		#a.delete()
		#User.objects.get(open_id='social_people').delete()
		#User.objects.get(open_id='right_bind').delete()
		#User.objects.get(open_id='wrong_bind').delete()
		#User.objects.get(open_id='has_bind').delete()

	def test_get_student(self):
		client_student = Client()
		student = User.objects.get(open_id='student')

		res_student = client_student.get('/api/u/user/bind/?', {'openid': student.open_id})
		self.assertEqual(res_student.json()['data'], '2016013666')

	def test_get_social(self):
		res_social = Client().get('/api/u/user/bind/?', {'openid': 'social_people'})
		self.assertEqual(res_social.json()['data'], '')

	def test_get_not_exist(self):
		res = Client().get('/api/u/user/bind/?', {'openid': 'not_exist_'})
		self.assertNotEqual(res.json()['code'], 0)

	def test_post_right_bind(self):
		res = Client().post('/api/u/user/bind/', {'openid': 'right_bind', 'student_id': '2016013699', 'password': 'whatever'})
		self.assertEqual(res.json()['code'], 0)

	def test_post_no_passwd(self):
		res = Client().post('/api/u/user/bind/', {'openid': 'wrong_bind', 'student_id': '2016013699'})
		self.assertNotEqual(res.json()['code'], 0)

	def test_post_no_student_id(self):
		res = Client().post('/api/u/user/bind/', {'openid': 'wrong_bind'})
		self.assertNotEqual(res.json()['code'], 0)

	def test_post_conflict(self):
		res = Client().post('/api/u/user/bind/', {'openid': 'wrong_bind', 'student_id': '2016013666', 'password':'what_ever'})
		self.assertNotEqual(res.json()['code'], 0)

	def test_post_not_exist(self):
		res = Client().post('/api/u/user/bind/', {'openid': 'not_exist_', 'student_id': '2016013999', 'password':'what_ever'})
		self.assertNotEqual(res.json()['code'], 0)

	def test_post_has_bind(self):
		res = Client().post('/api/u/user/bind/', {'openid': 'has_bind', 'student_id': '2016013210', 'password': 'whatever'})
		self.assertNotEqual(res.json()['code'], 0)

class UserActivityDetailTestCase(TestCase):
	def setUp(self):
		Activity.objects.create(name = 'Activity_A1', key = 'A1', 
    description = 'This is activity A1',
    start_time = datetime.datetime(2018, 10, 21, 18, 25, 29, tzinfo=timezone.utc),
    end_time = datetime.datetime(2018, 10, 22, 18, 25, 29, tzinfo=timezone.utc),
    place = 'place_A1',
    book_start = datetime.datetime(2018, 10, 18, 10, 25, 29, tzinfo=timezone.utc),
    book_end = datetime.datetime(2018, 10, 10, 10, 25, 29, tzinfo=timezone.utc),
    total_tickets = 1000,
    status = Activity.STATUS_PUBLISHED,
    pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
    remain_tickets = 999)

		Activity.objects.create(name = 'Activity_A2', key = 'A2', 
    description = 'This is activity A2',
    start_time = datetime.datetime(2018, 10, 21, 18, 25, 29, tzinfo=timezone.utc),
    end_time = datetime.datetime(2018, 10, 22, 18, 25, 29, tzinfo=timezone.utc),
    place = 'place_A2',
    book_start = datetime.datetime(2018, 10, 18, 10, 25, 29, tzinfo=timezone.utc),
    book_end = datetime.datetime(2018, 10, 10, 10, 25, 29, tzinfo=timezone.utc),
    total_tickets = 1000,
    status = Activity.STATUS_SAVED,
    pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
    remain_tickets = 999)


		Activity.objects.create(name = 'Activity_A3', key = 'A3',
    description = 'This is activity A3',
    start_time = datetime.datetime(2018, 10, 21, 18, 25, 29, tzinfo=timezone.utc),
    end_time = datetime.datetime(2018, 10, 22, 18, 25, 29, tzinfo=timezone.utc),
    place = 'place_A3',
    book_start = datetime.datetime(2018, 10, 18, 10, 25, 29, tzinfo=timezone.utc),
    book_end = datetime.datetime(2018, 10, 10, 10, 25, 29, tzinfo=timezone.utc),
    total_tickets = 1000,
    status = Activity.STATUS_DELETED,
    pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
    remain_tickets = 999)

	def test_get_right(self):
		res = self.client.get('/api/u/activity/detail/', {'id': 1})
		self.assertEqual(res.json()['code'], 0)

	def test_get_not_exist(self):
		res = self.client.get('/api/u/activity/detail/', {'id': 4})
		self.assertNotEqual(res.json()['code'], 0)

	def test_get_no_id(self):
		res = self.client.get('/api/u/activity/detail/')
		self.assertNotEqual(res.json()['code'], 0)

	def test_get_saved(self):
		res = self.client.get('/api/u/activity/detail/', {'id': 2})
		self.assertNotEqual(res.json()['code'], 0)

	def test_get_deleted(self):
		res = self.client.get('/api/u/activity/detail/', {'id': 3})
		self.assertNotEqual(res.json()['code'], 0)

