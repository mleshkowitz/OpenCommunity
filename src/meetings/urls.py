from django.conf.urls import patterns, url
from meetings import views

urlpatterns = patterns('',

    url(r'^$', views.MeetingList.as_view(), name="history"),

    url(r'^(?P<pk>\d+)/$', views.MeetingDetailView.as_view(), name="meeting"),
    url(r'^(?P<pk>\d+)/protocol/$', views.MeetingProtocolView.as_view(),
        name="meeting_protocol"),

)
