
from .views import (
    HomeView, BookingView, AboutView,
)
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from restaurant.apps import RestaurantConfig
from . import views

app_name = RestaurantConfig.name



urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("booking/", views.BookingView.as_view(), name="booking"),
    path("about/", views.AboutView.as_view(), name="about"),
]
    # path("product/<int:pk>/", cache_page(15)(ProductDetailView.as_view()), name="product"),
    # path("product/create/", ProductsCreateView.as_view(), name="create"),
    # path("product/update/<int:pk>/", ProductsUpdateView.as_view(), name="update"),
    # path("product/delete/<int:pk>/", ProductsDeleteView.as_view(), name="delete"),
    # path("category/<int:category_id>/",ProductsByCategoryView.as_view(),name="products_by_category"),


# Только для DEBUG-режима!
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
