import datetime as dt
from datetime import timedelta

import cd_core.models as cm
from django.db import models
from django.db.models.deletion import DO_NOTHING, RESTRICT
from django.utils.translation import ugettext_lazy as _


class Examination(models.Model):

    module = models.ForeignKey(
        cm.Module, on_delete=models.DO_NOTHING, verbose_name=_("Modul")
    )
    seminargroup = models.ForeignKey(
        cm.Seminargroup, on_delete=models.DO_NOTHING, verbose_name=_("Seminargruppe")
    )
    date = models.DateField(verbose_name=_("Prüfungstermin"), null=True)
    start_time = models.TimeField(verbose_name=_("Prüfungsbeginn"), null=True)
    end_time = models.TimeField(verbose_name=_("Prüfungsende"), null=True)
    room = models.ForeignKey(
        cm.Room, on_delete=models.DO_NOTHING, verbose_name=_("Raum")
    )

    EXAM = "K"
    COMPUTEREXAM = "C"
    PRESENTATION = "P"
    ESSAY = "SE"
    PAPER = "PR"
    ORALEXAM = "M"
    THESIS = "BT"

    TYPE_CHOICES = [
        (EXAM, _("Klausur")),
        (COMPUTEREXAM, _("Computerklausur")),
        (PRESENTATION, _("Präsentation")),
        (ESSAY, _("Hausarbeit")),
        (PAPER, _("Projektarbeit")),
        (ORALEXAM, _("Mündliche Prüfung")),
        (THESIS, _("Bachelor Thesis")),
    ]

    type = models.CharField(
        verbose_name=_("Prüfungsart"), max_length=2, choices=TYPE_CHOICES
    )

    enrollmentDeadline = models.DateTimeField(
        verbose_name=_("Anmeldeschluss"),
        null=True,
    )

    createdAt = models.DateTimeField(
        editable=False,
        auto_now_add=True,
        null=True,
    )

    comment = models.TextField(verbose_name=_("Kommentar"), blank=True, null=True)

    class Meta:
        verbose_name = _("Prüfung")
        verbose_name_plural = _("Prüfungen")

    def __str__(self):
        return f"PR: {self.module.code} ({self.seminargroup}) - {self.date.strftime('%d.%m.%Y')} {self.start_time.strftime('%H:%M')}"

    def print_duration(self):
        return f'{self.start_time.strftime("%H:%M")}-{self.end_time.strftime("%H:%M")}'

    def print_to_timetable(self):
        offset_string = (
            "" if self.start_time.minute % 30 == 0 else "position: relative; top: 2em;"
        )
        html_string = ""

        start = timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
        end = timedelta(hours=self.end_time.hour, minutes=self.end_time.minute)

        dur = end - start
        space = int((dur.total_seconds() // (60 * 30)) * 4)

        html_string += (
            f"<div class='is-exam' style='height: {space}em; {offset_string}'>\n"
        )
        html_string += f"{self.print_duration()}</br>\n"
        html_string += f'<p class="title is-5">{self.type}: {self.module.code}</p>\n'
        html_string += f"{self.room}</br>\n"
        html_string += f"{self.comment or ''}</br></div>\n"

        return html_string


class ExamRegistration(models.Model):

    examination = models.ForeignKey(
        to=Examination, verbose_name=_("Prüfung"), on_delete=RESTRICT, null=True
    )

    participant = models.ForeignKey(
        to=cm.User,
        verbose_name=_("Teilnehmer"),
        on_delete=RESTRICT,
        null=True,
        limit_choices_to={"role": "Stu"},
    )

    attempt = models.PositiveSmallIntegerField(
        verbose_name=_("Versuch"), editable=False, null=True
    )

    createdAt = models.DateTimeField(
        verbose_name=_("Angemeldet am"), auto_now_add=True, null=True
    )

    result = models.DecimalField(
        verbose_name=_("Ergebnis"),
        editable=False,
        null=True,
        max_digits=3,
        decimal_places=1,
    )

    evaluationCompletion = models.DateTimeField(
        verbose_name=_("Beurteilung vom"), editable=False, null=True
    )

    resultPublication = models.DateTimeField(
        verbose_name=_("Veröffentlicht am"), editable=False, null=True
    )

    def save(self, *args, **kwargs):
        super(ExamRegistration, self).save(*args, **kwargs)
        getAttempt(self)

    class Meta:
        unique_together = ("examination", "participant", "evaluationCompletion")
        verbose_name = _("Prüfungsanmeldung")
        verbose_name_plural = _("Prüfungsanmeldungen")

    def __str__(self):
        return f"{self.examination.module}"


class ExamResult(models.Model):

    examination = models.ForeignKey(
        to=Examination, verbose_name=_("Prüfung"), on_delete=RESTRICT, null=True
    )

    evaluationCompletion = models.DateTimeField(
        verbose_name=_("Beurteilung vom"), null=True
    )

    results = models.TextField(
        verbose_name=_("Ergebnisse"),
        help_text=_(
            """Bitte geben Sie die Ergebnisse in folgender Form ein:</br>
            <b>Matrikelnummer, Note ohne Komma,</b></br> 
            Beispiel: 5001001, 27,</br>
            (Noten: 1,0 = 10; 1,3 = 13; 2,7 = 27; etc.)</br>
            (Zeilenumbrüche sind gestattet)"""
        ),
    )

    createdAt = models.DateTimeField(
        verbose_name=_("Veröffentlicht am"), auto_now_add=True, null=True
    )

    lastEdited = models.DateTimeField(
        verbose_name=_("Zuletzt geändert am"), auto_now=True, null=True
    )

    def save(self, *args, **kwargs):
        super(ExamResult, self).save(*args, **kwargs)
        assignResultsToStudents(self)

    def delete(self, *args, **kwargs):
        revertResults(self)
        super(ExamResult, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = _("Prüfungsergebnis")
        verbose_name_plural = _("Prüfungsergebnisse")

    def __str__(self):
        return f"{self.examination.module}"


class ExamRecognition(models.Model):
    user = models.ForeignKey(
        cm.User,
        on_delete=DO_NOTHING,
        verbose_name=_("Student"),
        limit_choices_to={"role": "Stu"},
    )

    module = models.ForeignKey(
        cm.Module,
        on_delete=DO_NOTHING,
        verbose_name=_("Modul"),
    )

    result = models.DecimalField(
        verbose_name=_("Ergebnis"), max_digits=2, decimal_places=1, null=True
    )

    createdAt = models.DateField(
        verbose_name=_("Anerkannt am"), auto_now_add=True, editable=False, null=True
    )

    lastEditedAt = models.DateTimeField(
        verbose_name=_("zuletzt editiert am"), auto_now=True, editable=False, null=True
    )

    def save(self, *args, **kwargs):
        super(ExamRecognition, self).save(*args, **kwargs)
        assignRecResults(self)

    def delete(self, *args, **kwargs):
        revertRecResults(self)
        super(ExamRecognition, self).delete(*args, **kwargs)

    class Meta:
        unique_together = ("user", "module")
        verbose_name = _("Prüfungsanerkennung")
        verbose_name_plural = _("Prüfungsanerkennungen")

    def __str__(self):
        return f"{self.user.last_name}, {self.user.first_name}"


def getAttempt(obj):
    query = ExamRegistration.objects.filter(
        examination__module=obj.examination.module,
        participant=obj.participant,
        attempt__isnull=False,
    )
    examQS = ExamRegistration.objects.filter(
        examination__module=obj.examination.module,
        participant=obj.participant,
        attempt__isnull=True,
    )
    if len(examQS) == 0:
        return

    exam = examQS[0]

    if len(query) == 0:
        exam.attempt = 1
    else:
        maxAtempts = max(q.attempt for q in query)
        exam.attempt = maxAtempts + 1
    exam.save()


def assignResultsToStudents(obj):
    """Function takes in an object of type ExamResult.
    This contents of a TextField of format "Matrikelnummer, Note ohne Komma,".
    All pairs of User and Result are found out and written into the DB accordingly."""

    examId = obj.examination.id
    exams = ExamRegistration.objects.filter(examination_id=examId)

    text = obj.results
    listOfText = text.replace(" ", "").replace("\r", "").replace("\n", "").split(",")
    listOfMatriculation = []
    listOfResults = []

    for idx in range(len(listOfText)):
        if idx % 2 == 0:
            listOfMatriculation.append(listOfText[idx])
        else:
            a, b = listOfText[idx][:1], listOfText[idx][1:]
            listOfResults.append(f"{a}.{b}")

    matriculationResultTuples = list(zip(listOfMatriculation, listOfResults))

    for exam in exams:
        regNumber = exam.participant.registration_number.upper().replace("S", "")
        for tuple in matriculationResultTuples:
            if regNumber == tuple[0]:
                oldResult = exam.result
                newResult = tuple[1]
                user = cm.User.objects.filter(registration_number=regNumber)[0]
                if oldResult == None:
                    if float(newResult) <= 4.0:
                        user.ects += exam.examination.module.ects
                elif float(oldResult) != float(newResult):
                    if float(newResult) <= 4.0 and float(oldResult) > 4.0:
                        user.ects += exam.examination.module.ects
                    elif float(newResult) > 4.0 and float(oldResult) <= 4.0:
                        user.ects -= exam.examination.module.ects
                user.save()
                exam.result = tuple[1]
                exam.evaluationCompletion = obj.evaluationCompletion
                exam.resultPublication = obj.lastEdited
                exam.save()
                break


def revertResults(obj):
    text = obj.results
    listOfText = text.replace(" ", "").replace("\r", "").replace("\n", "").split(",")
    listOfMatriculation = []
    listOfResults = []

    for idx in range(len(listOfText)):
        if idx % 2 == 0:
            listOfMatriculation.append(listOfText[idx])
        else:
            a, b = listOfText[idx][:1], listOfText[idx][1:]
            listOfResults.append(f"{a}.{b}")

    matriculationResultTuples = list(zip(listOfMatriculation, listOfResults))

    for tpl in matriculationResultTuples:
        user = cm.User.objects.filter(registration_number=tpl[0])[0]
        exam = ExamRegistration.objects.filter(
            examination=obj.examination, participant=user
        )[0]

        if float(exam.result) <= 4.0:
            user.ects -= obj.examination.module.ects
            user.save()

        exam.result = None
        exam.save()


def assignRecResults(obj):
    currUser = obj.user
    currModule = obj.module

    examination = Examination(
        module=currModule,
        seminargroup=currUser.seminargroup,
        date=dt.date.today(),
        start_time=dt.time(hour=0, minute=0),
        end_time=dt.time(hour=0, minute=0),
        room=cm.Room.objects.filter(code="Sekretariat")[0],
        type=currModule.type,
        enrollmentDeadline=dt.datetime.now(),
    )
    examination.save()

    examRegistration = ExamRegistration(
        examination=examination,
        participant=currUser,
        attempt=4,
        createdAt=dt.datetime.now(),
        result=obj.result,
        evaluationCompletion=dt.datetime.now(),
        resultPublication=dt.datetime.now(),
    )
    examRegistration.save()

    if examRegistration.result <= 4.0:
        currUser.ects += currModule.ects
        currUser.save()


def revertRecResults(obj):
    currUser = obj.user
    currModule = obj.module

    examReg = ExamRegistration.objects.filter(
        examination__module=currModule, participant=currUser
    )[0]
    examinationId = examReg.examination_id

    if examReg.result <= 4.0:
        currUser.ects -= currModule.ects
        currUser.save()
    examReg.delete()

    exam = Examination.objects.filter(id=examinationId)[0]
    exam.delete()
