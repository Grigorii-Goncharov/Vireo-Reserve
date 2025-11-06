from django.urls import path
from .views import (
    HomeView,
    # ContactsView,
    # ProductDetailView,
    # ProductsCreateView,
    # ProductsDeleteView,
    # ProductsUpdateView,
    # ProductsByCategoryView,
)

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('restaurant.urls')),  # или ваше приложение
]

# Только для DEBUG-режима!
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from restaurant.apps import RestaurantConfig
app_name = RestaurantConfig.name

urlpatterns = [
    path("", HomeView.as_view(), name="home"), # главная страница
    # path("contacts/", ContactsView.as_view(), name="contacts"),
    # path("product/<int:pk>/", cache_page(15)(ProductDetailView.as_view()), name="product"),
    # path("product/create/", ProductsCreateView.as_view(), name="create"),
    # path("product/update/<int:pk>/", ProductsUpdateView.as_view(), name="update"),
    # path("product/delete/<int:pk>/", ProductsDeleteView.as_view(), name="delete"),
    # path("category/<int:category_id>/",ProductsByCategoryView.as_view(),name="products_by_category"),
]