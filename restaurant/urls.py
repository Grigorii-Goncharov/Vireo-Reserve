# restaurant/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from restaurant.apps import RestaurantConfig
from . import views

app_name = RestaurantConfig.name

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("booking/", views.BookingView.as_view(), name="booking"),
    path("booking/success/<int:pk>/", views.BookingSuccessView.as_view(), name="booking_success"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("cancel/<int:pk>/", views.cancel_reservation, name="cancel_reservation"),
    # Новый маршрут для проверки доступности
    path("check_availability/", views.check_availability, name="check_availability"),
    # Новый маршрут для редактирования бронирования
    path("edit/<int:pk>/", views.edit_reservation, name="edit_reservation"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)