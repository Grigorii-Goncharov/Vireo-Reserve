import secrets

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from django.views.generic import CreateView, DetailView, UpdateView

from config.settings import EMAIL_HOST_USER
from restaurant.models import TableReservation

from .forms import CustomUserCreationForm, UserProfileForm
from .models import User
from .services import send_telegram_message


# USER CRUD
class UserRegisterView(CreateView):
    """
    Представление для регистрации нового пользователя.
    При успешной регистрации отправляет письмо для подтверждения email
    и (опционально) приветственное сообщение в Telegram, если указан chat_id.
    """

    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        """
        Обработка валидной формы регистрации.

        Создает пользователя с неактивным статусом, генерирует токен подтверждения,
        отправляет сообщение в Telegram (если возможно) и письмо с подтверждением.
        """
        user = form.save(commit=False)  # Сохраняем пользователя без логирования
        user.is_active = False  # Деактивируем
        token = secrets.token_hex(16)  # Генерация токена
        user.token = token
        user.save()

        if user.telegram_chat_id:
            try:
                message = "Добро пожаловать в ресторан Vireo Reserve!"
                send_telegram_message(chat_id=user.telegram_chat_id, message=message)
            except Exception as e:
                print(f"Ошибка отправки Telegram: {e}")

        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"

        # Рендерим HTML-письмо
        html_message = render_to_string(
            "users/email_confirmation.html",
            {
                "protocol": "http",
                "domain": host,
                "url": url,
            },
        )

        # Текстовая версия (на случай, если клиент не поддерживает HTML)
        plain_message = strip_tags(html_message)

        send_mail(
            subject="Подтверждение почты",
            message=plain_message,
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=html_message,  # ← ключевая строка!
        )

        messages.info(self.request, "Проверьте почту для подтверждения email.")
        return redirect(self.success_url)


# Подтверждение регистрации через почту:
def email_verification(request, token):
    """
    Представление для подтверждения email пользователя по токену.
    Активирует пользователя, если токен действителен и аккаунт еще не активирован.
    """
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


class UserProfileView(LoginRequiredMixin, DetailView):
    """
    Представление для просмотра профиля пользователя.
    Отображает данные текущего авторизованного пользователя и его
    историю бронирований с пагинацией.
    """

    template_name = "users/profile.html"
    context_object_name = "user_profile"

    def get_object(self, queryset=None):
        """Возвращает текущего пользователя."""
        return self.request.user

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст список бронирований текущего пользователя
        с пагинацией (5 на страницу).
        """
        context = super().get_context_data(**kwargs)
        # Получаем все бронирования текущего пользователя, отсортированные по дате создания (новые сверху)
        all_reservations = TableReservation.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

        # Создаем объект Paginator
        paginator = Paginator(all_reservations, 5)  # 5 броней на страницу

        # Получаем номер страницы из GET-параметра
        page_number = self.request.GET.get("page")
        # Получаем объект страницы
        page_obj = paginator.get_page(page_number)

        # Передаем page_obj в контекст, а не all_reservations
        context["reservations"] = page_obj
        return context


class UserLoginView(LoginView):
    """
    Представление для входа пользователя в систему.
    """

    template_name = "users/login.html"


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования профиля текущего пользователя.
    """

    form_class = UserProfileForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        """Возвращает текущего пользователя для редактирования."""
        return self.request.user


@login_required
def toggle_user_active(request, pk):
    """
    Представление для переключения статуса активности пользователя (активен/неактивен).
    Доступно только суперпользователям. Предотвращает деактивацию самого себя.
    """
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


@login_required
def delete_user(request, pk):
    """
    Представление для удаления пользователя.
    Если удаляет сам себя, происходит выход из системы.
    """
    user = get_object_or_404(User, pk=pk)
    if user.pk == request.user.pk:
        username = request.user.get_full_name() or request.user.username
        request.user.delete()

        # Важно: разлогиниваемся ПОСЛЕ удаления, но до редиректа
        logout(request)

        # username = user.username
        # user.delete()

        messages.success(request, f"Пользователь {username} успешно удалён.")
        # return redirect("users:user_list")
        return redirect("users:login")
    # else:
    #     messages.error(request, "У вас нет прав для удаления этого пользователя.")
    #     return redirect("users:profile")
