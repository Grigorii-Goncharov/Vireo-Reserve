from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import set_language

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("restaurant.urls")),
    path("i18n/", set_language, name="set_language"),
    path("users/", include("users.urls")),
]

# path("create/", BlogPostCreateView.as_view(), name="create"),
# path("<int:pk>/", BlogPostDetailView.as_view(), name="detail"),
# path("<int:pk>/edit/", BlogPostUpdateView.as_view(), name="update"),
# path("<int:pk>/delete/", BlogPostDeleteView.as_view(), name="delete"),


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
