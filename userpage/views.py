from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import *
import time
import datetime


class UserBind(APIView):

    def validate_user(self):
        """
        input: self.input['student_id'] and self.input['password']
        raise: ValidateError when validating failed
        """
#         raise NotImplementedError('You should implement UserBind.validate_user method')
        return True

    def get(self):
        self.check_input('openid')
        return User.get_by_openid(self.input['openid']).student_id

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()

class ActivityDetail(APIView):

    def get(self):
        self.check_input('id')
        act = Activity.objects.get(id=self.input['id'], status=1)
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

class TicketDetail(APIView):
    
    def get(self):
        self.check_input('openid', 'ticket')
        student_id = User.objects.get(open_id=self.input['openid']).student_id
        tic = Ticket.objects.get(student_id=student_id, unique_id=self.input['ticket'])
        act = tic.activity
        return {
            'activityName': act.name,
            'place': act.place,
            'activityKey': act.key,
            'uniqueId': tic.unique_id,
            'startTime': time.mktime(act.start_time.timetuple()),
            'endTime': time.mktime(act.end_time.timetuple()),
            'currentTime': time.mktime(datetime.datetime.now().timetuple()),
            'status': tic.status
        }


        


        