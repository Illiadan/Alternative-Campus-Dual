from datetime import timedelta
import cd_core.models as cm
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Lecture(models.Model):
    module = models.ForeignKey(
        cm.Module, on_delete=models.DO_NOTHING, verbose_name=_("Modul")
    )
    seminargroup = models.ForeignKey(
        cm.Seminargroup, on_delete=models.DO_NOTHING, verbose_name=_("Seminargruppe")
    )
    date = models.DateField(verbose_name=_("Vorlesungstermin"), null=True)
    start_time = models.TimeField(verbose_name=_("Vorlesungsbeginn"), null=True)
    end_time = models.TimeField(verbose_name=_("Vorlesungsende"), null=True)
    room = models.ForeignKey(
        cm.Room, on_delete=models.DO_NOTHING, verbose_name=_("Raum")
    )
    comment = models.TextField(blank=True, null=True, verbose_name=_("Kommentar"))
    lecturer = models.ForeignKey(
            cm.User, limit_choices_to={"role": "Lec"}, on_delete=models.DO_NOTHING, verbose_name=_("Dozent"), null=True
    )

    class Meta:
        verbose_name = _("Vorlesung")
        verbose_name_plural = _("Vorlesungen")

    def __str__(self):
        return f"VL: {self.module} für {self.seminargroup}; {self.date.strftime('%d.%m.%Y')}, {self.start_time} - {self.end_time}"

    def print_duration(self):
        return f'{self.start_time.strftime("%H:%M")}-{self.end_time.strftime("%H:%M")}'

    def print_to_timetable(self):
        offset_string = "" if self.start_time.minute % 30 == 0 else "position: relative; top: 2em;"
        html_string = ""
        
        start = timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
        end = timedelta(hours=self.end_time.hour, minutes=self.end_time.minute)

        dur = end - start;
        space = int((dur.total_seconds() // (60 * 30)) * 4)

        html_string += f"<div class='is-lecture' style='height: {space}em; {offset_string}'>\n"
        html_string += f"{self.print_duration()}</br>\n"
        html_string += f'<p class="title is-5">{self.module.code}</p>\n'
        html_string += f"{self.room}</br>\n"
        html_string += f"{self.lecturer.get_full_name()}</br>\n"
        html_string += f"{self.comment or ''}</br></div>\n"

        return html_string
