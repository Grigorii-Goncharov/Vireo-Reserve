from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('restaurant.urls'))
]

    # path("create/", BlogPostCreateView.as_view(), name="create"),
    # path("<int:pk>/", BlogPostDetailView.as_view(), name="detail"),
    # path("<int:pk>/edit/", BlogPostUpdateView.as_view(), name="update"),
    # path("<int:pk>/delete/", BlogPostDeleteView.as_view(), name="delete"),


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
