from django.test import TestCase

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
        act_saved_but_not_published = Activity.objects.create(
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
        act_deleted = Activity.objects.create(
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
        act_published_but_it_is_to_early_to_book = Activity.objects.create(
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
        act_published_but_it_is_to_late_to_book = Activity.objects.create(
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
        act_published_and_it_is_time_to_book_without_remain_tickets = Activity.objects.create(
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
        act_published_and_it_is_time_to_book_with_remain_tickets = Activity.objects.create(
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
            activity=act_published_and_it_is_time_to_book_with_remain_tickets, 
            status=Ticket.STATUS_CANCELLED
        )

        # 抢票一个发布的，正在抢票的活动，有余票的活动，但是已抢过同一张票了，抢过的票用了
        User.objects.create(open_id='gay_dog_2', student_id='2015080047') 
        Ticket.objects.create(
            student_id='2015080047', 
            unique_id='222222', 
            activity=act_published_and_it_is_time_to_book_with_remain_tickets, 
            status=Ticket.STATUS_USED
        )

        # 抢票一个发布的，正在抢票的活动，有余票的活动，但是已抢过同一张票了，抢过的票没用没退了
        User.objects.create(open_id='gay_dog_3', student_id='2015080048') 
        Ticket.objects.create(
            student_id='2015080048', 
            unique_id='333333', 
            activity=act_published_and_it_is_time_to_book_with_remain_tickets, 
            status=Ticket.STATUS_VALID
        )

        # 抢票一个发布的，正在抢票的活动，有余票的活动，但是已抢过另一张票了
        User.objects.create(open_id='gay_dog_4', student_id='2015080049')
        Ticket.objects.create(
            student_id='2015080049', 
            unique_id='444444', 
            activity=act_published_and_it_is_time_to_book_without_remain_tickets, 
            status=Ticket.STATUS_VALID
        )

### 》》》》》》》》》》》》》》 并未处理点击事件

    def test_post_not_bind(self):
		User.objects.create(open_id='social_people')
        for i in range(6):
            res = self.client.post('/wechat/', 
                content_type='application/xml', 
                data=generateTextXml('Toyou', 'social_people', '抢票 A' + str(i + 1), 123456))

            self.isReplyText(res, '点此绑定学号')

	def test_post_activity_not_existed(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'sad_man_1', '抢票 不存在的', 123456))

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

    def test_post_activity_too_early_to_book(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'sad_man_1', '抢票 A3', 123456))

		self.isReplyText(res, '失败 】 对不起，现在不是抢票时间:(')

    def test_post_activity_too_late_to_book(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'sad_man_1', '抢票 A4', 123456))

		self.isReplyText(res, '失败 】 对不起，现在不是抢票时间:(')

    def test_post_activity_without_remain_tickets(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'sad_man_1', '抢票 A5', 123456))

		self.isReplyText(res, '失败 】 对不起，已经没有余票了:(')

    def test_post_user_has_the_same_ticket_cancelled(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'gay_dog_1', '抢票 A6', 123456))

		self.isReplyText(res, '失败 】 --------------------------')

    def test_post_user_has_the_same_ticket_used(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'gay_dog_2', '抢票 A6', 123456))

		self.isReplyText(res, '失败 】 --------------------------')

    def test_post_user_has_the_same_ticket_valid(self):
		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'gay_dog_3', '抢票 A6', 123456))

		self.isReplyText(res, '失败 】 --------------------------')

    def test_post_user_has_other_tickets(self):
        origin_remain = Activity.objects.get(key='A6').remain_tickets

		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'gay_dog_4', '抢票 A6', 123456))
		self.isReplyNews(res, 1)

		tick = Ticket.objects.get(
            student_id='2015080049', 
            activity=act_published_and_it_is_time_to_book_with_remain_tickets
        )
		self.assertEqual(tick.status, Ticket.STATUS_VALID)

        new_remain = Activity.objects.get(key='A6').remain_tickets
		self.assertEqual(new_remain - origin_remain, -1)

	def test_post_right(self):
		origin_remain = Activity.objects.get(key='A6').remain_tickets

		res = self.client.post('/wechat/', 
			content_type='application/xml', 
			data=generateTextXml('Toyou', 'sad_man_1', '抢票 A6', 123456))
		self.isReplyNews(res, 1)

		tick = Ticket.objects.get(
            student_id='2015080045', 
            activity=act_published_and_it_is_time_to_book_with_remain_tickets
        )
		self.assertEqual(tick.status, Ticket.STATUS_VALID)

        new_remain = Activity.objects.get(key='A6').remain_tickets
		self.assertEqual(new_remain - origin_remain, -1)

    def test_concurrent_different_users_100(self):
        for i in range(100):
            User.objects.create(
                open_id='gay_dog_' + str(100 + i), 
                student_id= str(2015080100 + i)
            )
        return

    def test_concurrent_same_users_100(self):
        return
