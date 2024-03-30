import datetime as dt

from django.utils.safestring import mark_safe

import cd_examination.models as exm
import cd_examination.views as exv
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

import cd_dashboard.models as dsm
from cd_timetable.utils import WeekCalendar
from cd_timetable.views import get_events, get_week, next_week, prev_week


@login_required
def switchToDashboardView(request):
    currUser = request.user
    unregisteredExams = None
    registeredExams = None
    gradedExams = None
    grades = None
    summary = None
    pendingResults = None
    messages = getMessages(currUser)

    if currUser.role == "Stu":
        unregisteredExams, registeredExams, gradedExams, summary = exv.query(currUser)
        pendingResults = query(currUser)

        idx = 0
        while idx < len(gradedExams):
            if dt.date.fromisoformat(
                gradedExams[idx]["isoPublication"]
            ) < dt.date.today() - dt.timedelta(days=90):
                gradedExams.remove(gradedExams[idx])
            else:
                idx += 1

    date = get_week(request.GET.get("week"))
    cal = WeekCalendar(date.year, date.week, get_events(currUser, currUser.seminargroup))

    context = {
        "unregisteredExams": unregisteredExams,
        "registeredExams": registeredExams,
        "gradedExams": gradedExams,
        "pendingResults": pendingResults,
        "messages": messages,
        "prev_week": prev_week(date),
        "next_week": next_week(date),
        "calendar": mark_safe(cal.formatweek())
    }

    return render(request, "dashboardBlockManager.html", context=context)


def query(user):

    query1 = exm.ExamRegistration.objects.filter(
        participant=user,
        result__isnull=True,
        examination__date__lte=dt.date.today(),
        examination__end_time__lt=dt.datetime.now().time(),
    )

    pendingResults = []
    for exam in query1:
        name = exam.examination.module.name
        code = exam.examination.module.code
        type = exam.examination.type
        date = exam.examination.date.strftime("%d.%m.%Y")
        out = {
            "name": name,
            "code": code,
            "type": type,
            "date": date,
        }
        pendingResults.append(out)

    return pendingResults


def getMessages(user):
    if user.role == "Stu":
        query = dsm.MessageBox.objects.filter(
            readableByStudents=True,
            lastEdited__gte=dt.datetime.now() - dt.timedelta(days=180),
        )

        messages = []
        for msg in query:
            authorLName = msg.author.last_name
            authorFName = msg.author.first_name
            posted = msg.posted.strftime("%d.%m.%Y %H:%M")
            isoPosted = dt.datetime.isoformat(
                dt.datetime.fromisoformat(msg.posted.strftime("%Y-%m-%d %H:%M:%S.%f"))
            )
            lastEdited = msg.lastEdited.strftime("%d.%m.%Y %H:%M")
            isoLastEdited = dt.datetime.isoformat(
                dt.datetime.fromisoformat(
                    msg.lastEdited.strftime("%Y-%m-%d %H:%M:%S.%f")
                )
            )
            message = msg.message
            out = {
                "authorLName": authorLName,
                "authorFName": authorFName,
                "posted": posted,
                "isoPosted": isoPosted,
                "lastEdited": lastEdited,
                "isoLastEdited": isoLastEdited,
                "message": message,
            }
            messages.append(out)

        return messages

    elif user.role == "Lec":
        query = dsm.MessageBox.objects.filter(
            readableByLecturers=True,
            lastEdited__gte=dt.datetime.now() - dt.timedelta(days=180),
        )

        messages = []
        for msg in query:
            authorLName = msg.author.last_name
            authorFName = msg.author.first_name
            posted = msg.posted.strftime("%d.%m.%Y %H:%M")
            isoPosted = dt.datetime.isoformat(
                dt.datetime.fromisoformat(msg.posted.strftime("%Y-%m-%d %H:%M:%S.%f"))
            )
            lastEdited = msg.lastEdited.strftime("%d.%m.%Y %H:%M")
            isoLastEdited = dt.datetime.isoformat(
                dt.datetime.fromisoformat(
                    msg.lastEdited.strftime("%Y-%m-%d %H:%M:%S.%f")
                )
            )
            message = msg.message
            out = {
                "authorLName": authorLName,
                "authorFName": authorFName,
                "posted": posted,
                "isoPosted": isoPosted,
                "lastEdited": lastEdited,
                "isoLastEdited": isoLastEdited,
                "message": message,
            }
            messages.append(out)

        return messages

    elif user.role == "Org":
        query = dsm.MessageBox.objects.filter(
            readableByOrganisator=True,
            lastEdited__gte=dt.datetime.now() - dt.timedelta(days=180),
        )

        messages = []
        for msg in query:
            authorLName = msg.author.last_name
            authorFName = msg.author.first_name
            posted = msg.posted.strftime("%d.%m.%Y %H:%M")
            isoPosted = dt.datetime.isoformat(
                dt.datetime.fromisoformat(msg.posted.strftime("%Y-%m-%d %H:%M:%S.%f"))
            )
            lastEdited = msg.lastEdited.strftime("%d.%m.%Y %H:%M")
            isoLastEdited = dt.datetime.isoformat(
                dt.datetime.fromisoformat(
                    msg.lastEdited.strftime("%Y-%m-%d %H:%M:%S.%f")
                )
            )
            message = msg.message
            out = {
                "authorLName": authorLName,
                "authorFName": authorFName,
                "posted": posted,
                "isoPosted": isoPosted,
                "lastEdited": lastEdited,
                "isoLastEdited": isoLastEdited,
                "message": message,
            }
            messages.append(out)

        return messages

    else:
        return None
