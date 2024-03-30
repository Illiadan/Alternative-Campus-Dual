from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Lecture

class ModuleSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
            option = super().create_option(name, value, label, selected, index, subindex, attrs)
            if value:
                if value.instance.lecturer1:
                    option['attrs']['data-lecone'] = value.instance.lecturer1.id
                if value.instance.lecturer2:
                    option['attrs']['data-lectwo'] = value.instance.lecturer2.id
                if value.instance.lecturer3:
                    option['attrs']['data-lecthr'] = value.instance.lecturer3.id
            return option
    

class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['module', 'lecturer', 'date', 'start_time', 'end_time', 'seminargroup', 'room']
        widgets = {'module': ModuleSelect}


class LectureAdmin(ModelAdmin):
    form = LectureForm
    add_form = LectureForm
    change_form_template = 'lecture_form_js.html'

    list_display = (
        "module",
        "seminargroup",
        "date",
        "start_time",
        "end_time",
        "room",
    )

admin.site.register(Lecture, LectureAdmin)
