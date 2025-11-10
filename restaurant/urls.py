from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from restaurant.apps import RestaurantConfig
from . import views

app_name = RestaurantConfig.name

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),                  # Главная страница
    path("booking/", views.BookingView.as_view(), name="booking"),    # Забронировать
    path("booking/success/<int:pk>/", views.BookingSuccessView.as_view(), name="booking_success"),  # Подтверждение бронирования
    path("about/", views.AboutView.as_view(), name="about"),          # О ресторане
    path("profile/", views.ProfileView.as_view(), name="profile"),    # Личный кабинет
    path("cancel/<int:pk>/", views.cancel_reservation, name="cancel_reservation"),  # Отменить бронь
]

# Только для DEBUG-режима!
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)