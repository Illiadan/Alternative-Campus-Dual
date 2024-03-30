from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import (
    Examination,
    ExamRecognition,
    ExamRegistration,
    ExamResult,
    revertRecResults,
    revertResults,
)


class ExaminationAdmin(admin.ModelAdmin):
    list_display = ("module", "seminargroup", "date", "time", "room")

    def time(self, obj: Examination) -> str:
        return f"{obj.start_time} - {obj.end_time}"

    time.short_description = _("Uhrzeit")


class ExamResultAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            revertResults(obj)
        queryset.delete()


class ExamRecognitionAdmin(admin.ModelAdmin):
    list_display = ("student", "regNumber", "moduleCode")

    def student(self, obj: ExamRecognition) -> str:
        return f"{obj.user.last_name}, {obj.user.first_name}"

    student.short_description = _("Student*in")

    def regNumber(self, obj: ExamRecognition) -> str:
        return f"{obj.user.registration_number}"

    regNumber.short_description = _("Matrikelnummer")

    def moduleCode(self, obj: ExamRecognition) -> str:
        return f"{obj.module.code}"

    moduleCode.short_description = _("Modul")

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            revertRecResults(obj)
        queryset.delete()


admin.site.register(Examination, ExaminationAdmin)
admin.site.register(ExamRegistration)
admin.site.register(ExamResult, ExamResultAdmin)
admin.site.register(ExamRecognition, ExamRecognitionAdmin)
