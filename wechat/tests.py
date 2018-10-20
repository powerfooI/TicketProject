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

class customTestCase(TestCase):
	def isReplyNews(self, res, newscount):
		self.assertIs(newscount > 0, True)

		self.assertEqual(res.status_code,200)
		root_elem = ET.fromstring(res.content)
		self.assertEqual(root_elem.tag,'xml')
		
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

	def isReplyText(self, res, contain_content = ''):
		self.assertEqual(res.status_code,200)
		root_elem = ET.fromstring(res.content)
		self.assertEqual(root_elem.tag,'xml')
		
		children = root_elem.getchildren()
		Tags = []

		for child in children:
			Tags.append(child.tag)

		self.assertIs('MsgType' in Tags, True)
		self.assertIs('Content' in Tags, True)

		for child in children:
			if child.tag == 'MsgType':
				self.assertEqual(child.text, 'text')
			if child.tag == 'Content':	
				#print('==============')
				#print(contain_content)
				#print(child.text)
				#print('==============')
				self.assertIs(contain_content in child.text, True)

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

	#return
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
	event_key.text = ET.CDATA(str(EventKey))

	#return
	return ET.tostring(root, encoding='utf-8')

class UserBookingActivityHandlerTest(customTestCase):
	# # 处理文本信息的情况
	# # 处理点击事件的情况
	# 用户未有绑定
	# 抢票一个不存在的活动
	# 抢票一个删除的活动
	# 抢票一个没有发布的活动
	# 抢票一个发布的，没开始抢票的活动
	# 抢票一个发布的，结束抢票的活动
	# 抢票一个发布的，正在抢票的活动，但是没有余票的活动
	# 抢票一个发布的，正在抢票的活动，有余票的活动，但是已抢过同一张票了，抢过的票退了
	# 抢票一个发布的，正在抢票的活动，有余票的活动，但是已抢过同一张票了，抢过的票用了
	# 抢票一个发布的，正在抢票的活动，有余票的活动，但是已抢过同一张票了，抢过的票没用没退了
	# 抢票一个发布的，正在抢票的活动，有余票的活动，但是已抢过另一张票了
	# 抢票一个发布的，正在抢票的活动，有余票的活动，但是还没有抢过票

	def setUp(self):
		settings.IGNORE_WECHAT_SIGNATURE = True

		# A1
		self.act_saved_but_not_published = Activity.objects.create(
			name        = 'Activity_A1', 
			key         = 'A1', 
			description = 'This is activity A1',
			start_time  = datetime.datetime(2019, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
			end_time    = datetime.datetime(2019, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
			place       = 'place_A1',
			book_start  = datetime.datetime(2018, 12, 1, 0, 0, 0, tzinfo=timezone.utc),
			book_end    = datetime.datetime(2018, 12, 2, 0, 0, 0, tzinfo=timezone.utc),
			total_tickets = 1000,
			status      = Activity.STATUS_SAVED, # !
			pic_url     = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
			remain_tickets = 1000
		)

		# A2
		self.act_deleted = Activity.objects.create(
			name        = 'Activity_A2', 
			key         = 'A2', 
			description = 'This is activity A2',
			start_time  = datetime.datetime(2019, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
			end_time    = datetime.datetime(2019, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
			place       = 'place_A2',
			book_start  = datetime.datetime(2018, 12, 1, 0, 0, 0, tzinfo=timezone.utc),
			book_end    = datetime.datetime(2018, 12, 2, 0, 0, 0, tzinfo=timezone.utc),
			total_tickets = 1000,
			status      = Activity.STATUS_DELETED, # !
			pic_url     = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
			remain_tickets = 1000
		)

		# A3
		self.act_published_but_it_is_to_early_to_book = Activity.objects.create(
			name        = 'Activity_A3', 
			key         = 'A3', 
			description = 'This is activity A3',
			start_time  = datetime.datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
			end_time    = datetime.datetime(2021, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
			place       = 'place_A3',
			book_start  = datetime.datetime(2020, 12, 1, 0, 0, 0, tzinfo=timezone.utc), # !
			book_end    = datetime.datetime(2020, 12, 2, 0, 0, 0, tzinfo=timezone.utc),
			total_tickets = 1000,
			status      = Activity.STATUS_PUBLISHED, # !
			pic_url     = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
			remain_tickets = 1000
		)

		# A4
		self.act_published_but_it_is_to_late_to_book = Activity.objects.create(
			name        = 'Activity_A4', 
			key         = 'A4', 
			description = 'This is activity A4',
			start_time  = datetime.datetime(2019, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
			end_time    = datetime.datetime(2019, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
			place       = 'place_A4',
			book_start  = datetime.datetime(2012, 12, 1, 0, 0, 0, tzinfo=timezone.utc),
			book_end    = datetime.datetime(2012, 12, 2, 0, 0, 0, tzinfo=timezone.utc), # !
			total_tickets = 1000,
			status      = Activity.STATUS_PUBLISHED, # !
			pic_url     = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
			remain_tickets = 1000
		)

		# A5
		self.act_published_and_it_is_time_to_book_without_remain_tickets = Activity.objects.create(
			name        = 'Activity_A5', 
			key         = 'A5', 
			description = 'This is activity A5',
			start_time  = datetime.datetime(2020, 12, 1, 0, 0, 0, tzinfo=timezone.utc),
			end_time    = datetime.datetime(2020, 12, 2, 0, 0, 0, tzinfo=timezone.utc),
			place       = 'place_A5',
			book_start  = datetime.datetime(2012, 12, 1, 0, 0, 0, tzinfo=timezone.utc), # !
			book_end    = datetime.datetime(2019, 12, 2, 0, 0, 0, tzinfo=timezone.utc), # !
			total_tickets = 1000,
			status      = Activity.STATUS_PUBLISHED, # !
			pic_url     = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
			remain_tickets = 0 # !
		)

		# A6
		self.act_published_and_it_is_time_to_book_with_remain_tickets = Activity.objects.create(
			name        = 'Activity_A6', 
			key         = 'A6', 
			description = 'This is activity A6',
			start_time  = datetime.datetime(2020, 12, 1, 0, 0, 0, tzinfo=timezone.utc),
			end_time    = datetime.datetime(2020, 12, 2, 0, 0, 0, tzinfo=timezone.utc),
			place       = 'place_A6',
			book_start  = datetime.datetime(2012, 12, 1, 0, 0, 0, tzinfo=timezone.utc), # !
			book_end    = datetime.datetime(2019, 12, 2, 0, 0, 0, tzinfo=timezone.utc), # !
			total_tickets = 1000,
			status      = Activity.STATUS_PUBLISHED, # !
			pic_url     = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
			remain_tickets = 900 # !
		)

		# 没有票的同志
		User.objects.create(open_id='sad_man_1', student_id='2015080045')

		# 抢票一个发布的，正在抢票的活动，有余票的活动，但是已抢过同一张票了，抢过的票退了
		User.objects.create(open_id='gay_dog_1', student_id='2015080046') 
		Ticket.objects.create(
			student_id='2015080046', 
			unique_id='111111', 
			activity=self.act_published_and_it_is_time_to_book_with_remain_tickets, 
			status=Ticket.STATUS_CANCELLED
		)

		# 抢票一个发布的，正在抢票的活动，有余票的活动，但是已抢过同一张票了，抢过的票用了
		User.objects.create(open_id='gay_dog_2', student_id='2015080047') 
		Ticket.objects.create(
			student_id='2015080047', 
			unique_id='222222', 
			activity=self.act_published_and_it_is_time_to_book_with_remain_tickets, 
			status=Ticket.STATUS_USED
		)

		# 抢票一个发布的，正在抢票的活动，有余票的活动，但是已抢过同一张票了，抢过的票没用没退了
		User.objects.create(open_id='gay_dog_3', student_id='2015080048') 
		Ticket.objects.create(
			student_id='2015080048', 
			unique_id='333333', 
			activity=self.act_published_and_it_is_time_to_book_with_remain_tickets, 
			status=Ticket.STATUS_VALID
		)

		# 抢票一个发布的，正在抢票的活动，有余票的活动，但是已抢过另一张票了
		User.objects.create(open_id='gay_dog_4', student_id='2015080049')
		Ticket.objects.create(
			student_id='2015080049', 
			unique_id='444444', 
			activity=self.act_published_and_it_is_time_to_book_without_remain_tickets, 
			status=Ticket.STATUS_VALID
		)


	def test_post_text_not_bind(self):
		User.objects.create(open_id='social_people_1')
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'social_people_1', '抢票 A1', 123456))
		self.isReplyText(res, '点此绑定学号')


	def test_post_click_not_bind(self):
		User.objects.create(open_id='social_people_2')
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'social_people_2', 
				'BOOKING_ACTIVITY_' + str(self.act_saved_but_not_published.id)))
		self.isReplyText(res, '点此绑定学号')


	def test_post_activity_not_existed(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'sad_man_1', '抢票 A100', 123456))

		self.isReplyText(res, '失败 】 对不起，这儿没有对应的活动:(')


	def test_post_activity_saved(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'sad_man_1', '抢票 A1', 123456))

		self.isReplyText(res, '失败 】 对不起，这儿没有对应的活动:(')


	def test_post_activity_deleted(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'sad_man_1', '抢票 A2', 123456))

		self.isReplyText(res, '失败 】 对不起，这儿没有对应的活动:(')


	def test_post_text_activity_too_early_to_book(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'sad_man_1', '抢票 A3', 123456))

		self.isReplyText(res, '失败 】 对不起，现在不是抢票时间:(')


	def test_post_click_activity_too_early_to_book(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'sad_man_1', 'BOOKING_ACTIVITY_' 
				+ str(self.act_published_but_it_is_to_early_to_book.id)))

		self.isReplyText(res, '失败 】 对不起，现在不是抢票时间:(')


	def test_post_text_activity_too_late_to_book(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'sad_man_1', '抢票 A4', 123456))

		self.isReplyText(res, '失败 】 对不起，现在不是抢票时间:(')


	def test_post_click_activity_too_late_to_book(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'sad_man_1', 'BOOKING_ACTIVITY_' 
				+ str(self.act_published_but_it_is_to_late_to_book.id)))

		self.isReplyText(res, '失败 】 对不起，现在不是抢票时间:(')


	def test_post_text_activity_without_remain_tickets(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'sad_man_1', '抢票 A5', 123456))

		self.isReplyText(res, '失败 】 对不起，已经没有余票了:(')


	def test_post_click_activity_without_remain_tickets(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'sad_man_1', 'BOOKING_ACTIVITY_' 
				+ str(self.act_published_and_it_is_time_to_book_without_remain_tickets.id)))

		self.isReplyText(res, '失败 】 对不起，已经没有余票了:(')


	## 。。。
	def test_post_text_user_has_the_same_ticket_cancelled(self):
		origin_remain = Activity.objects.get(key='A6').remain_tickets

		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'gay_dog_1', '抢票 A6', 123456))

		tick = Ticket.objects.get(
			student_id='2015080046', 
			activity=self.act_published_and_it_is_time_to_book_with_remain_tickets,
            status=Ticket.STATUS_VALID
		)
		self.assertEqual(tick.status, Ticket.STATUS_VALID)

		new_remain = Activity.objects.get(key='A6').remain_tickets
		self.assertEqual(new_remain - origin_remain, -1)

		tick.delete()


	def test_post_click_user_has_the_same_ticket_cancelled(self):
		origin_remain = Activity.objects.get(key='A6').remain_tickets

		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'gay_dog_1', 'BOOKING_ACTIVITY_' 
				+ str(self.act_published_and_it_is_time_to_book_with_remain_tickets.id)))

		tick = Ticket.objects.get(
			student_id='2015080046', 
			activity=self.act_published_and_it_is_time_to_book_with_remain_tickets,
            status=Ticket.STATUS_VALID
		)
		self.assertEqual(tick.status, Ticket.STATUS_VALID)

		new_remain = Activity.objects.get(key='A6').remain_tickets
		self.assertEqual(new_remain - origin_remain, -1)

		tick.delete()


	def test_post_text_user_has_the_same_ticket_used(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'gay_dog_2', '抢票 A6', 123456))

		self.isReplyText(res, '失败 】 请不要重复抢票')


	def test_post_click_user_has_the_same_ticket_used(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'gay_dog_2', 'BOOKING_ACTIVITY_' 
				+ str(self.act_published_and_it_is_time_to_book_with_remain_tickets.id)))

		self.isReplyText(res, '失败 】 请不要重复抢票')


	def test_post_text_user_has_the_same_ticket_valid(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'gay_dog_3', '抢票 A6', 123456))

		self.isReplyText(res, '失败 】 请不要重复抢票')


	def test_post_click_user_has_the_same_ticket_valid(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'gay_dog_3', 'BOOKING_ACTIVITY_' 
				+ str(self.act_published_and_it_is_time_to_book_with_remain_tickets.id)))

		self.isReplyText(res, '失败 】 请不要重复抢票')


	def test_post_text_user_has_other_tickets(self):
		origin_remain = Activity.objects.get(key='A6').remain_tickets

		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'gay_dog_4', '抢票 A6', 123456))
		self.isReplyNews(res, 1)

		tick = Ticket.objects.get(
			student_id='2015080049', 
			activity=self.act_published_and_it_is_time_to_book_with_remain_tickets
		)
		self.assertEqual(tick.status, Ticket.STATUS_VALID)

		new_remain = Activity.objects.get(key='A6').remain_tickets
		self.assertEqual(new_remain - origin_remain, -1)
		tick.delete()


	def test_post_click_user_has_other_tickets(self):
		origin_remain = Activity.objects.get(key='A6').remain_tickets

		res = res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'gay_dog_4', 'BOOKING_ACTIVITY_' 
				+ str(self.act_published_and_it_is_time_to_book_with_remain_tickets.id)))
		self.isReplyNews(res, 1)

		tick = Ticket.objects.get(
			student_id='2015080049', 
			activity=self.act_published_and_it_is_time_to_book_with_remain_tickets
		)
		self.assertEqual(tick.status, Ticket.STATUS_VALID)

		new_remain = Activity.objects.get(key='A6').remain_tickets
		self.assertEqual(new_remain - origin_remain, -1)
		tick.delete()


	def test_post_text_right(self):
		origin_remain = Activity.objects.get(key='A6').remain_tickets

		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'sad_man_1', '抢票 A6', 123456))
		self.isReplyNews(res, 1)

		tick = Ticket.objects.get(
			student_id='2015080045', 
			activity=self.act_published_and_it_is_time_to_book_with_remain_tickets
		)
		self.assertEqual(tick.status, Ticket.STATUS_VALID)

		new_remain = Activity.objects.get(key='A6').remain_tickets
		self.assertEqual(new_remain - origin_remain, -1)

		tick.delete()


	def test_post_click_right(self):
		origin_remain = Activity.objects.get(key='A6').remain_tickets

		res = res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'sad_man_1', 'BOOKING_ACTIVITY_' 
				+ str(self.act_published_and_it_is_time_to_book_with_remain_tickets.id)))
		self.isReplyNews(res, 1)

		tick = Ticket.objects.get(
			student_id='2015080045', 
			activity=self.act_published_and_it_is_time_to_book_with_remain_tickets
		)
		self.assertEqual(tick.status, Ticket.STATUS_VALID)

		new_remain = Activity.objects.get(key='A6').remain_tickets
		self.assertEqual(new_remain - origin_remain, -1)

		tick.delete()

