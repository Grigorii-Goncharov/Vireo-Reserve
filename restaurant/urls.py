from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from restaurant.apps import RestaurantConfig

from . import views

app_name = RestaurantConfig.name

urlpatterns = [
    # главная
    path("", views.HomeView.as_view(), name="home"),
    # о сайте
    path("about/", views.AboutView.as_view(), name="about"),
    # станица с бронированием столиков
    path("booking/", views.BookingView.as_view(), name="booking"),
    # просмотр профиля пользователя
    path("profile/", views.ProfileView.as_view(), name="profile"),
    # бронирование столика
    path(
        "booking/success/<int:pk>/",
        views.BookingSuccessView.as_view(),
        name="booking_success",
    ),
    # отмена бронирования
    path("cancel/<int:pk>/", views.cancel_reservation, name="cancel_reservation"),
    # для проверки доступности столика
    path("check_availability/", views.check_availability, name="check_availability"),
    # для редактирования бронирования
    path("edit/<int:pk>/", views.edit_reservation, name="edit_reservation"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
