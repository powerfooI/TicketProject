# -*- coding: utf-8 -*-
#


from django.conf.urls import url
from adminpage.views import *

__author__ = "Epsirom"


urlpatterns = [
  url(r'^login/?$', Login.as_view()),
  url(r'^logout/?$', Logout.as_view()),
  url(r'^activity/detail/?$', ActivityDetail.as_view()),
  url(r'^image/upload/?$', ImageUpload.as_view())
]
