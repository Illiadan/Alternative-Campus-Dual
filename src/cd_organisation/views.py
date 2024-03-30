import datetime as dt

from cd_core.models import Module
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def switchToOrganisationView(request):
    currUser = request.user
    semGroup = currUser.seminargroup
    currSemester = getSemester(currUser)
    phaseDict = None
    course = None
    semesterIdx = None
    modulesMandatory = None
    modulesElective = None
    modulesDict = None
    terms = [x for x in range(1, 7)]

    if currUser.role == "Stu":
        course = semGroup.course
        term1_t_start = semGroup.term1_t_start.strftime("%d.%m.%Y")
        term1_t_end = semGroup.term1_t_end.strftime("%d.%m.%Y")
        term2_t_start = semGroup.term2_t_start.strftime("%d.%m.%Y")
        term2_t_end = semGroup.term2_t_end.strftime("%d.%m.%Y")
        term3_t_start = semGroup.term3_t_start.strftime("%d.%m.%Y")
        term3_t_end = semGroup.term3_t_end.strftime("%d.%m.%Y")
        term4_t_start = semGroup.term4_t_start.strftime("%d.%m.%Y")
        term4_t_end = semGroup.term4_t_end.strftime("%d.%m.%Y")
        term5_t_start = semGroup.term5_t_start.strftime("%d.%m.%Y")
        term5_t_end = semGroup.term5_t_end.strftime("%d.%m.%Y")
        term6_t_start = semGroup.term6_t_start.strftime("%d.%m.%Y")
        term6_t_end = semGroup.term6_t_end.strftime("%d.%m.%Y")
        term1_p_start = semGroup.term1_p_start.strftime("%d.%m.%Y")
        term1_p_end = semGroup.term1_p_end.strftime("%d.%m.%Y")
        term2_p_start = semGroup.term2_p_start.strftime("%d.%m.%Y")
        term2_p_end = semGroup.term2_p_end.strftime("%d.%m.%Y")
        term3_p_start = semGroup.term3_p_start.strftime("%d.%m.%Y")
        term3_p_end = semGroup.term3_p_end.strftime("%d.%m.%Y")
        term4_p_start = semGroup.term4_p_start.strftime("%d.%m.%Y")
        term4_p_end = semGroup.term4_p_end.strftime("%d.%m.%Y")
        term5_p_start = semGroup.term5_p_start.strftime("%d.%m.%Y")
        term5_p_end = semGroup.term5_p_end.strftime("%d.%m.%Y")
        term6_p_start = semGroup.term6_p_start.strftime("%d.%m.%Y")
        term6_p_end = semGroup.term6_p_end.strftime("%d.%m.%Y")
        phaseDict = {
            "term1_t_start": term1_t_start,
            "term2_t_start": term2_t_start,
            "term3_t_start": term3_t_start,
            "term4_t_start": term4_t_start,
            "term5_t_start": term5_t_start,
            "term6_t_start": term6_t_start,
            "term1_t_end": term1_t_end,
            "term2_t_end": term2_t_end,
            "term3_t_end": term3_t_end,
            "term4_t_end": term4_t_end,
            "term5_t_end": term5_t_end,
            "term6_t_end": term6_t_end,
            "term1_p_start": term1_p_start,
            "term2_p_start": term2_p_start,
            "term3_p_start": term3_p_start,
            "term4_p_start": term4_p_start,
            "term5_p_start": term5_p_start,
            "term6_p_start": term6_p_start,
            "term1_p_end": term1_p_end,
            "term2_p_end": term2_p_end,
            "term3_p_end": term3_p_end,
            "term4_p_end": term4_p_end,
            "term5_p_end": term5_p_end,
            "term6_p_end": term6_p_end,
        }
        phaseList = (
            semGroup.term1_t_end,
            semGroup.term2_t_end,
            semGroup.term3_t_end,
            semGroup.term4_t_end,
            semGroup.term5_t_end,
            semGroup.term6_t_end,
        )
        semesterIdx, modulesMandatory, modulesElective, modulesDict = getModules(
            currUser, currSemester, phaseList
        )

    context = {
        "user": currUser,
        "sgrp": semGroup,
        "course": course,
        "semester": currSemester,
        "phase": phaseDict,
        "terms": terms,
        "semesterIdx": semesterIdx,
        "modulesMandatory": modulesMandatory,
        "modulesElective": modulesElective,
        "modules": modulesDict,
    }
    return render(request, "organisationBlockManager.html", context)


