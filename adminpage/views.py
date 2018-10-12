from codex.baseerror import *
from codex.baseview import APIView
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required

from django.conf import settings
from wechat.models import *
import time
import datetime
import uuid
import os

# Create your views here.

# 系统自带的login_required要设置登录页面 似乎跟我们这个要求不是很符合
def login_required(func):
    def wrapper(self, *args, **kwargs):
        if self.request.user.is_anonymous():
            raise BaseError(-1, 'Not logged in')
        else:
            return func(self, *args, **kwargs)
    return wrapper


class Login(APIView):
  
    @login_required
    def get(self):
        return None
    
    def post(self):
        self.check_input('username', 'password')
        user = authenticate(username=self.input['username'], password=self.input['password'])
        if user is not None:
            if user.is_active:
                login(self.request, user)

class Logout(APIView):
    
    def post(self):
        logout(self.request)
        if self.request.user.is_authenticated():
            raise BaseError(-1, 'Logout Failure')

class ActivityDetail(APIView):

    @login_required
    def get(self):
        self.check_input('id')
        act = Activity.objects.get(id=self.input['id'])
        return {
            'name': act.name,
            'key': act.key,
            'description': act.description,
            'startTime': time.mktime(act.start_time.timetuple()),
            'endTime': time.mktime(act.end_time.timetuple()),
            'place': act.place,
            'bookStart': time.mktime(act.book_start.timetuple()),
            'bookEnd': time.mktime(act.book_end.timetuple()),
            'totalTickets': act.total_tickets,
            'picUrl': act.pic_url,
            'remainTickets': act.remain_tickets,
            'currentTime': time.mktime(datetime.datetime.now().timetuple()),
        }

class ImageUpload(APIView):

    @login_required
    def post(self):
        self.check_input('image')
        image = self.input['image'][0]
        ext = image.name.split('.')[-1]
        filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
        # return the whole path to the file
        fname =  os.path.join(settings.MEDIA_ROOT, "pic", filename)
        with open(fname, 'wb') as pic:
            for c in image.chunks():
                pic.write(c)
        return ''.join([self.request.get_host(), settings.MEDIA_URL, 'pic/', filename])
        
