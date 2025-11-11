# restaurant/views.py

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    TemplateView, CreateView, DetailView, ListView, UpdateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.db.models import Q

from .models import Table, TableReservation, Feedback
from .forms import BookingForm
from config import settings
from datetime import datetime, date, time


# --- Представления для общедоступных страниц ---

class HomeView(TemplateView):
    template_name = "restaurant/home.html"

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        message = request.POST.get('message')
        if email and message:
            Feedback.objects.create(email=email, message=message)
            messages.success(request, "Ваше сообщение успешно отправлено! Спасибо за обратную связь.")
            return redirect('restaurant:home')
        else:
            messages.error(request, "Пожалуйста, заполните все поля.")
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Можно добавить в контекст, например, список услуг или акции
        return context


class AboutView(TemplateView):
    template_name = "restaurant/about.html"



class BookingView(TemplateView):
    template_name = "restaurant/booking.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tables'] = Table.objects.filter(is_active=True)

        # --- Установка начальных значений для формы ---
        now = datetime.now()
        rounded_hour = now.hour
        rounded_minute = 30 if now.minute >= 30 else 0

        if rounded_minute == 60:
            rounded_minute = 0
            rounded_hour += 1
            if rounded_hour > 23:
                rounded_hour = 23
                rounded_minute = 59

        rounded_time = time(
            hour=rounded_hour,
            minute=rounded_minute
        )

        initial_data = {
            'reservation_date': date.today(),
            'reservation_time': rounded_time,
        }
        # --- КОНЕЦ установки начальных значений ---

        context['form'] = BookingForm(initial=initial_data)
        return context

    def post(self, request, *args, **kwargs):
        form = BookingForm(request.POST)
        if form.is_valid():
            reservation_date = form.cleaned_data['reservation_date']
            reservation_time = form.cleaned_data['reservation_time']
            reservation_period = form.cleaned_data['reservation_period']
            selected_tables = form.cleaned_data['tables'] # <-- ВАЖНО: получаем из формы

            # --- Проверка доступности ---
            # Преобразуем period в timedelta, если он строка (например, "02:00:00")
            if isinstance(reservation_period, str):
                 h, m, s = map(int, reservation_period.split(':'))
                 reservation_period = timedelta(hours=h, minutes=m, seconds=s)

            reservation_start_datetime = datetime.combine(reservation_date, reservation_time)
            reservation_end_datetime = reservation_start_datetime + reservation_period

            # Найдем существующие бронирования, пересекающиеся по времени с выбранными столами
            conflicting_reservations = TableReservation.objects.filter(
                reservation_date=reservation_date,
                tables__in=selected_tables
            ).filter(
                Q(reservation_time__lt=reservation_end_datetime.time(), reservation_time__gte=reservation_start_datetime.time()) |
                Q(reservation_time__lt=reservation_start_datetime.time(), reservation_time__gte=(reservation_start_datetime - reservation_period).time())
            )

            if conflicting_reservations.exists():
                messages.error(request, "Некоторые из выбранных вами столов уже забронированы на это время.")
                context = self.get_context_data()
                context['form'] = form
                return self.render_to_response(context)
            # --- Конец проверки доступности ---

            # Создаем объект, но не сохраняем в БД (commit=False)
            reservation = form.save(commit=False)
            reservation.user = request.user if request.user.is_authenticated else None

            # --- ГАРАНТИРУЕМ, что total_amount не None перед первым save() ---
            # Устанавливаем временное значение 0, чтобы пройти NOT NULL
            reservation.total_amount = 0
            # ---

            reservation.save() # <-- Сохраняем основной объект, получаем ID, total_amount = 0

            # Устанавливаем связи ManyToMany (таблицы)
            reservation.tables.set(selected_tables)

            # --- ВРУЧНУЮ вычисляем и устанавливаем total_amount ---
            # Используем selected_tables, чтобы избежать проблем с кэшем ManyToMany
            total = sum(table.price for table in selected_tables)
            reservation.total_amount = total # <-- Устанавливаем правильную сумму
            # ---

            # СОХРАНЯЕМ объект снова, чтобы обновить total_amount
            reservation.save()

            messages.success(request, "Ваше бронирование успешно оформлено!")
            return redirect('restaurant:booking_success', pk=reservation.pk)
        else:
            messages.error(request, "Ошибка при заполнении формы. Проверьте введённые данные.")

        # При ошибке валидации передаем ту же форму с ошибками
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)







# --- Представления для аутентифицированных пользователей ---

class BookingSuccessView(DetailView):
    model = TableReservation
    template_name = "restaurant/booking_success.html"
    context_object_name = "reservation"

    def get_queryset(self):
        # Пользователь может видеть только свои бронирования
        if self.request.user.is_authenticated:
            return TableReservation.objects.filter(user=self.request.user)
        else:
            # Если пользователь не аутентифицирован, возвращаем пустой QuerySet
            return TableReservation.objects.none()


class ProfileView(LoginRequiredMixin, ListView):
    model = TableReservation
    template_name = "restaurant/profile.html" # Этот шаблон в приложении restaurant
    context_object_name = "reservations"
    paginate_by = 10

    def get_queryset(self):
        return TableReservation.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


# --- Вспомогательные функции и представления ---

@login_required
def cancel_reservation(request, pk):
    # Получаем бронь, принадлежащую текущему пользователю
    reservation = get_object_or_404(TableReservation, pk=pk, user=request.user)
    if request.method == "POST":
        reservation.delete()
        messages.success(request, "Бронирование успешно отменено.")
        return redirect('users:profile') # Редиректим в профиль restaurant
    # Для GET запроса показываем страницу подтверждения
    return render(request, 'restaurant/cancel_reservation.html', {'reservation': reservation})


def check_availability(request):
    date = request.GET.get('date')
    time_str = request.GET.get('time')

    if date and time_str:
        try:
            reservation_date = datetime.strptime(date, '%Y-%m-%d').date()
            reservation_time = datetime.strptime(time_str, '%H:%M').time()
            reservation_period = timedelta(hours=2) # Пример: стандартная продолжительность 2 часа
            reservation_start_datetime = datetime.combine(reservation_date, reservation_time)
            reservation_end_datetime = reservation_start_datetime + reservation_period

            # Найдем все активные столы
            all_active_tables = Table.objects.filter(is_active=True)
            # Найдем забронированные столы на это время
            booked_table_ids = TableReservation.objects.filter(
                reservation_date=reservation_date,
                reservation_time__lt=reservation_end_datetime.time(),
                reservation_time__gte=reservation_start_datetime.time()
            ).values_list('tables__id', flat=True)

            # Доступные столы - это активные минус забронированные
            available_table_ids = list(all_active_tables.exclude(id__in=booked_table_ids).values_list('id', flat=True))

            return JsonResponse({'available_table_ids': available_table_ids})
        except ValueError:
            pass # Игнорируем ошибки формата даты/времени

    # Если что-то пошло не так, возвращаем пустой список
    return JsonResponse({'available_table_ids': []})




