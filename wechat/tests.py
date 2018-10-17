from django.test import TestCase
import datetime,time
from django.utils import timezone
from wechat.models import *
from django.test import Client
from WeChatTicket import settings

import lxml.etree as ET

'''
wechat POST:
/wechat?signature=<content>&timestamp=<timestamp>&nonce=<int_num>&openid=<openid>
like above, you can use 
	settings.IGNORE_WECHAT_SIGNATURE = True
to turn off the _check_signature function, so that you don't need to write that.

A text xml example:(in django, request.body should be a byte string with content like this.)
<xml>
	<ToUserName><![CDATA[gh_9caf75c794ee]]></ToUserName>
	<FromUserName><![CDATA[openid]]></FromUserName>
	<CreateTime>timestamp</CreateTime>
	<MsgType><![CDATA[text]]></MsgType>
	<Content><![CDATA[\xe8\x8d\x89\xe6\x8b\x9f]]></Content>
	<MsgId>6613267746628708547</MsgId>
</xml>

A click event:
<xml>
    <ToUserName><![CDATA[gh_9caf75c794ee]]></ToUserName>
    <FromUserName><![CDATA[oOTV-5uRdpJ9vW6AnupsFRzWjgUg]]></FromUserName>
    <CreateTime>1539772572</CreateTime>
    <MsgType><![CDATA[event]]></MsgType>
    <Event><![CDATA[CLICK]]></Event>
    <EventKey><![CDATA[SERVICE_BOOK_WHAT]]></EventKey>
</xml>

'''

def generateTextXml(ToUserName, openid, Content, MsgId):
	root = ET.Element('xml')

	to_user = ET.SubElement(root, 'ToUserName')
	from_user = ET.SubElement(root, 'FromUserName')
	create_time = ET.SubElement(root, 'CreateTime')
	content = ET.SubElement(root, 'Content')
	msg_type = ET.SubElement(root, 'MsgType')
	msg_id = ET.SubElement(root, 'MsgId')

	to_user.text = ET.CDATA(ToUserName)
	from_user.text = ET.CDATA(openid)
	create_time.text = str(int(time.mktime(datetime.datetime.now().timetuple())))
	content.text = ET.CDATA(Content)
	msg_type.text = ET.CDATA('text')
	msg_id.text = str(MsgId)

	return ET.tostring(root, encoding='utf-8')

def generateClickXml(ToUserName, openid, EventKey):
	root = ET.Element('xml')

	to_user = ET.SubElement(root, 'ToUserName')
	from_user = ET.SubElement(root, 'FromUserName')
	create_time = ET.SubElement(root, 'CreateTime')
	event = ET.SubElement(root, 'Event')
	msg_type = ET.SubElement(root, 'MsgType')
	event_key = ET.SubElement(root, 'EventKey')

	to_user.text = ET.CDATA(ToUserName)
	from_user.text = ET.CDATA(openid)
	create_time.text = str(int(time.mktime(datetime.datetime.now().timetuple())))
	msg_type.text = ET.CDATA('event')
	event.text = ET.CDATA('CLICK')
	msg_id.text = ET.CDATA(str(EventKey))

	return ET.tostring(root, encoding='utf-8')

class UserBookWhatHandlerTest(TestCase):
	def setUp(self):
		settings.IGNORE_WECHAT_SIGNATURE = True
		User.objects.create(open_id='student',student_id='2016013666')
		User.objects.create(open_id='social_people')
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

	def isReplyNews(res, newscount):
		self.assertTure(newscount > 0)

		self.assertEqual(res.status_code,200)
		root_elem = ET.fromstring(res.content)
		self.assertEqual(root_elem.tag == 'xml')
		
		children = root_elem.getchildren()
		Tags = []

		for child in children:
			Tags.append(child.tag)

		self.assertIs('MsgType' in Tags, True)
		self.assertIs('Articles' in Tags, True)
		self.assertIs('ArticleCount' in Tags, True)

		for child in children:
			if child.tag == 'MsgType':
				self.assertEqual(child.text, 'news')
			if child.tag == 'ArticleCount':
				self.assertEqual(child.text, str(newscount))

	def isReplyText(res):
		self.assertEqual(res.status_code,200)
		root_elem = ET.fromstring(res.content)
		self.assertEqual(root_elem.tag == 'xml')
		
		children = root_elem.getchildren()
		Tags = []

		for child in children:
			Tags.append(child.tag)

		self.assertIs('MsgType' in Tags, True)

		for child in children:
			if child.tag == '':
				self.assertEqual(child.text, 'text')

	def test_post_right_text(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student', '抢啥', 123456))

		self.isReplyNews(res, 1)


	def test_post_right_click(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'student', 'SERVICE_BOOK_WHAT'))

		self.isReplyNews(res, 1)

	def test_post_no_actvity(self):
		Activity.objects.get(key='A1').delete()
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'student', 'SERVICE_BOOK_WHAT'))

		self.isReplyText(res)