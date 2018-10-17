from django.test import TestCase
import datetime
from django.utils import timezone
from wechat.models import *
from django.test import Client
from WeChatTicket import settings

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

class UserBookWhatHandlerTest(TestCase):
	def setUp(self):
		settings.IGNORE_WECHAT_SIGNATURE = True
