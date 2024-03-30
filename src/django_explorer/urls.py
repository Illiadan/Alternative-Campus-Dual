from django.urls import path
from django.conf import settings
from .views import PlainExplorerView

urlpatterns = [path("", PlainExplorerView.as_include(root=settings.FILESERV_MOUNTPOINT))]
