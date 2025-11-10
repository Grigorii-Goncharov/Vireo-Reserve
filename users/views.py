import secrets
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.views import View

from config.settings import EMAIL_HOST_USER
from .forms import CustomUserCreationForm, UserProfileForm
from .models import User


class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)  # Сохраняем пользователя без логирования
        user.is_active = False  # Деактивируем
        token = secrets.token_hex(16)  # Генерация токена
        user.token = token
        user.save()

        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject="Подтверждение почты при регистрации аккаунта",
            message=f"Перейдите по ссылке {url} для завершения регистрации",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        messages.info(
            self.request, "Письмо подтверждения регистрации направлено на почту"
        )
        return redirect(self.success_url)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)

    if user.is_active:
        # Уже активен — просто перенаправляем
        messages.info(request, "Ваш email уже подтверждён. Вы можете войти.")
        return redirect("users:login")

    # Активируем
    user.is_active = True
    user.token = None  # Обнуляем токен, чтобы можно было использовать его для сброса пароля позже
    user.save()

    messages.success(request, "Email подтверждён! Теперь можно войти.")
    return redirect("users:login")


class UserProfileView(DetailView):
    template_name = "users/profile.html"
    context_object_name = "user_profile"

    def get_object(self, queryset=None):
        return self.request.user


class UserLoginView(LoginView):
    template_name = "users/login.html"


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user


@login_required
def toggle_user_active(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied("У вас нет прав для изменения статуса пользователя.")

    user = get_object_or_404(User, pk=pk)

    # Защита от самоблокирования
    if user.pk == request.user.pk:
        messages.error(request, "Нельзя заблокировать самого себя!")
        return redirect("users:user_list")

    # Переключаем статус
    user.is_active = not user.is_active
    user.save()

    # Оповещение — что изменилось
    if user.is_active:
        messages.success(request, f"Пользователь {user.username} разблокирован.")
    else:
        messages.warning(request, f"Пользователь {user.username} заблокирован.")

    return redirect("users:user_list")