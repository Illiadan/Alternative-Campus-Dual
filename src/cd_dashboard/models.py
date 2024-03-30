import campusdual.settings as settings
import cd_core.models as cm
from django.db import models
from django.db.models.deletion import DO_NOTHING
from django.utils.translation import ugettext_lazy as _


class MessageBox(models.Model):

    author = models.ForeignKey(
        cm.User,
        on_delete=DO_NOTHING,
        verbose_name=_("Verfasser"),
        editable=False,
        null=True,
        blank=True,
    )

    posted = models.DateTimeField(
        verbose_name=_("veröffentlicht"), auto_now_add=True, null=True
    )

    lastEdited = models.DateTimeField(
        verbose_name=_("zuletzt bearbeitet"),
        auto_now=True,
        null=True,
    )

    title = models.CharField(verbose_name=_("Titel"), max_length=100, null=True)

    message = models.TextField(verbose_name=_("Nachricht"), max_length=250, null=True)

    readableByStudents = models.BooleanField(
        verbose_name=_("lesbar für Studenten"), default=False
    )

    readableByLecturers = models.BooleanField(
        verbose_name=_("lesbar für Dozenten"), default=False
    )

    readableByOrganisator = models.BooleanField(
        verbose_name=_("lesbar für Organisator"), editable=False, default=True
    )

    class Meta:
        verbose_name = _("Kurzmitteilung")
        verbose_name_plural = _("Kurzmitteilungen")

    def __str__(self):
        return f"{self.author.last_name}, {self.author.first_name}"
