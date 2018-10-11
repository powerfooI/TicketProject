from codex.baseerror import *
from codex.baseview import APIView
from django.contrib.auth import authenticate, login, logout

from wechat.models import *

# Create your views here.

class Login(APIView):
  
    def get(self):
        if self.request.user.is_anonymous():
            raise BaseError(-1, 'Not logged in')
    
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

