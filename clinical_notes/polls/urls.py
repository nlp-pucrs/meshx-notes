###
from __future__ import unicode_literals
###


from django.urls import path

####
from django.conf.urls import url
###

from . import views
from polls.views import PacientePageView#, PacientePageViewEng

urlpatterns = [
	#path('', PacientePageView.as_view(), name='index'),
	path('', PacientePageView.as_view(), name='index')
]