class UserBookWhatHandlerTest(customTestCase):
	def setUp(self):
		settings.IGNORE_WECHAT_SIGNATURE = True
		User.objects.create(open_id='student',student_id='2016013666')
		User.objects.create(open_id='social_people')
		Activity.objects.create(name = 'Activity_A1', key = 'A1', 
		    description = 'This is activity A1',
		    start_time = datetime.datetime(2018, 10, 21, 18, 25, 29, tzinfo=timezone.utc),
		    end_time = datetime.datetime(2018, 10, 22, 18, 25, 29, tzinfo=timezone.utc),
		    place = 'place_A1',
			# 一直可以抢票的活动
		    book_start = datetime.datetime(2050, 10, 18, 10, 25, 29, tzinfo=timezone.utc),
		    book_end = datetime.datetime(2050, 10, 10, 10, 25, 29, tzinfo=timezone.utc),
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
        
		Activity.objects.create(name = 'Activity_A4', key = 'A4',
			description = 'This is activity A4',
			start_time = datetime.datetime(2018, 10, 21, 18, 25, 29, tzinfo=timezone.utc),
			end_time = datetime.datetime(2018, 10, 22, 18, 25, 29, tzinfo=timezone.utc),
			place = 'place_A4',
			book_start = datetime.datetime(2018, 7, 18, 10, 25, 29, tzinfo=timezone.utc),
			book_end = datetime.datetime(2018, 7, 10, 10, 25, 29, tzinfo=timezone.utc),
			total_tickets = 1000,
			status = Activity.STATUS_DELETED,
			pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
			remain_tickets = 999)

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

	def test_post_dont_show_pass_time(self):
		act = Activity.objects.get(key='A4')
		act.status = Activity.STATUS_PUBLISHED
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'student', 'SERVICE_BOOK_WHAT'))

		self.isReplyNews(res, 1)
		
	def test_post_no_actvity(self):
		Activity.objects.get(key='A1').delete()
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'student', 'SERVICE_BOOK_WHAT'))

		self.isReplyText(res, '没有活动')
        