def getSemester(user):
    if user.role != "Stu":
        return None

    today = dt.date.today()
    if user.seminargroup.rythm == "TP":
        term1Start = user.seminargroup.term1_t_start
        term2Start = user.seminargroup.term2_t_start
        term3Start = user.seminargroup.term3_t_start
        term4Start = user.seminargroup.term4_t_start
        term5Start = user.seminargroup.term5_t_start
        term6Start = user.seminargroup.term6_t_start
        term6End = user.seminargroup.term6_p_end
    else:
        term1Start = user.seminargroup.term1_p_start
        term2Start = user.seminargroup.term2_p_start
        term3Start = user.seminargroup.term3_p_start
        term4Start = user.seminargroup.term4_p_start
        term5Start = user.seminargroup.term5_p_start
        term6Start = user.seminargroup.term6_p_start
        term6End = user.seminargroup.term6_t_end

    if today > term6End:
        return 7
    elif today >= term6Start:
        return 6
    elif today >= term5Start:
        return 5
    elif today >= term4Start:
        return 4
    elif today >= term3Start:
        return 3
    elif today >= term2Start:
        return 2
    elif today >= term1Start:
        return 1
    else:
        return 0


def getModules(user, currSemester, phaseList):
    if user.role != "Stu":
        return None, None, None, None

    if currSemester > 6:
        semesterIdx = currSemester
    elif currSemester < 1:
        semesterIdx = 1
    else:
        today = dt.date.today()
        if user.seminargroup.rythm == "TP":
            for idx in range(6):
                if currSemester == idx + 1 and today > phaseList[idx]:
                    semesterIdx = currSemester + 1
                else:
                    semesterIdx = currSemester
        else:
            semesterIdx = currSemester

    mandModulesDict = []
    elecModulesDict = []
    mandatoryModules = Module.objects.filter(
        moduleType="mandatory", subject_id=user.seminargroup.course.id, term=semesterIdx
    )

    for module in mandatoryModules:
        title1 = f"{module.name} ({module.code})"
        lecturer1_1 = f"{module.lecturer1.last_name}, {module.lecturer1.first_name}"
        lecturer2_1 = None
        lecturer3_1 = None
        if module.lecturer2 != None:
            lecturer2_1 = f"{module.lecturer2.last_name}, {module.lecturer2.first_name}"
        if module.lecturer3 != None:
            lecturer3_1 = f"{module.lecturer3.last_name}, {module.lecturer3.first_name}"
        type1 = module.type
        ects1 = module.ects
        mandModulesDict.append(
            {
                "title": title1,
                "lecturer1": lecturer1_1,
                "lecturer2": lecturer2_1,
                "lecturer3": lecturer3_1,
                "type": type1,
                "ects": ects1,
            }
        )

    electiveModules = Module.objects.filter(
        moduleType="elective", subject_id=user.seminargroup.course.id, term=semesterIdx
    )

    for module in electiveModules:
        title2 = f"{module.name} ({module.code})"
        lecturer1_2 = f"{module.lecturer1.last_name}, {module.lecturer1.first_name}"
        lecturer2_2 = None
        lecturer3_2 = None
        if module.lecturer2 != None:
            lecturer2_2 = f"{module.lecturer2.last_name}, {module.lecturer2.first_name}"
        if module.lecturer3 != None:
            lecturer3_2 = f"{module.lecturer3.last_name}, {module.lecturer3.first_name}"
        type2 = module.type
        ects2 = module.ects
        elecModulesDict.append(
            {
                "title": title2,
                "lecturer1": lecturer1_2,
                "lecturer2": lecturer2_2,
                "lecturer3": lecturer3_2,
                "type": type2,
                "ects": ects2,
            }
        )

    query1 = Module.objects.filter(subject_id=user.seminargroup.course.id, term=1)

    term1Modules = []
    for module in query1:
        term1Modules.append(f"{module.name} ({module.code})")

    query2 = Module.objects.filter(subject_id=user.seminargroup.course.id, term=2)

    term2Modules = []
    for module in query2:
        term2Modules.append(f"{module.name} ({module.code})")

    query3 = Module.objects.filter(subject_id=user.seminargroup.course.id, term=3)

    term3Modules = []
    for module in query3:
        term3Modules.append(f"{module.name} ({module.code})")

    query4 = Module.objects.filter(subject_id=user.seminargroup.course.id, term=4)

    term4Modules = []
    for module in query4:
        term4Modules.append(f"{module.name} ({module.code})")

    query5 = Module.objects.filter(subject_id=user.seminargroup.course.id, term=5)

    term5Modules = []
    for module in query5:
        term5Modules.append(f"{module.name} ({module.code})")

    query6 = Module.objects.filter(subject_id=user.seminargroup.course.id, term=6)

    term6Modules = []
    for module in query6:
        term6Modules.append(f"{module.name} ({module.code})")

    termModuleDict = {
        "term1": term1Modules,
        "term2": term2Modules,
        "term3": term3Modules,
        "term4": term4Modules,
        "term5": term5Modules,
        "term6": term6Modules,
    }

    return semesterIdx, mandModulesDict, elecModulesDict, termModuleDict
