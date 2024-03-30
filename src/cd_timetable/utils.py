from calendar import HTMLCalendar 
from datetime import date, datetime, timedelta

from cd_examination.models import Examination
from cd_timetable.models import Lecture

class MonthCalendar(HTMLCalendar):
    def __init__(self, year=None, month=None, events=None):
        self.year = year
        self.month = month
        self.events = [event for event in events if event.date.year == year and event.date.month == month]
        super(MonthCalendar, self).__init__()

    def formatday(self, day):
        d = ""

        events_this_day = [event for event in self.events if event.date.day == day]
        for event in events_this_day:
            type = 'exam' if isinstance(event, Examination) else 'lecture'

            if isinstance(event, Lecture):
                d += f"<div class='is-{type}'>{event.module.code}</div>"
                d += f'<div class="eventinfo is-{type}">\n'
                d += f'<p class="title is-5">{event.module.code}</p>\n'
            else:
                d += f"<div class='is-{type}'>{event.type}: {event.module.code}</div>"
                d += f'<div class="eventinfo is-{type}">\n'
                d += f'<p class="title is-5">{event.type}: {event.module.code}</p>\n'
            d += f'{event.date.strftime("%d.%m.%Y")}</br>{event.start_time} - {event.end_time}</br>\n'
            if isinstance(event, Lecture):
                d += f"{event.lecturer.get_full_name()} - {event.seminargroup}</br>\n"
            d += f"{event.room}</br>\n"
            d += f"<p>{event.comment or ''}</p>\n"
            d += f"</div>\n"

        if day != 0:
            return f"<td class='is-monthly'><span class='date'>{day}</span> {d} </td>"
        return "<td class='is-monthly'></td>"

    def formatweek(self, theweek):
        week = ""
        for d, weekday in theweek:
            week += self.formatday(d)
        return f"<tr> {week} </tr>"

    def formatmonth(self, withyear=True):
        cal = f'<table class="calendar" style="table-layout: fixed;">\n'
        cal += f"{self.formatmonthname(self.year, self.month, withyear=withyear)}\n"
        cal += f"{self.formatweekheader()}\n"
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f"{self.formatweek(week)}\n"
        cal += '</table>'
        return cal


class WeekCalendar(HTMLCalendar):
    def __init__(self, year=None, week=None, events=None):
        self.events = [event for event in events if event.date.year == year and event.date.isocalendar().week == week]
        self.first_day = datetime.fromisocalendar(year, week, 1)
        self.last_day = datetime.fromisocalendar(year, week, 7)
        super(WeekCalendar, self).__init__()

    def formatweekheader(self):
        s = "<tr>"
        s = "<th></th>"  # empty header for time column
        calendar_day = self.first_day

        for day in self.iterweekdays():
            s += f'<th>{calendar_day.strftime("%A, %d.%m.%Y")}</th>'
            calendar_day = calendar_day + timedelta(days=1)

        s += "</tr>"
        return s

    def formattime(self, current_time):
        current_day = self.first_day
        next_fifteen_minutes = current_time + timedelta(minutes=15)

        timerow_html = ""
        timerow_html += f'<td style="width: 100px;">{current_time.strftime("%H:%M")}</td>\n'

        while current_day <= self.last_day:
            events = [event for event in self.events if event.date == current_day.date() and (event.start_time == current_time.time() or event.start_time == next_fifteen_minutes.time())]

            if events:
                timerow_html += f'<td class="is-weekly"><div class="timetable-flexbox">\n'
                for event in events:
                    timerow_html += event.print_to_timetable()
                timerow_html += f'</div></td>\n'
            else:
                timerow_html += f'<td></td>\n'

            current_day = current_day + timedelta(days=1)

        return timerow_html

    def formatweek(self):
        # we dont care for date, we only want to start at 0:00
        start_of_day = datetime(2021, 1, 1, 0, 0, 0)
        current_time = start_of_day
        end_of_day = start_of_day + timedelta(hours=24)

        cal = f'<table class="calendar">\n'
        cal += f"{self.formatweekheader()}\n"
        while current_time <= end_of_day:
            cal += f"<tr>{self.formattime(current_time)}</tr>"
            current_time = current_time + timedelta(minutes=30)
        cal += '</table>'

        return cal

class DayCalendar(HTMLCalendar):
    def __init__(self, year=None, week=None, weekday=None, events=None):
        self.events = [event for event in events if event.date == date.fromisocalendar(year, week, weekday)]
        self.date = datetime.fromisocalendar(year, week, weekday)
        super(DayCalendar, self).__init__()

    def formattime(self, current_time):
        next_fifteen_minutes = current_time + timedelta(minutes=15)
        events = [event for event in self.events if event.start_time == current_time.time() or event.start_time == next_fifteen_minutes.time()]

        timerow_html = ""
        timerow_html += f'<td style="width: 100px;">{current_time.strftime("%H:%M")}</td>\n'
        timerow_html += f'<td class="is-daily">\n'

        if events:
            for event in events:
                timerow_html += event.print_to_timetable()

        timerow_html += f'</td>\n'

        return timerow_html

    def formatweekday(self):
        return f"<tr><th colspan=2>{self.date.strftime('%A, %d.%m.%Y')}</th></tr>"

    def formatday(self):
        # we dont care for date, we only want to start at 0:00
        start_of_day = datetime(2021, 1, 1, 0, 0, 0)
        current_time = start_of_day
        end_of_day = start_of_day + timedelta(hours=24)

        cal = f'<table class="calendar">\n'
        cal += f"{self.formatweekday()}\n"
        while current_time <= end_of_day:
            cal += f"<tr>{self.formattime(current_time)}</tr>"
            current_time = current_time + timedelta(minutes=30)
        cal += '</table>'

        return cal
