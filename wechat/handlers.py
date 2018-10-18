# -*- coding: utf-8 -*-
#
import datetime
import uuid

from wechat.wrapper import WeChatHandler
from wechat.models import *
from codex.baseerror import *
from django.db import transaction
from django.utils import timezone


__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        self.user.student_id = ''
        self.user.save()
        return self.reply_text(self.get_message('unbind_account'))


class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


# new added handlers
class BookWhatHandler(WeChatHandler):

    def check (self):
        return self.is_text('抢啥') or self.is_event_click(self.view.event_keys['book_what'])
    
    def handle(self):
        published_acts = Activity.objects.filter(status=Activity.STATUS_PUBLISHED)
        response_news = []
        for act in published_acts:
            response_news.append({
                'Title': act.name,
                'Description': act.description,
                'Url': self.url_activity(act.id),
            })
        return self.reply_news(response_news)
    

class BookingActivityHandler(WeChatHandler):

    def check (self):
        if self.is_msg_type('text'):
            return self.input['Content'].startswith('抢票 ')
        elif self.is_msg_type('event'):
            return (self.input['Event'] == 'CLICK') and (self.input['EventKey'].startswith(self.view.event_keys['book_header']))
        return False
    
    def handle(self):
        with transaction.commit_on_success():            
            # 测试是否存在此用户
            try:
                user = User.objects.select_for_update().get(open_id=self.user.open_id) # 悲观锁
                # user = User.objects.get(open_id=self.user.open_id) # 悲观锁
            except User.DoesNotExist:
                raise BaseError(-1, 'User does not exist.')

            # 测试用户是否绑定
            if not user.student_id:
                return self.reply_text(self.get_message('bind_account'))

            # 处理文本信息的情况
            if self.is_msg_type('text'):
                act_key = self.input['Content'][len("抢票 "):]
                acts = Activity.objects.select_for_update().filter(key=act_key)
                # acts = Activity.objects.filter(key=act_key)
            # 处理点击事件的情况
            else:
                act_id = int(self.input['EventKey'].split('_')[-1])
                acts = Activity.objects.select_for_update().filter(id=act_id)
                # acts = Activity.objects.filter(id=act_id)

            # 检查活动
            if len(acts) == 0:
                return self.reply_text("【 抢票失败 】 对不起，这儿没有对应的活动:(") 
            act = acts[0]
            if act.status != Activity.STATUS_PUBLISHED:
                return self.reply_text("【 抢票失败 】 对不起，这儿没有对应的活动:(") 
            current_timestamp = timezone.now().timestamp()
            book_start_timestamp = act.book_start.timestamp()
            book_end_timestamp = act.book_end.timestamp()
            if current_timestamp < book_start_timestamp or book_end_timestamp < current_timestamp:
                return self.reply_text("【 抢票失败 】 对不起，现在不是抢票时间:(") 
            if act.remain_tickets <= 0:
                return self.reply_text("【 抢票失败 】 对不起，已经没有余票了:(")

            # 检查重复抢票的情况
            tickets_valid_in_the_same_activity = Ticket.objects.select_for_update().filter(
                student_id = user.student_id,
                activity = act,
                status = Ticket.STATUS_VALID
            )
            #tickets_valid_in_the_same_activity = Ticket.objects.filter(
            #    student_id = user.student_id,
            #    activity = act,
            #    status = Ticket.STATUS_VALID
            #)

            if len(tickets_valid_in_the_same_activity) > 0:
                tickets_valid_in_the_same_activity.save()
                return self.reply_text("【 抢票失败 】 请不要重复抢票")
            
            tickets_used_in_the_same_activity = Ticket.objects.select_for_update().filter(
                student_id = user.student_id,
                activity = act,
                status = Ticket.STATUS_USED
            )
            #tickets_used_in_the_same_activity = Ticket.objects.filter(
            #    student_id = user.student_id,
            #    activity = act,
            #    status = Ticket.STATUS_USED
            #)
            if len(tickets_used_in_the_same_activity) > 0:
                tickets_used_in_the_same_activity.save()
                return self.reply_text("【 抢票失败 】 请不要重复抢票") 
            

            # 票充足，处理活动表格、电子票表格，失败、成功都则返回对应信息
            act.remain_tickets = act.remain_tickets - 1
            ticket_unique_id = str(uuid.uuid1()) + str(user.student_id)
            if len(ticket_unique_id) > 64:
                ticket_unique_id = ticket_unique_id[:64]
            Ticket.objects.create(
                student_id = user.student_id,
                unique_id = ticket_unique_id,
                activity = act,
                status = Ticket.STATUS_VALID
            )

            act.save()
            user.save()
            return self.reply_single_news({
                'Title': "【 抢票成功 】 " + act.name,
                'Description': act.description,
                'Url': self.url_activity(act.id),
            })


