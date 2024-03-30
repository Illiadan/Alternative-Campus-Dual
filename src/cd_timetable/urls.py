from django.conf.urls import url

from . import views

urlpatterns = [
    url("ics", views.ics_view, name="ics"),
    url("", views.CalendarView.as_view(), name="calendar"),
]
