from __future__ import unicode_literals

from calendar import monthcalendar
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from datetime import date, datetime, timedelta

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import Permission, PermissionsMixin
from django.db import models
from django.db.models.deletion import DO_NOTHING, RESTRICT
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager


class Institution(models.Model):

    headInstitution = models.CharField(
        verbose_name=_("Hauptinstitution"), max_length=100, null=True
    )
    subInstitution = models.CharField(
        verbose_name=_("Unterinstitution"), max_length=100, null=True, unique=True
    )
    streetNameAndNumber = models.CharField(
        verbose_name=_("Anschrift - Straße und Hausnummer"), max_length=100, null=True
    )
    zipCode = models.CharField(
        verbose_name=_("Anschrift - Postleitzahl"), max_length=5, null=True
    )
    city = models.CharField(
        verbose_name=_("Anschrift - Ort"), max_length=100, null=True
    )

    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("     Institutionen")

    def __str__(self):
        return f"{self.headInstitution} - {self.city}"


class Course(models.Model):

    name = models.CharField(
        verbose_name=_("Bezeichnung"), max_length=100, null=True, unique=True
    )

    abbrev = models.CharField(
        verbose_name=_("Abkürzung"), max_length=5, null=True, unique=True
    )

    institution = models.ForeignKey(
        Institution, on_delete=DO_NOTHING, verbose_name=_("Institution")
    )

    DEGREE_CHOICES = [
        ("Bachelor of Science", "Bachelor of Science"),
        ("Bachelor of Arts", "Bachelor of Arts"),
        ("Bachelor of Engineering", "Bachelor of Engineering"),
    ]

    degree = models.CharField(
        verbose_name=_("Abschluss"), max_length=50, choices=DEGREE_CHOICES, null=True
    )

    class Meta:
        verbose_name = _("Studiengang")
        verbose_name_plural = _("    Studiengänge")

    def __str__(self):
        return f"{self.name}"


