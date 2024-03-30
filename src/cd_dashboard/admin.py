from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import MessageBox


class MessageBoxAdmin(admin.ModelAdmin):
    list_display = (
        "autor",
        "title",
        "post",
        "lastEdit",
        "readableByStudents",
        "readableByLecturers",
    )

    def autor(self, obj):
        return f"{obj.author.last_name}, {obj.author.first_name}"

    autor.short_description = _("Verfasser")

    def post(self, obj):
        timestamp = obj.posted.strftime("%d.%m.%Y %H:%M")
        return f"{timestamp}"

    post.short_description = _("veröffentlicht am")

    def lastEdit(self, obj):
        timestamp = obj.lastEdited.strftime("%d.%m.%Y %H:%M")
        return f"{timestamp}"

    lastEdit.short_description = _("zuletzt bearbeitet am")

    def save_model(self, request, obj, form, change):
        if getattr(obj, "author", None) is None:
            obj.author = request.user
            obj.save()
        else:
            super(MessageBox, obj).save()


admin.site.register(MessageBox, MessageBoxAdmin)
