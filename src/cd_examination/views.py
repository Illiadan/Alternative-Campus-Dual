import datetime

import cd_organisation.views as orgv
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render

import cd_examination.models as exm


@login_required
def switchToExaminationView(request):

    currUser = request.user
    pendingExams = None
    registeredExams = None
    gradedExams = None
    summary = None

    if currUser.role == "Stu":
        pendingExams, registeredExams, gradedExams, summary = query(currUser)

    context = {
        "pendingExams": pendingExams,
        "registeredExams": registeredExams,
        "gradedExams": gradedExams,
        "summary": summary,
        "now": datetime.datetime.isoformat(datetime.datetime.now()),
    }

    return render(request, "examinationBlockManager.html", context=context)


def query(user):

    userCourse = user.seminargroup.course.abbrev
    userSemester = orgv.getSemester(user)

    # passed and not yet graded Exams
    nonPendingExams = exm.ExamRegistration.objects.filter(participant=user)
    nonPendingExamList = [exam.examination_id for exam in nonPendingExams]

    # pendingExams: only Exams of same course, no exams from higher terms, no exams that have already been passed
    pendingExams = (
        exm.Examination.objects.filter(
            seminargroup__course__abbrev=userCourse, module__term__lte=userSemester
        )
        .exclude(id__in=nonPendingExamList)
        .exclude(enrollmentDeadline__lt=datetime.datetime.now())
    )
    pendingExamList = []
    for exam in pendingExams:
        id1 = exam.id
        name1 = exam.module.name
        code1 = exam.module.code
        type1 = exam.type
        attemptQS = exm.ExamRegistration.objects.filter(
            participant=user, examination__module=exam.module
        )
        attempt = len(attemptQS)
        date1 = exam.date.strftime("%d.%m.%Y")
        sTime1 = exam.start_time
        eTime1 = exam.end_time
        room1 = exam.room
        deadline1 = exam.enrollmentDeadline.strftime("%d.%m.%Y %H:%M")
        isoDeadline1 = datetime.datetime.isoformat(
            datetime.datetime.fromisoformat(
                exam.enrollmentDeadline.strftime("%Y-%m-%d %H:%M:%S.%f")
            )
        )
        out = {
            "id": id1,
            "name": name1,
            "code": code1,
            "type": type1,
            "attempt": attempt,
            "date": date1,
            "sTime": sTime1,
            "eTime": eTime1,
            "room": room1,
            "deadline": deadline1,
            "isoDeadline": isoDeadline1,
        }
        pendingExamList.append(out)

    # registeredExams: all exams that the user is registered for, that are not yet graded
    registeredExams = exm.ExamRegistration.objects.filter(
        participant=user, result__isnull=True
    )
    registeredExamList = []
    for exam in registeredExams:
        id2 = exam.examination.id
        name2 = exam.examination.module.name
        code2 = exam.examination.module.code
        type2 = exam.examination.type
        date2 = exam.examination.date.strftime("%d.%m.%Y")
        sTime2 = exam.examination.start_time
        eTime2 = exam.examination.end_time
        room2 = exam.examination.room
        deadline2 = exam.examination.enrollmentDeadline.strftime("%d.%m.%Y %H:%M")
        isoDeadline2 = datetime.datetime.isoformat(
            datetime.datetime.fromisoformat(
                exam.examination.enrollmentDeadline.strftime("%Y-%m-%d %H:%M:%S.%f")
            )
        )
        out = {
            "id": id2,
            "name": name2,
            "code": code2,
            "type": type2,
            "date": date2,
            "sTime": sTime2,
            "eTime": eTime2,
            "room": room2,
            "deadline": deadline2,
            "isoDeadline": isoDeadline2,
        }
        registeredExamList.append(out)

    # query3: get all results of all examinations that the user took and that are already graded
    query3 = exm.ExamRegistration.objects.filter(
        participant=user, result__isnull=False
    ).order_by(
        "examination__module__term", "examination__module__code", "evaluationCompletion"
    )

    gradedExams = []
    listOfExamIds = []
    for exam in query3:
        exam_id3 = exam.examination_id
        name3 = exam.examination.module.name
        code3 = exam.examination.module.code
        if exam.attempt == 1:
            attempt = "EP"
        elif exam.attempt == 2:
            attempt = "W1"
        elif exam.attempt == 3:
            attempt = "W2"
        elif exam.attempt == 4:
            attempt = "AL"
        else:
            attempt = "FL"
        type3 = exam.examination.type
        result = exam.result
        evaluation = exam.evaluationCompletion.strftime("%d.%m.%Y")
        publication = exam.resultPublication.strftime("%d.%m.%Y")
        isoPublication = datetime.date.isoformat(
            datetime.date.fromisoformat(exam.resultPublication.strftime("%Y-%m-%d"))
        )
        out3 = {
            "exam_id": exam_id3,
            "name": name3,
            "code": code3,
            "attempt": attempt,
            "type": type3,
            "result": result,
            "evaluation": evaluation,
            "publication": publication,
            "isoPublication": isoPublication,
        }
        listOfExamIds.append(exam_id3)
        gradedExams.append(out3)

    # query4: get results of all participants of all examinations the user took too and that are already graded
    query4 = (
        exm.ExamRegistration.objects.filter(
            examination__seminargroup__course__abbrev=userCourse,
            result__isnull=False,
            examination_id__in=set(listOfExamIds),
        )
        .values("examination", "result")
        .order_by("examination")
    )

    grades = []
    for x in query4:
        grades.append(x)

    # summary: [examination_id, Module Code, #Noten gesamt, #Note1, #Note2, #Note3, #Note4, #Note5]
    summary = []
    idy = -1
    for idx in set(listOfExamIds):
        summary.append([idx])
        idy += 1
        ct1 = 0
        ct2 = 0
        ct3 = 0
        ct4 = 0
        ct5 = 0
        code = 0
        for grade in grades:
            if grade["examination"] == idx:
                if grade["result"] > 4.0:
                    ct5 += 1
                elif grade["result"] >= 3.5:
                    ct4 += 1
                elif grade["result"] >= 2.5:
                    ct3 += 1
                elif grade["result"] >= 1.5:
                    ct2 += 1
                elif grade["result"] < 1.5:
                    ct1 += 1
        summary[idy].append(ct1 + ct2 + ct3 + ct4 + ct5)
        summary[idy].append(ct1)
        summary[idy].append(ct2)
        summary[idy].append(ct3)
        summary[idy].append(ct4)
        summary[idy].append(ct5)

    return pendingExamList, registeredExamList, gradedExams, summary


def createUserReg(request):
    currUser = request.user
    exam = None

    req = request.POST.get("reg")
    examId = req.split("_")[0]
    isoDeadline = datetime.datetime.fromisoformat(req.split("_")[1])
    exam = exm.Examination.objects.filter(id=examId)[0]

    if exam and isoDeadline >= datetime.datetime.now():
        regUser = exm.ExamRegistration()
        regUser.participant = currUser
        regUser.examination = exam
        regUser.save()

    return HttpResponseRedirect("/examination/")


def deleteUserReg(request):
    currUser = request.user
    exam = None

    req = request.POST["unreg"]
    examId = req.split("_")[0]
    isoDeadline = datetime.datetime.fromisoformat(req.split("_")[1])
    exam = exm.Examination.objects.filter(id=examId)[0]

    if exam and isoDeadline >= datetime.datetime.now():
        exm.ExamRegistration.objects.filter(
            participant=currUser, examination=exam, evaluationCompletion__isnull=True
        ).delete()

    return HttpResponseRedirect("/examination/")
