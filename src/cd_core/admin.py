from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Course, Institution, Module, Room, Seminargroup, User


class UserAddForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = (
            "role",
            "email",
            "first_name",
            "last_name",
            "registration_number",
            "seminargroup",
        )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserEditForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput, required=False
    )

    class Meta:
        model = User
        fields = (
            "role",
            "email",
            "first_name",
            "last_name",
            "registration_number",
            "seminargroup",
        )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        if self.cleaned_data["password1"]:
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdmin(BaseUserAdmin):
    form = UserEditForm
    add_form = UserAddForm

    list_display = (
        "last_name",
        "first_name",
        "email",
        "registration_number",
        "role",
        "seminargroup",
        "is_active",
    )
    list_filter = ("role",)
    # when editing an user
    fieldsets = (
        ("Anmeldedaten", {"fields": ("email", "password1", "password2")}),
        (
            "Persönliche Daten",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "streetNameAndNumber",
                    "zipCode",
                    "city",
                    "gender",
                    "dateOfBirth",
                    "placeOfBirth",
                    "phoneNumber",
                    "nationality",
                )
            },
        ),
        (
            "Institutionelle Zuordnung",
            {"fields": ("registration_number", "seminargroup", "enrollmentDate")},
        ),
        (
            "Berechtigungen",
            {
                "fields": (
                    "role",
                    "is_active",
                )
            },
        ),
    )
    # when creating a new user
    add_fieldsets = (
        ("Anmeldedaten", {"fields": ("email", "password1", "password2")}),
        (
            "Persönliche Daten",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "streetNameAndNumber",
                    "zipCode",
                    "city",
                    "gender",
                    "dateOfBirth",
                    "placeOfBirth",
                    "phoneNumber",
                    "nationality",
                )
            },
        ),
        (
            "Institutionelle Zuordnung",
            {"fields": ("registration_number", "seminargroup", "enrollmentDate")},
        ),
        (
            "Berechtigungen",
            {
                "fields": (
                    "role",
                    "is_active",
                )
            },
        ),
    )
    search_fields = ("last_name", "email", "registration_number")
    ordering = ("role", "last_name")
    filter_horizontal = ()


class SeminargroupAdmin(admin.ModelAdmin):
    list_display = ("code", "enrollment_year")


class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "abbrev")


class ModuleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "abbrev",
        "term",
        "dozent1",
        "dozent2",
        "dozent3",
        "moduleType",
        "ects",
    )

    def dozent1(self, obj: Module) -> str:
        return f"{obj.lecturer1.last_name}, {obj.lecturer1.first_name}"

    dozent1.short_description = _("Dozent 1")

    def dozent2(self, obj: Module) -> str:
        if obj.lecturer2 == None:
            return "-"
        return f"{obj.lecturer2.last_name}, {obj.lecturer2.first_name}"

    dozent2.short_description = _("Dozent 2")

    def dozent3(self, obj: Module) -> str:
        if obj.lecturer3 == None:
            return "-"
        return f"{obj.lecturer3.last_name}, {obj.lecturer3.first_name}"

    dozent3.short_description = _("Dozent 3")

    def abbrev(self, obj: Module) -> str:
        return f"{obj.subject.abbrev}"

    abbrev.short_description = _("Studiengang")


class RoomAdmin(admin.ModelAdmin):
    list_display = ("raum", "institution")

    def raum(self, obj):
        return obj

    raum.short_description = _("Raum")


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("header", "city")

    def header(self, obj):
        return obj

    header.short_description = _("Institution")


admin.site.site_header = "Campus Dual Admin"

# to disable it
admin.site.unregister(Group)

admin.site.register(User, UserAdmin)
admin.site.register(Seminargroup, SeminargroupAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Institution, InstitutionAdmin)
