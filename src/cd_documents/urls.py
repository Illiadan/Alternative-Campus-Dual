from django.urls import path

from . import views

urlpatterns = [
    path("", views.switchToDocumentationView),
    path("stuDoc1", views.stuDoc1View),
    path("stuDoc2", views.stuDoc2View),
    path("stuDoc3", views.stuDoc3View),
    path("stuDoc4", views.stuDoc4View),
    path("lecDoc1", views.lecDoc1View),
    path("lecDoc2", views.lecDoc2View),
]