class UserQueryTicketHandlerTest(customTestCase):
	def setUp(self):
		settings.IGNORE_WECHAT_SIGNATURE = True

		# 活动表只有公布的原因：认为不应该出现未发布就有票的情况或已经发了票但被删除的情况
		# 应该在抢票handlers的测试中出现，未发布活动不能抢票这一用例
		act_a1 = Activity.objects.create(name = 'Activity_A1', key = 'A1', 
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

		act_a3 = Activity.objects.create(name = 'Activity_A3', key = 'A3',
		    description = 'This is activity A3',
		    start_time = datetime.datetime(2018, 10, 21, 18, 25, 29, tzinfo=timezone.utc),
		    end_time = datetime.datetime(2018, 10, 22, 18, 25, 29, tzinfo=timezone.utc),
		    place = 'place_A3',
		    book_start = datetime.datetime(2018, 10, 18, 10, 25, 29, tzinfo=timezone.utc),
		    book_end = datetime.datetime(2018, 10, 10, 10, 25, 29, tzinfo=timezone.utc),
		    total_tickets = 1000,
		    status = Activity.STATUS_PUBLISHED,
		    pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
		    remain_tickets = 999)

		User.objects.create(open_id='student_two', student_id='2016013666')
		Ticket.objects.create(student_id='2016013666', unique_id='123456', activity=act_a1, status=Ticket.STATUS_VALID)
		Ticket.objects.create(student_id='2016013666', unique_id='123457', activity=act_a3, status=Ticket.STATUS_VALID)

	def test_post_not_bind(self):
		User.objects.create(open_id='social_people')
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'social_people', '查票', 123456))

		self.isReplyText(res, '点此绑定学号')

	def test_post_no_ticket(self):
		User.objects.create(open_id='student_none',student_id='2016013667')
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_none', '查票', 123456))

		self.isReplyText(res, '没有票')

	def test_post_two_tickets_text(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_two', '查票', 123456))

		self.isReplyNews(res, 2)

	def test_post_two_tickets_click(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'student_two', 'SERVICE_GET_TICKET'))

		self.isReplyNews(res, 2)

	def test_post_dont_show_ticket_cancelled(self):
		tick = Ticket.objects.get(unique_id = '123457')
		tick.status = Ticket.STATUS_CANCELLED
		tick.save()
		
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'student_two', 'SERVICE_GET_TICKET'))

		self.isReplyNews(res, 1)

	def test_post_dont_show_ticket_used(self):
		tick = Ticket.objects.get(unique_id = '123457')
		tick.status = Ticket.STATUS_USED
		tick.save()
		
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateClickXml('Toyou', 'student_two', 'SERVICE_GET_TICKET'))


		self.isReplyNews(res, 1)