class QueryTicketHandler(WeChatHandler):
    def check(self):
        return self.is_text('查票') or self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        # 测试是否存在此用户
        try:
            user = User.objects.get(open_id=self.user.open_id)
        except User.DoesNotExist:
            raise BaseError(-1, 'User does not exist.')

        # 测试用户是否绑定
        if not user.student_id:
            return self.reply_text(self.get_message('bind_account')) 
        
        tickets = Ticket.objects.filter(student_id=self.user.student_id)
        if len(tickets) == 0:
            return self.reply_text("您现在还没有票嗷:)") 
        return_info = []
        for ticket in tickets:
            return_info.append({
                'Title': ticket.activity.name,
                'Description': "",
                'Url': self.url_ticket(ticket),
            })
        return self.reply_news(return_info)


class ExtractTicketHandler(WeChatHandler):
    def check(self):
        if self.is_msg_type('text'):
            return self.input['Content'].startswith('取票 ')
        return False

    def handle(self):
        # 测试是否存在此用户
        try:
            user = User.objects.get(open_id=self.user.open_id)
        except User.DoesNotExist:
            raise BaseError(-1, 'User does not exist.')

        # 测试用户是否绑定
        if not user.student_id:
            return self.reply_text(self.get_message('bind_account')) 

        # 检测活动名的合法性
        act_key = self.input['Content'][len('取票 '):]
        acts = Activity.objects.filter(key=act_key)
        if len(acts) == 0:
            return self.reply_text('【 检票失败 】 活动不存在哦~')
        act = acts[0]

        # 检测是否有未使用的对应活动的票
        tickets = Ticket.objects.filter(student_id=user.student_id, activity=act.key, status=Ticket.STATUS_VALID)
        if len(tickets) == 0:
            return self.reply_text('【 检票失败 】 您没有此活动中未使用的票嗷！')
        
        # 检测活动是否开始
        ticket = tickets[0]
        current_timestamp = datetime.timezone.now().timestamp()
        start_timestamp = act.start_time.timestamp()
        end_timestamp = act.end_time.timestamp()
        # 开始还是结束后不能检票嘛？
        if current_timestamp > end_timestamp:
            return self.reply_text('【 检票失败 】 活动已经结束！')

        # 检票
        ticket.status = Ticket.STATUS_USED
        tickets.save()
        return self.reply_single_news({
            'Title': "【 检票成功 】 " + act.name,
            'Description': act.description,
            'Url': self.url_activity(act.key),
        })


class RefundTicketHandler(WeChatHandler):
    def check(self):
        if self.is_msg_type('text'):
            return self.input['Content'].startswith('退票 ')
        return False

    def handle(self):
        # 测试是否存在此用户
        try:
            user = User.objects.get(open_id=self.user.open_id)
        except User.DoesNotExist:
            raise BaseError(-1, 'User does not exist.')

        # 测试用户是否绑定
        if not user.student_id:
            return self.reply_text(self.get_message('bind_account')) 

        # 检测活动名的合法性
        act_key = self.input['Content'][len('退票 '):]
        acts = Activity.objects.filter(key=act_key)
        if len(acts) == 0:
            return self.reply_text('【 退票失败 】 活动不存在哦~')
        act = acts[0]

        # 检测是否有未使用的对应活动的票
        tickets = Ticket.objects.filter(student_id=user.student_id, activity=act.key, status=Ticket.STATUS_VALID)
        if len(tickets) == 0:
            return self.reply_text('【 退票失败 】 您没有此活动中未使用的票嗷！')
        
        # 检测活动是否开始
        ticket = tickets[0]
        current_timestamp = datetime.timezone.now().timestamp()
        start_timestamp = act.start_time.timestamp()
        end_timestamp = act.end_time.timestamp()
        # 开始还是结束后不能退票嘛？
        if current_timestamp > end_timestamp:
            return self.reply_text('【 退票失败 】 活动已经结束！')

        # 退票
        ticket.status = Ticket.STATUS_CANCELLED
        tickets.save()
        return self.reply_single_news({
            'Title': "【 退票成功 】 " + act.name,
            'Description': act.description,
            'Url': self.url_activity(act.key),
        })
