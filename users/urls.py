from django.urls import path

from . import views
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.contrib.auth.views import LogoutView

app_name = "users"

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path("profile_edit/", views.UserProfileEditView.as_view(), name="profile_edit"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("email-confirm/<str:token>/", views.email_verification, name="email-confirm"),
    path("users/toggle/<int:pk>/", views.toggle_user_active, name="toggle_user_active"),
    path("delete/<int:pk>/", views.delete_user, name="delete_user"),


    # Сброс и восстановление пароля:
    path(
        "password-reset/",
        PasswordResetView.as_view(
            template_name="users/password_reset.html",
            email_template_name="users/password_reset_email.html",  # Шаблон письма
            success_url="/users/password-reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url="/users/reset/done/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]