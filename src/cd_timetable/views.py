import calendar
from ics import Calendar, Event
from datetime import datetime, timedelta
from itertools import chain

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse
from django.utils.safestring import mark_safe
from django.views import generic

from cd_core.models import Seminargroup, User
from cd_examination.models import Examination

from .models import Lecture
from .utils import DayCalendar, MonthCalendar, WeekCalendar


class CalendarView(LoginRequiredMixin, generic.ListView):
    model = Lecture
    template_name = "timetableLayout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['seminargroups'] = Seminargroup.objects.all()
        user = self.request.user

        semgroup = ""
        if user.role == User.ORGANISATOR:
            semgroup = self.request.GET.get("semgroup") or context['seminargroups'].first()
            context["semgroup"] = semgroup
        else:
            semgroup = user.seminargroup or ""

        display = self.request.GET.get("display")
        context["display"] = display
        if display == None or display == "month":
            date = get_month(self.request.GET.get("month"))

            context["prev_month"] = prev_month(date)
            context["next_month"] = next_month(date)

            self.template_name = "monthLayout.html"
            cal = MonthCalendar(date.year, date.month, get_events(user, semgroup))
            html_cal = cal.formatmonth(withyear=True)
            context["calendar"] = mark_safe(html_cal)

        if display == "week":
            date = get_week(self.request.GET.get("week"))

            context["prev_week"] = prev_week(date)
            context["next_week"] = next_week(date)

            self.template_name = "weekLayout.html"
            cal = WeekCalendar(date.year, date.week, get_events(user, semgroup))
            html_cal = cal.formatweek()
            context["calendar"] = mark_safe(html_cal)

        if display == "day":
            date = get_day(self.request.GET.get("day"))

            context["prev_day"] = prev_day(date)
            context["next_day"] = next_day(date)

            self.template_name = "dayLayout.html"
            cal = DayCalendar(date.year, date.week, date.weekday, get_events(user, semgroup))
            html_cal = cal.formatday()
            context["calendar"] = mark_safe(html_cal)

        return context

def get_events(user, semgroup):
    role = user.role;
    lectures = list();
    exams = list();

    if role == User.ORGANISATOR or role == User.STUDENT:
        lectures = Lecture.objects.filter(seminargroup__code=semgroup)
        exams = Examination.objects.filter(seminargroup__code=semgroup)
    elif role == User.LECTURER:
        lectures = Lecture.objects.filter(lecturer=user)

    return list(chain(lectures, exams))

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = "month=" + str(prev_month.year) + "-" + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = "month=" + str(next_month.year) + "-" + str(next_month.month)
    return month


def prev_week(d):
    da = datetime.fromisocalendar(d.year, d.week, d.weekday)
    da = da - timedelta(weeks=1)

    return "week=" + str(da.year) + "-" + str(da.isocalendar().week)


def next_week(d):
    da = datetime.fromisocalendar(d.year, d.week, d.weekday)
    da = da + timedelta(weeks=1)

    return "week=" + str(da.year) + "-" + str(da.isocalendar().week)


def prev_day(d):
    da = datetime.fromisocalendar(d.year, d.week, d.weekday)
    da = da - timedelta(days=1)

    return (
        "day="
        + str(da.year)
        + "-"
        + str(da.isocalendar().week)
        + "-"
        + str(da.isocalendar().weekday)
    )


def next_day(d):
    da = datetime.fromisocalendar(d.year, d.week, d.weekday)
    da = da + timedelta(days=1)

    return (
        "day="
        + str(da.year)
        + "-"
        + str(da.isocalendar().week)
        + "-"
        + str(da.isocalendar().weekday)
    )


def get_month(year_month_string):
    if year_month_string:
        year, month = (int(x) for x in year_month_string.split("-"))
        return datetime(year, month, day=1)
    return datetime.today()


def get_week(year_week_string):
    if year_week_string:
        year, week = (int(x) for x in year_week_string.split("-"))
        return datetime.fromisocalendar(year, week, 1).isocalendar()
    return datetime.today().isocalendar()


def get_day(year_week_day_string):
    if year_week_day_string:
        year, week, day = (int(x) for x in year_week_day_string.split("-"))
        return datetime.fromisocalendar(year, week, day).isocalendar()
    return datetime.today().isocalendar()

def ics_view(request):
    user = request.user

    c = Calendar()
    events = get_events(user, user.seminargroup);

    for tmt_event in events:
        ics_event = Event()
        if isinstance(tmt_event, Lecture):
            ics_event.name = f'VS {tmt_event.module.code}'
            ics_event.description = f'Dozent: {tmt_event.lecturer} - {tmt_event.seminargroup}\n Bemerkungen: {tmt_event.comment}'
        elif isinstance(tmt_event, Examination):
            ics_event.name = f'P {tmt_event.module.code} ({tmt_event.type})'
            ics_event.description = f'Bemerkungen: {tmt_event.comment} - {tmt_event.seminargroup}'

        ics_event.begin = f'{tmt_event.date.strftime("%Y-%m-%d")} {tmt_event.start_time.strftime("%X")}'
        ics_event.end = f'{tmt_event.date.strftime("%Y-%m-%d")} {tmt_event.end_time.strftime("%X")}'
        ics_event.location = f'{tmt_event.room}'
        c.events.add(ics_event)

    response = HttpResponse(c, content_type='text/calendar')
    response["Content-Disposition"] = "attachment; filename=ba_stundenplan.ics"
    
    return response
