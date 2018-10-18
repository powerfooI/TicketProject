from codex.baseerror import *
from codex.baseview import APIView
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
# from django.contrib.auth.decorators import login_required
from wechat.views import CustomWeChatView

from django.conf import settings
from wechat.models import *
import time
import datetime
import uuid
import os


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
        else:
            raise BaseError(-1, 'Login Failure')


class Logout(APIView):

    @login_required
    def post(self):
        logout(self.request)
        if self.request.user.is_authenticated():
            raise BaseError(-1, 'Logout Failure')


class ActivityDetail(APIView):

    @login_required
    def get(self):
        self.check_input('id')
        act = Activity.objects.get(id=self.input['id'])
        used_tickets = len(Ticket.objects.filter(activity_id=act.id, status=Ticket.STATUS_USED))
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
            'usedTickets': used_tickets,
            'remainTickets': act.remain_tickets,
            'bookedTickets': act.total_tickets - act.remain_tickets,
            'currentTime': time.mktime(datetime.datetime.now().timetuple()),
            'status': act.status,
        }

    @login_required
    def post(self):
        self.check_input('id', 'name', 'place', 'description', 'picUrl', 'startTime',
                         'endTime', 'bookStart', 'bookEnd', 'totalTickets', 'status')
        try:
            fetch_activity = Activity.objects.get(id=self.input['id'])
            fetch_activity.description = self.input['description']
            fetch_activity.pic_url = self.input['picUrl']
            current_time = timezone.now()
            if current_time < fetch_activity.book_start:
                fetch_activity.book_end = self.input['bookEnd']
                fetch_activity.start_time = self.input['startTime']
                fetch_activity.end_time = self.input['endTime']
                fetch_activity.total_tickets = self.input['totalTickets']
            elif current_time < fetch_activity.start_time and current_time >= fetch_activity.book_start:
                fetch_activity.start_time = self.input['startTime']
                fetch_activity.end_time = self.input['endTime']
                fetch_activity.book_end = self.input['bookEnd']
            elif current_time < fetch_activity.end_time and current_time >= fetch_activity.start_time:
                fetch_activity.start_time = self.input['startTime']
                fetch_activity.end_time = self.input['endTime']
            if fetch_activity.status != Activity.STATUS_PUBLISHED:
                fetch_activity.name = self.input['name']
                fetch_activity.place = self.input['place']
                fetch_activity.book_start = self.input['bookStart']
                fetch_activity.status = self.input['status']
            fetch_activity.save()
        except Activity.DoesNotExist:
            raise BaseError(-1, 'Wrong Activity Id!')


class ImageUpload(APIView):

    @login_required
    def post(self):
        self.check_input('image')
        image = self.input['image'][0]
        ext = image.name.split('.')[-1]
        filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
        # return the whole path to the file
        fname = os.path.join(settings.STATIC_ROOT, "upload", filename)
        with open(fname, 'wb') as pic:
            for c in image.chunks():
                pic.write(c)
        return ''.join(['http://', self.request.get_host(), '/upload/', filename])


class ActivityList(APIView):

    @login_required
    def get(self):
        query_set = Activity.objects.filter(status__gte=0)
        activities = []
        for item in query_set:
            activities.append({
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'startTime': time.mktime(item.start_time.timetuple()),
                'endTime': time.mktime(item.end_time.timetuple()),
                'place': item.place,
                'bookStart': time.mktime(item.book_start.timetuple()),
                'bookEnd': time.mktime(item.book_end.timetuple()),
                'currentTime': time.mktime(datetime.datetime.now().timetuple()),
                'status': item.status
            })
        return activities


class ActivityDelete(APIView):

    @login_required
    def post(self):
        self.check_input('id')
        try:
            act_deleting = Activity.objects.get(id=self.input['id'])
            if act_deleting.status != Activity.STATUS_DELETED:
                act_deleting.status = Activity.STATUS_DELETED
                act_deleting.save()
            else:
                raise BaseError(-1, 'The activity has been deleted!')
        except Activity.DoesNotExist:
            raise BaseError(-1, 'The activity does not exist!')


class ActivityCreate(APIView):

    @login_required
    def post(self):
        self.check_input('name', 'key', 'place', 'description', 'picUrl', 'startTime',
                         'endTime', 'bookStart', 'bookEnd', 'totalTickets', 'status')
        try:
            new_activity = Activity()
        except:
            raise BaseError(-1, 'Create Failed!')
        new_activity.name = self.input['name']
        new_activity.key = self.input['key']
        new_activity.place = self.input['place']
        new_activity.description = self.input['description']
        new_activity.start_time = self.input['startTime']
        new_activity.end_time = self.input['endTime']
        new_activity.book_start = self.input['bookStart']
        new_activity.book_end = self.input['bookEnd']
        new_activity.total_tickets = self.input['totalTickets']
        new_activity.remain_tickets = self.input['totalTickets']
        new_activity.status = self.input['status']
        new_activity.pic_url = self.input['picUrl']
        new_activity.save()
        return {
            'id': new_activity.id,
        }


class ActivityMenu(APIView):

    @login_required
    def get(self):
        # get current
        existed_ids = CustomWeChatView.get_menu()

        query_set = Activity.objects.filter(status__gte=0)
        activities = []
        ind = 1
        for item in query_set:
            if item.id in existed_ids:
                activities.append({
                    'id': item.id,
                    'name': item.name,
                    'menuIndex': ind,
                })
                ind += 1
            else:
                activities.append({
                    'id': item.id,
                    'name': item.name,
                    'menuIndex': 0,
                })
        return activities

    @login_required
    def post(self):
        activities = []
        for i in self.input:
            act = Activity.objects.get(id=i)
            activities.append(act)
        CustomWeChatView.update_menu(activities)


class ActivityChekin(APIView):

    @login_required
    def post(self):
        self.check_input('actId', 'ticket', 'studentId')
        try:
            if self.input['ticket']:
                the_ticket = Ticket.objects.get(activity_id=self.input['actId'], unique_id=self.input['ticket'])
                if the_ticket.status != Ticket.STATUS_VALID:
                    raise BaseError(-1, 'Not a valid ticket!')
                the_ticket.status = Ticket.STATUS_USED
                the_ticket.save()
                return {
                    'ticket': the_ticket.id,
                    'studentId': the_ticket.student_id
                }
            else:
                the_ticket = Ticket.objects.get(activity_id=self.input['actId'], student_id=self.input['studentId'])
                if the_ticket.status != Ticket.STATUS_VALID:
                    raise BaseError(-1, 'Not a valid ticket!')
                the_ticket.status = Ticket.STATUS_USED
                the_ticket.save()
                return {
                    'ticket': the_ticket.id,
                    'studentId': the_ticket.student_id
                }
        except Ticket.DoesNotExist:
            raise BaseError(-1, 'Error in checkin!')