class UserExtractTicketHandlerTest(customTestCase):
	# 取票只能回复消息
	def setUp(self):
		settings.IGNORE_WECHAT_SIGNATURE = True

		act_a1 = Activity.objects.create(name = 'Activity_A1', key = 'A1', 
		    description = 'This is activity A1',
		    start_time = datetime.datetime(2018, 10, 21, 18, 25, 29, tzinfo=timezone.utc),
		    # 此活动2050年结束。。。。应该一直都可以取票
		    end_time = datetime.datetime(2050, 10, 22, 18, 25, 29, tzinfo=timezone.utc),
		    place = 'place_A1',
		    book_start = datetime.datetime(2018, 10, 18, 10, 25, 29, tzinfo=timezone.utc),
		    book_end = datetime.datetime(2018, 10, 10, 10, 25, 29, tzinfo=timezone.utc),
		    total_tickets = 1000,
		    status = Activity.STATUS_PUBLISHED,
		    pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
		    remain_tickets = 999)

		# 此活动时间已过
		act_a2 = Activity.objects.create(name = 'Activity_A2', key = 'A2', 
		    description = 'This is activity A2',
		    start_time = datetime.datetime(2018, 8, 3, 18, 25, 29, tzinfo=timezone.utc),
		    end_time = datetime.datetime(2018, 8, 5, 18, 25, 29, tzinfo=timezone.utc),
		    place = 'place_A2',
		    book_start = datetime.datetime(2018, 8, 1, 10, 25, 29, tzinfo=timezone.utc),
		    book_end = datetime.datetime(2018, 8, 2, 10, 25, 29, tzinfo=timezone.utc),
		    total_tickets = 1000,
		    status = Activity.STATUS_PUBLISHED,
		    pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
		    remain_tickets = 999)

		User.objects.create(open_id='student_666', student_id='2016013666')
		Ticket.objects.create(student_id='2016013666', unique_id='123456', activity=act_a1, status=Ticket.STATUS_VALID)
		Ticket.objects.create(student_id='2016013666', unique_id='123457', activity=act_a2, status=Ticket.STATUS_USED)

	def test_post_not_bind(self):
		User.objects.create(open_id='social_people')
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'social_people', '取票 A1', 123456))

		self.isReplyText(res, '点此绑定学号')

	def test_post_no_activity(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '取票 A3', 123456))

		self.isReplyText(res, '失败 】 活动不存在')

	def test_post_activity_deleted(self):
		Activity.objects.create(name = 'Activity_A8', key = 'A8', 
		    description = 'This is activity A8',
		    start_time = datetime.datetime(2018, 8, 3, 18, 25, 29, tzinfo=timezone.utc),
		    end_time = datetime.datetime(2018, 8, 5, 18, 25, 29, tzinfo=timezone.utc),
		    place = 'place_A8',
		    book_start = datetime.datetime(2018, 8, 1, 10, 25, 29, tzinfo=timezone.utc),
		    book_end = datetime.datetime(2018, 8, 2, 10, 25, 29, tzinfo=timezone.utc),
		    total_tickets = 1000,
		    status = Activity.STATUS_DELETED,
		    pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
		    remain_tickets = 999)
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '取票 A8', 123456))

		self.isReplyText(res, '失败 】 活动不存在')

	def test_post_activity_saved(self):
		Activity.objects.create(name = 'Activity_A9', key = 'A9', 
		    description = 'This is activity A9',
		    start_time = datetime.datetime(2018, 8, 3, 18, 25, 29, tzinfo=timezone.utc),
		    end_time = datetime.datetime(2018, 8, 5, 18, 25, 29, tzinfo=timezone.utc),
		    place = 'place_A9',
		    book_start = datetime.datetime(2018, 8, 1, 10, 25, 29, tzinfo=timezone.utc),
		    book_end = datetime.datetime(2018, 8, 2, 10, 25, 29, tzinfo=timezone.utc),
		    total_tickets = 1000,
		    status = Activity.STATUS_SAVED,
		    pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
		    remain_tickets = 999)
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '取票 A9', 123456))

		self.isReplyText(res, '失败 】 活动不存在')

	def test_post_no_corresponding_ticket(self):
		Activity.objects.create(name = 'Activity_A10', key = 'A10', 
		    description = 'This is activity A10',
		    start_time = datetime.datetime(2018, 8, 3, 18, 25, 29, tzinfo=timezone.utc),
		    end_time = datetime.datetime(2018, 8, 5, 18, 25, 29, tzinfo=timezone.utc),
		    place = 'place_A10',
		    book_start = datetime.datetime(2018, 8, 1, 10, 25, 29, tzinfo=timezone.utc),
		    book_end = datetime.datetime(2018, 8, 2, 10, 25, 29, tzinfo=timezone.utc),
		    total_tickets = 1000,
		    status = Activity.STATUS_PUBLISHED,
		    pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
		    remain_tickets = 999)

		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '取票 A10', 123456))

		self.isReplyText(res, '失败 】 您没有此活动中未使用的票')

	def test_post_no_valid_ticket_used(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '取票 A2', 123456))

		self.isReplyText(res, '失败 】 您没有此活动中未使用的票')

	def test_post_no_valid_ticket_cancelled(self):
		tick = Ticket.objects.get(unique_id = '123457')
		tick.status = Ticket.STATUS_CANCELLED
		tick.save()
		
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '取票 A2', 123456))

		self.isReplyText(res, '失败 】 您没有此活动中未使用的票')

	def test_post_pass_time(self):
		tick = Ticket.objects.get(unique_id = '123457')
		tick.status = Ticket.STATUS_VALID
		tick.save()

		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '取票 A2', 123456))

		self.isReplyText(res, '失败 】 活动已经结束')

	def test_post_right(self):
		# 取票成功
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '取票 A1', 123456))
		
		#tick = Ticket.objects.get(unique_id='123456')

		#self.assertEqual(tick.status, Ticket.STATUS_USED)
		self.isReplyNews(res, 1)

