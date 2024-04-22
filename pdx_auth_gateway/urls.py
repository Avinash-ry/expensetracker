from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from pdx_auth.views import UploadProcessView

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("expense/", admin.site.urls),

    path(
        "expense/",
        UploadProcessView.as_view(),
        name="upload",
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
