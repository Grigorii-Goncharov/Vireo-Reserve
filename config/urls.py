from restaurant.apps import RestaurantConfig

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from restaurant.apps import RestaurantConfig
from restaurant.views import (
    HomeView,
    # BlogPostDetailView,
    # BlogPostCreateView,
    # BlogPostUpdateView,
    # BlogPostDeleteView,
)



app_name = RestaurantConfig.name

urlpatterns = [
    path("", HomeView.as_view(), name="list"),
    # path("create/", BlogPostCreateView.as_view(), name="create"),
    # path("<int:pk>/", BlogPostDetailView.as_view(), name="detail"),
    # path("<int:pk>/edit/", BlogPostUpdateView.as_view(), name="update"),
    # path("<int:pk>/delete/", BlogPostDeleteView.as_view(), name="delete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