class UserRefundTicketHandlerTest(customTestCase):
	# 退票只能回复消息
	def setUp(self):
		settings.IGNORE_WECHAT_SIGNATURE = True

		act_a1 = Activity.objects.create(name = 'Activity_A1', key = 'A1', 
		    description = 'This is activity A1',
		    start_time = datetime.datetime(2018, 10, 21, 18, 25, 29, tzinfo=timezone.utc),
		    # 此活动2050年结束。。。。应该一直都可以退票
		    end_time = datetime.datetime(2050, 10, 22, 18, 25, 29, tzinfo=timezone.utc),
		    place = 'place_A1',
		    book_start = datetime.datetime(2018, 10, 18, 10, 25, 29, tzinfo=timezone.utc),
		    book_end = datetime.datetime(2018, 10, 10, 10, 25, 29, tzinfo=timezone.utc),
		    total_tickets = 1000,
		    status = Activity.STATUS_PUBLISHED,
		    pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
		    remain_tickets = 999)

		# 此活动时间已过
		act_a2 = Activity.objects.create(name = 'Activity_A2', key = 'A2', 
		    description = 'This is activity A2',
		    start_time = datetime.datetime(2018, 8, 3, 18, 25, 29, tzinfo=timezone.utc),
		    end_time = datetime.datetime(2018, 8, 5, 18, 25, 29, tzinfo=timezone.utc),
		    place = 'place_A2',
		    book_start = datetime.datetime(2018, 8, 1, 10, 25, 29, tzinfo=timezone.utc),
		    book_end = datetime.datetime(2018, 8, 2, 10, 25, 29, tzinfo=timezone.utc),
		    total_tickets = 1000,
		    status = Activity.STATUS_PUBLISHED,
		    pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
		    remain_tickets = 999)

		User.objects.create(open_id='student_666', student_id='2016013666')
		Ticket.objects.create(student_id='2016013666', unique_id='123456', activity=act_a1, status=Ticket.STATUS_VALID)
		Ticket.objects.create(student_id='2016013666', unique_id='123457', activity=act_a2, status=Ticket.STATUS_USED)

	def test_post_not_bind(self):
		User.objects.create(open_id='social_people')
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'social_people', '退票 A1', 123456))

		self.isReplyText(res, '点此绑定学号')

	def test_post_no_activity(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '退票 A3', 123456))

		self.isReplyText(res, '失败 】 活动不存在')

	def test_post_activity_deleted(self):
		Activity.objects.create(name = 'Activity_A8', key = 'A8', 
		    description = 'This is activity A8',
		    start_time = datetime.datetime(2018, 8, 3, 18, 25, 29, tzinfo=timezone.utc),
		    end_time = datetime.datetime(2018, 8, 5, 18, 25, 29, tzinfo=timezone.utc),
		    place = 'place_A8',
		    book_start = datetime.datetime(2018, 8, 1, 10, 25, 29, tzinfo=timezone.utc),
		    book_end = datetime.datetime(2018, 8, 2, 10, 25, 29, tzinfo=timezone.utc),
		    total_tickets = 1000,
		    status = Activity.STATUS_DELETED,
		    pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
		    remain_tickets = 999)
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '退票 A8', 123456))

		self.isReplyText(res, '失败 】 活动不存在')

	def test_post_activity_saved(self):
		Activity.objects.create(name = 'Activity_A9', key = 'A9', 
		    description = 'This is activity A9',
		    start_time = datetime.datetime(2018, 8, 3, 18, 25, 29, tzinfo=timezone.utc),
		    end_time = datetime.datetime(2018, 8, 5, 18, 25, 29, tzinfo=timezone.utc),
		    place = 'place_A9',
		    book_start = datetime.datetime(2018, 8, 1, 10, 25, 29, tzinfo=timezone.utc),
		    book_end = datetime.datetime(2018, 8, 2, 10, 25, 29, tzinfo=timezone.utc),
		    total_tickets = 1000,
		    status = Activity.STATUS_SAVED,
		    pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
		    remain_tickets = 999)
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '退票 A9', 123456))

		self.isReplyText(res, '失败 】 活动不存在')

	def test_post_no_corresponding_ticket(self):
		Activity.objects.create(name = 'Activity_A10', key = 'A10', 
		    description = 'This is activity A10',
		    start_time = datetime.datetime(2018, 8, 3, 18, 25, 29, tzinfo=timezone.utc),
		    end_time = datetime.datetime(2018, 8, 5, 18, 25, 29, tzinfo=timezone.utc),
		    place = 'place_A10',
		    book_start = datetime.datetime(2018, 8, 1, 10, 25, 29, tzinfo=timezone.utc),
		    book_end = datetime.datetime(2018, 8, 2, 10, 25, 29, tzinfo=timezone.utc),
		    total_tickets = 1000,
		    status = Activity.STATUS_PUBLISHED,
		    pic_url = 'http://47.95.120.180/media/img/8e7cecab01.jpg',
		    remain_tickets = 999)

		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '退票 A10', 123456))

		self.isReplyText(res, '失败 】 您没有此活动中未使用的票')

	def test_post_no_valid_ticket_used(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '退票 A2', 123456))

		self.isReplyText(res, '失败 】 您没有此活动中未使用的票')

	def test_post_no_valid_ticket_cancelled(self):
		tick = Ticket.objects.get(unique_id = '123457')
		tick.status = Ticket.STATUS_CANCELLED
		tick.save()
		
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '退票 A2', 123456))

		self.isReplyText(res, '失败 】 您没有此活动中未使用的票')

	def test_post_pass_time(self):
		tick = Ticket.objects.get(unique_id = '123457')
		tick.status = Ticket.STATUS_VALID
		tick.save()

		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '退票 A2', 123456))

		self.isReplyText(res, '失败 】 活动已经结束')

	def test_post_right(self):
		# 退票成功
		origin_remain = Activity.objects.get(key='A1').remain_tickets
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'student_666', '退票 A1', 123456))

		self.isReplyNews(res, 1)
		tick = Ticket.objects.get(unique_id='123456')

		self.assertEqual(tick.status, Ticket.STATUS_CANCELLED)

		new_remain = Activity.objects.get(key='A1').remain_tickets
		self.assertEqual(new_remain - origin_remain, 1)
