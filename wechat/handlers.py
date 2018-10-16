# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
from wechat.models import *
from codex.baseerror import *


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
        #raise NotImplementedError('抢啥的handler，可以利用ActivityDetailHandler的方式，返回一些news即可。（ActivityDetailHandler的实现代码质量不高）')
        published_acts = Activity.objects.filter(status=Activity.STATUS_PUBLISHED)
        response_news = []
        for act in published_acts:
            response_news.append({
                'Title': act.name,
                'Description': act.description,
                'Url': self.url_activity(act.id),
                })
        return self.reply_news(response_news)
        # return self.reply_text(self.get_message('book_what'))
    
class BookingActivityHandler(WeChatHandler):
    def check (self):
        if self.is_msg_type('text'):
            return self.input['Content'].startswith('抢票 ')
        elif self.is_msg_type('event'):
            return (self.input['Event'] == 'CLICK') and (self.input['EventKey'].startswith(self.view.event_keys['book_header']))
        return False
        # return self.is_book_event_click(self.view.event_keys['book_header'])
    
    def handle(self):
        try:
            user = User.objects.get(open_id=self.user.open_id)
        except User.DoesNotExist:
            raise BaseError(-1, 'user does not exist.')
        if user.student_id:
            # 使用锁创建一个电子票的记录
            raise NotImplementedError('book activity API not implemented.')
        else:
            raise BaseError(-1, '还未绑定，可能需要添加template')
        #raise NotImplementedError('抢票的handler，在这里实现逻辑（这个过程可能不标准，代码质量也不高）')
        #actid = int(self.input['EventKey'].split('_')[-1])
        #act = Activity.objects.get(id=actid)
        #return self.reply_single_news({
        #    'Title': act.name,
        #    'Description': act.description,
        #    'Url': self.url_activity(actid),
        #})

class QueryTicketHandler(WeChatHandler):
    def check(self):
        return self.is_text('查票') or self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        try:
            user = User.objects.get(open_id=self.user.open_id)
        except User.DoesNotExist:
            raise BaseError(-1, 'user does not exist.')
        if user.student_id:
            tickets = Ticket.objects.filter(student_id=user.student_id)
            
            raise NotImplementedError('book activity API not implemented.')
        else:
            raise BaseError(-1, '还未绑定，可能需要添加template')
        raise NotImplementedError('query ticket API not implemented.')


class ExtractTicketHandler(WeChatHandler):
    def check(self):
        if self.is_msg_type('text'):
            return self.input['Content'].startswith('取票 ')
        return False

    def handle(self):
        raise NotImplementedError('extract ticket API not implemented.')

class RefundTicketHandler(WeChatHandler):
    def check(self):
        if self.is_msg_type('text'):
            return self.input['Content'].startswith('退票 ')
        return False

    def handle(self):
        raise NotImplementedError('refund ticket API not implemented.')



