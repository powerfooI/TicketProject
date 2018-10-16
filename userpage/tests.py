from django.test import TestCase

# Create your tests here.

from django.test import TestCase
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

	def tearDown(self):
		User.objects.all().delete()

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
		self.assertEqual(res.json()['code'], '-1')

	def test_post_right_bind(self):
		res = Client().post('/api/u/user/bind/', {'openid': 'right_bind', 'student_id': '2016013699', 'password': 'whatever'})
		self.assertEqual(res.json()['code'], '0')

	def test_post_no_passwd(self):
		res = Client().post('/api/u/user/bind/', {'openid': 'wrong_bind', 'student_id': '2016013699'})
		self.assertEqual(res.json()['code'], '-1')

	def test_post_no_student_id(self):
		res = Client().post('/api/u/user/bind/', {'openid': 'wrong_bind'})
		self.assertEqual(res.json()['code'], '-1')

	def test_post_conflict(self):
		res = Client().post('/api/u/user/bind/', {'openid': 'wrong_bind', 'student_id': '2016013666', 'password':'what_ever'})
		self.assertEqual(res.json()['code'], '-1')

	def test_post_not_exist(self):
		res = Client().post('/api/u/user/bind/', {'openid': 'not_exist_', 'student_id': '2016013999', 'password':'what_ever'})
		self.assertEqual(res.json()['code'], '-1')

	def test_post_has_bind(self):
		res = Client().post('/api/u/user/bind/', {'openid': has_bind, 'student_id': '2016013210', 'password': 'whatever'})
		self.assertEqual(res.json()['code'], '-1')

		

