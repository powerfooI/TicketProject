from django.test import TestCase
from wechat.models import *
from django.test import Client

# Create your tests here.

class UserBindTestCase(TestCase):
	def setUp(self):
		User.objects.create(open_id='student')
		User.objects.create(open_id='social_people', student_id='2016013666')

	def test_get_request(self):
		client_student = Client()
		client_social_people = Client()
		student = User.objects.get(open_id='student')
		social_people = User.objects.get(open_id='social_people')

		res_student = client_student.get('/api/u/user/bind/?', {'openid': student.open_id})
		self.assertEqual(res_student, '2016013666')
		res_social = client_social_people.get('/api/u/user/bind/?', {'openid': social_people.open_id})
		self.assertEqual(res_social, '')
