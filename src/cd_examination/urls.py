from django.urls import path

from . import views

urlpatterns = [
    path("", views.switchToExaminationView),
    path("regUser", views.createUserReg),
    path("unregUser", views.deleteUserReg),
]