class Seminargroup(models.Model):
    code = models.CharField(_("Bezeichnung"), unique=True, max_length=50)

    course = models.ForeignKey(
        Course, on_delete=RESTRICT, null=True, verbose_name=_("Studiengang")
    )

    YEAR_CHOICES = []
    for year in range(2010, (datetime.now().year + 10)):
        YEAR_CHOICES.append((year, year))

    enrollment_year = models.IntegerField(
        _("Immatrikulationsjahr"),
        choices=YEAR_CHOICES,
        default=YEAR_CHOICES[-9],
    )

    THEORYFIRST = "TP"
    THEORYSECOND = "PT"
    RYTHM_CHOICES = [
        (THEORYFIRST, "Theorie -> Praxis"),
        (THEORYSECOND, "Praxis -> Theorie"),
    ]
    rythm = models.CharField(
        _("Phasenrythmus"), max_length=2, choices=RYTHM_CHOICES, default=THEORYFIRST
    )

    term1_t_start = models.DateField(editable=False, null=True)
    term1_t_end = models.DateField(editable=False, null=True)
    term1_p_start = models.DateField(editable=False, null=True)
    term1_p_end = models.DateField(editable=False, null=True)
    term2_t_start = models.DateField(editable=False, null=True)
    term2_t_end = models.DateField(editable=False, null=True)
    term2_p_start = models.DateField(editable=False, null=True)
    term2_p_end = models.DateField(editable=False, null=True)
    term3_t_start = models.DateField(editable=False, null=True)
    term3_t_end = models.DateField(editable=False, null=True)
    term3_p_start = models.DateField(editable=False, null=True)
    term3_p_end = models.DateField(editable=False, null=True)
    term4_t_start = models.DateField(editable=False, null=True)
    term4_t_end = models.DateField(editable=False, null=True)
    term4_p_start = models.DateField(editable=False, null=True)
    term4_p_end = models.DateField(editable=False, null=True)
    term5_t_start = models.DateField(editable=False, null=True)
    term5_t_end = models.DateField(editable=False, null=True)
    term5_p_start = models.DateField(editable=False, null=True)
    term5_p_end = models.DateField(editable=False, null=True)
    term6_t_start = models.DateField(editable=False, null=True)
    term6_t_end = models.DateField(editable=False, null=True)
    term6_p_start = models.DateField(editable=False, null=True)
    term6_p_end = models.DateField(editable=False, null=True)

    class Meta:
        verbose_name = _("Seminargruppe")
        verbose_name_plural = _("   Seminargruppen")

    def __str__(self):
        return self.code

    def save(self, check=False, *args, **kwargs):
        super(Seminargroup, self).save(*args, **kwargs)
        if check == False:
            self.createStudyTimeframe()

    def createStudyTimeframe(self):
        latestSeminargroupInDB = Seminargroup.objects.latest("id")
        year = latestSeminargroupInDB.enrollment_year
        rythm = latestSeminargroupInDB.rythm

        if rythm == "TP":
            latestSeminargroupInDB.term1_t_start = date(year, 10, 1)
            latestSeminargroupInDB.term1_t_end = date(
                year, 12, self.getSunday(year, 12)
            )
            latestSeminargroupInDB.term1_p_start = (
                latestSeminargroupInDB.term1_t_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term1_p_end = date(
                year + 1, 3, self.getSunday(year + 1, 3)
            )
            latestSeminargroupInDB.term2_t_start = (
                latestSeminargroupInDB.term1_p_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term2_t_end = date(
                year + 1, 6, self.getSunday(year + 1, 6)
            )
            latestSeminargroupInDB.term2_p_start = (
                latestSeminargroupInDB.term2_t_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term2_p_end = date(year + 1, 9, 30)
            latestSeminargroupInDB.term3_t_start = date(year + 1, 10, 1)
            latestSeminargroupInDB.term3_t_end = date(
                year + 1, 12, self.getSunday(year + 1, 12)
            )
            latestSeminargroupInDB.term3_p_start = (
                latestSeminargroupInDB.term3_t_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term3_p_end = date(
                year + 2, 3, self.getSunday(year + 2, 3)
            )
            latestSeminargroupInDB.term4_t_start = (
                latestSeminargroupInDB.term3_p_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term4_t_end = date(
                year + 2, 6, self.getSunday(year + 2, 6)
            )
            latestSeminargroupInDB.term4_p_start = (
                latestSeminargroupInDB.term4_t_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term4_p_end = date(year + 2, 9, 30)
            latestSeminargroupInDB.term5_t_start = date(year + 2, 10, 1)
            latestSeminargroupInDB.term5_t_end = date(
                year + 2, 12, self.getSunday(year + 2, 12)
            )
            latestSeminargroupInDB.term5_p_start = (
                latestSeminargroupInDB.term5_t_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term5_p_end = date(
                year + 3, 3, self.getSunday(year + 3, 3, 1)
            )
            latestSeminargroupInDB.term6_t_start = (
                latestSeminargroupInDB.term5_p_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term6_t_end = date(
                year + 3, 6, self.getSunday(year + 3, 6, 0)
            )
            latestSeminargroupInDB.term6_p_start = (
                latestSeminargroupInDB.term6_t_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term6_p_end = date(year + 3, 9, 30)

        else:
            latestSeminargroupInDB.term1_p_start = date(year, 10, 1)
            latestSeminargroupInDB.term1_p_end = date(
                year, 12, self.getSunday(year, 12)
            )
            latestSeminargroupInDB.term1_t_start = (
                latestSeminargroupInDB.term1_p_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term1_t_end = date(
                year + 1, 3, self.getSunday(year + 1, 3)
            )
            latestSeminargroupInDB.term2_p_start = (
                latestSeminargroupInDB.term1_t_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term2_p_end = date(
                year + 1, 6, self.getSunday(year + 1, 6)
            )
            latestSeminargroupInDB.term2_t_start = (
                latestSeminargroupInDB.term2_p_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term2_t_end = date(year + 1, 9, 30)
            latestSeminargroupInDB.term3_p_start = date(year + 1, 10, 1)
            latestSeminargroupInDB.term3_p_end = date(
                year + 1, 12, self.getSunday(year + 1, 12)
            )
            latestSeminargroupInDB.term3_t_start = (
                latestSeminargroupInDB.term3_p_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term3_t_end = date(
                year + 2, 3, self.getSunday(year + 2, 3)
            )
            latestSeminargroupInDB.term4_p_start = (
                latestSeminargroupInDB.term3_t_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term4_p_end = date(
                year + 2, 6, self.getSunday(year + 2, 6)
            )
            latestSeminargroupInDB.term4_t_start = (
                latestSeminargroupInDB.term4_p_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term4_t_end = date(year + 2, 9, 30)
            latestSeminargroupInDB.term5_p_start = date(year + 2, 10, 1)
            latestSeminargroupInDB.term5_p_end = date(
                year + 2, 12, self.getSunday(year + 2, 12)
            )
            latestSeminargroupInDB.term5_t_start = (
                latestSeminargroupInDB.term5_p_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term5_t_end = date(
                year + 3, 3, self.getSunday(year + 3, 3, 1)
            )
            latestSeminargroupInDB.term6_p_start = (
                latestSeminargroupInDB.term5_t_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term6_p_end = date(
                year + 3, 6, self.getSunday(year + 3, 6, 0)
            )
            latestSeminargroupInDB.term6_t_start = (
                latestSeminargroupInDB.term6_p_end + timedelta(days=1)
            )
            latestSeminargroupInDB.term6_t_end = date(year + 3, 9, 30)

        latestSeminargroupInDB.save(True)

    def getSunday(self, year, month, weekValue=-1):
        if weekValue == -1:
            return max(week[-1] for week in monthcalendar(year, month))
        return monthcalendar(year, month)[weekValue][-1]


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name=_("Email-Adresse"), unique=True)
    first_name = models.CharField(verbose_name=_("Vorname"), max_length=50)
    last_name = models.CharField(verbose_name=_("Nachname"), max_length=50)
    streetNameAndNumber = models.CharField(
        verbose_name=_("Anschrift - Straße und Hausnummer"), max_length=100, null=True
    )
    zipCode = models.CharField(verbose_name=_("Anschrift - Postleitzahl"), max_length=5)
    city = models.CharField(verbose_name=_("Anschrift - Ort"), max_length=100)

    GENDER_CHOICES = [
        ("m", "männlich"),
        ("w", "weiblich"),
        ("d", "divers"),
    ]

    gender = models.CharField(
        verbose_name=_("Geschlecht"), max_length=1, choices=GENDER_CHOICES, null=True
    )
    dateOfBirth = models.DateField(verbose_name=_("Geburtstag"), null=True)
    placeOfBirth = models.CharField(
        verbose_name=_("Geburtsort"), max_length=100, null=True
    )
    phoneNumber = models.CharField(
        verbose_name=_("Telefonnummer"), max_length=30, null=True
    )
    nationality = models.CharField(
        verbose_name=_("Staatsangehörigkeit"), max_length=100, null=True
    )
    is_active = models.BooleanField(_("Aktiv"), default=True)
    is_staff = models.BooleanField(default=False)  # for logging into admin interface
    is_superuser = models.BooleanField(default=False)  # assign all permissions
    registration_number = models.CharField(
        verbose_name=_("Matrikelnummer / Personalnummer"),
        max_length=7,
        unique=True,
        null=True,
    )
    seminargroup = models.ForeignKey(
        Seminargroup, on_delete=models.DO_NOTHING, default=None, null=True, blank=True
    )
    STUDENT = "Stu"
    LECTURER = "Lec"
    ORGANISATOR = "Org"
    ROLE_CHOICES = [
        (STUDENT, "Student"),
        (LECTURER, "Lecturer"),
        (ORGANISATOR, "Organisator"),
    ]

    if date.today().day >= 1 and date.today().month >= 10:
        year = date.today().year + 1
    else:
        year = date.today().year
    enrollmentDate = models.DateField(
        verbose_name=_("Immatrikulationsdatum"),
        default=date(year, 10, 1),
        null=True,
        blank=True,
    )
    role = models.CharField(
        _("Rolle"), max_length=3, choices=ROLE_CHOICES, default=STUDENT
    )
    ects = models.PositiveIntegerField(
        verbose_name=_("ECTS-Punkte"), editable=False, default=0
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "registration_number"]

    class Meta:
        verbose_name = _("Benutzer")
        verbose_name_plural = _("  Benutzer")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        self.is_staff = True if self.role == User.ORGANISATOR else False

        cts = [
                ContentType.objects.get_for_model(apps.get_model("cd_core", "Institution")),
                ContentType.objects.get_for_model(apps.get_model("cd_core", "Course")),
                ContentType.objects.get_for_model(apps.get_model("cd_core", "Seminargroup")),
                ContentType.objects.get_for_model(apps.get_model("cd_core", "User")),
                ContentType.objects.get_for_model(apps.get_model("cd_core", "Room")),
                ContentType.objects.get_for_model(apps.get_model("cd_core", "Module")),
                ContentType.objects.get_for_model(apps.get_model("cd_dashboard", "MessageBox")),
                ContentType.objects.get_for_model(apps.get_model("cd_examination", "Examination")),
                ContentType.objects.get_for_model(apps.get_model("cd_examination", "ExamRegistration")),
                ContentType.objects.get_for_model(apps.get_model("cd_examination", "ExamResult")),
                ContentType.objects.get_for_model(apps.get_model("cd_timetable", "Lecture")),
            ]

        for ct in cts:
            perms = Permission.objects.filter(content_type=ct)
            for perm in perms:
                self.user_permissions.add(perm)

        super().save(*args, **kwargs)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def __str__(self):
        header = "%s, %s (%s)" % (self.last_name, self.first_name, self.email)
        return header


class Room(models.Model):

    code = models.CharField(max_length=100, unique=True)

    institution = models.ForeignKey(
        Institution, on_delete=DO_NOTHING, verbose_name=_("Institution")
    )

    class Meta:
        verbose_name = _("Raum")
        verbose_name_plural = _(" Räume")

    def __str__(self):
        return self.code


class Module(models.Model):

    name = models.CharField(verbose_name=_("Modulname"), max_length=300, null=True)

    code = models.CharField(_("Modulcode"), max_length=100, unique=True)

    subject = models.ForeignKey(
        Course, on_delete=RESTRICT, null=True, verbose_name=_("Studiengang")
    )

    MANDATORY = "mandatory"
    ELECTIVE = "elective"
    MODULETYPE_CHOICES = [(MANDATORY, "Pflichtmodul"), (ELECTIVE, "Wahlpflichtmodul")]

    moduleType = models.CharField(
        verbose_name=_("Modulart"),
        max_length=16,
        choices=MODULETYPE_CHOICES,
        default=MANDATORY,
    )

    TERM_CHOICES = []
    for t in range(1, 7):
        TERM_CHOICES.append((t, f"{t}"))

    term = models.IntegerField(
        verbose_name=_("Semester"),
        choices=TERM_CHOICES,
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
        verbose_name=_("Prüfungsart"), max_length=2, choices=TYPE_CHOICES, null=True
    )

    lecturer1 = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        verbose_name="Dozent",
        limit_choices_to={"role": "Lec"},
        related_name="lecturer1",
        null=True,
    )

    lecturer2 = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        verbose_name="Dozent",
        limit_choices_to={"role": "Lec"},
        related_name="lecturer2",
        null=True,
        blank=True,
    )

    lecturer3 = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        verbose_name="Dozent",
        limit_choices_to={"role": "Lec"},
        related_name="lecturer3",
        null=True,
        blank=True,
    )

    ects = models.PositiveIntegerField(verbose_name=_("ECTS-Punkte"), null=True)

    class Meta:
        verbose_name = _("Modul")
        verbose_name_plural = _("Module")

    def __str__(self):
        return f"{self.name} ({self.code})"
