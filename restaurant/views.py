# restaurant/views.py
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    TemplateView, DetailView, ListView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import timedelta, date
from django.db.models import ExpressionWrapper
from django.db.models.functions import Cast
from django.db import models as django_models
from .models import Table, TableReservation, Feedback
from .forms import BookingForm
from datetime import datetime, time


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


class BookingView(LoginRequiredMixin, TemplateView):
    template_name = "restaurant/booking.html"
    # перевести на авторизацию благодаря LoginRequiredMixin
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tables'] = Table.objects.filter(is_active=True)

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

        context['form'] = BookingForm(initial=initial_data)

        # Добавляем список забронированных столов на сегодня
        today = date.today()
        reserved_table_ids = TableReservation.objects.filter(
            reservation_date=today,
            status__in=['pending', 'confirmed']  # Не включаем отменённые
        ).values_list('tables__id', flat=True)

        context['reserved_tables_today'] = Table.objects.filter(
            id__in=reserved_table_ids
        ).order_by('number')

        return context

    def post(self, request, *args, **kwargs):
        form = BookingForm(request.POST)
        if form.is_valid():
            reservation_date = form.cleaned_data['reservation_date']
            reservation_time = form.cleaned_data['reservation_time']
            reservation_duration_hours = form.cleaned_data['reservation_duration_hours']
            selected_tables = form.cleaned_data['tables']

            # --- Проверка ограничений времени работы ресторана ---
            start_time = reservation_time
            # Рассчитываем эффективное время окончания бронирования
            # Если start_time.hour + duration_hours > 24, то время переносится на следующий день
            effective_end_hour = start_time.hour + reservation_duration_hours
            effective_end_minute = start_time.minute

            # Проверяем, не выходит ли время за рамки работы ресторана
            is_valid_time = False
            if start_time >= time(18, 0):  # Начинается с 18:00
                if effective_end_hour <= 26:  # 18 + 8 = 26 (02:00 следующего дня)
                    is_valid_time = True
            elif start_time < time(2, 0):  # Начинается в начале следующего дня
                if reservation_duration_hours <= (2 - start_time.hour):
                    is_valid_time = True

            if not is_valid_time:
                messages.error(request, "Продолжительность бронирования выходит за рамки работы ресторана.")
                context = self.get_context_data()
                context['form'] = form
                return self.render_to_response(context)

            # --- Проверка доступности ---
            reservation_start_datetime = datetime.combine(reservation_date, reservation_time)
            # Используем timedelta для вычисления окончания
            reservation_end_datetime = reservation_start_datetime + timedelta(hours=reservation_duration_hours)

            # Найдем существующие бронирования, пересекающиеся по времени с выбранными столами
            conflicting_reservations = TableReservation.objects.filter(
                reservation_date=reservation_date,
                tables__in=selected_tables
            ).filter(
                # Пересечение интервалов: (start1 < end2) AND (start2 < end1)
                reservation_time__lt=reservation_end_datetime.time(),
                # Для вычисления окончания существующего бронирования используем F выражение
                # (reservation_time + timedelta(hours=reservation_duration_hours)) > start_time
                # Это сложнее сделать через ORM, поэтому используем более простой способ:
                # Ищем брони, у которых время начала < нового_окончания И (время_начала + длительность) > нового_начала
                # Это можно выразить как:
                # reservation_time < end_new_time AND (reservation_time + duration) > start_new_time
                # Выражение (reservation_time + duration) > start_new_time не поддерживается напрямую через F
                # Поэтому используем аннотацию для вычисления времени окончания в запросе
            ).annotate(
                existing_end_time=ExpressionWrapper(
                    Cast(django_models.F('reservation_time'), output_field=django_models.TimeField()) +
                    timedelta(hours=1) * django_models.F('reservation_duration_hours'),
                    output_field=django_models.TimeField()
                )
            ).filter(
                # Теперь можем использовать аннотированное поле
                existing_end_time__gt=reservation_start_datetime.time()
            )

            if conflicting_reservations.exists():
                messages.error(request, "Некоторые из выбранных вами столов уже забронированы на это время.")
                context = self.get_context_data()
                context['form'] = form
                return self.render_to_response(context)

            # --- Конец проверки доступности ---

            reservation = form.save(commit=False)
            reservation.user = request.user if request.user.is_authenticated else None
            # Устанавливаем total_amount в 0, так как цена за стол убрана
            reservation.total_amount = 0
            reservation.save()
            reservation.tables.set(selected_tables)

            # total_amount больше не рассчитывается, так как цена за стол убрана
            # total = sum(table.price for table in selected_tables) * reservation_duration_hours # Цена за стол * часы
            # reservation.total_amount = total
            reservation.save()

            messages.success(request, "Ваше бронирование успешно оформлено!")
            return redirect('restaurant:booking_success', pk=reservation.pk)
        else:
            messages.error(request, "Ошибка при заполнении формы. Проверьте введённые данные.")

        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


# --- Представления для аутентифицированных пользователей ---

class BookingSuccessView(DetailView):
    model = TableReservation
    template_name = "restaurant/booking_success.html"
    context_object_name = "reservation"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return TableReservation.objects.filter(user=self.request.user)
        else:
            return TableReservation.objects.none()


class ProfileView(LoginRequiredMixin, ListView):
    model = TableReservation
    template_name = "users/profile.html"
    context_object_name = "reservations"
    paginate_by = 10

    def get_queryset(self):
        return TableReservation.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


# КОД С УДАЛЕНИЕМ БРОНИ
# @login_required
# def cancel_reservation(request, pk):
#     reservation = get_object_or_404(TableReservation, pk=pk, user=request.user)
#     if request.method == "POST":
#         # Устанавливаем статус на 'canceled' перед удалением
#         reservation.status = 'canceled'
#         reservation.save() # Сохраняем изменения статуса
#         reservation.delete() # Удаляем бронь
#         messages.success(request, "Бронирование успешно отменено.")
#         return redirect('restaurant:profile')
#     # Для GET запроса показываем страницу подтверждения (если таковая есть)
#     # Если подтверждения нет, можно сразу вернуть 405 Method Not Allowed или redirect
#     # Ниже код для страницы подтверждения
#     return render(request, 'restaurant/cancel_reservation.html', {'reservation': reservation})

# КОД С ОТМЕНОЙ, НО НЕ УДАЛЕНИЕМ
@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(TableReservation, pk=pk, user=request.user)
    if request.method == "POST":
        reservation.status = 'canceled'
        reservation.save()
        messages.success(request, "Бронирование успешно отменено.")
        return redirect('restaurant:profile')
    # Для GET запроса показываем страницу подтверждения (если таковая есть)
    # Ниже код для страницы подтверждения
    return render(request, 'restaurant/cancel_reservation.html', {'reservation': reservation})


def check_availability(request):
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')
    duration_str = request.GET.get('duration')

    if date_str and time_str and duration_str:
        try:
            reservation_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            reservation_time = datetime.strptime(time_str, '%H:%M').time()
            reservation_duration_hours = int(duration_str)
            reservation_start_datetime = datetime.combine(reservation_date, reservation_time)
            reservation_end_datetime = reservation_start_datetime + timedelta(hours=reservation_duration_hours)

            # Проверка ограничений времени работы ресторана
            start_time = reservation_time
            effective_end_hour = start_time.hour + reservation_duration_hours
            is_valid_time = False

            if start_time >= time(18, 0):
                if effective_end_hour <= 26:  # 18 + 8 = 26 (02:00)
                    is_valid_time = True
            elif start_time < time(2, 0):
                if reservation_duration_hours <= (2 - start_time.hour):
                    is_valid_time = True

            if not is_valid_time:
                return JsonResponse({'available_table_ids': []})

            all_active_tables = Table.objects.filter(is_active=True)

            # Проверяем пересечения
            # Используем аннотацию для вычисления времени окончания в существующих бронированиях
            conflicting_reservations = TableReservation.objects.filter(
                reservation_date=reservation_date
            ).annotate(
                existing_end_time=ExpressionWrapper(
                    Cast(django_models.F('reservation_time'), output_field=django_models.TimeField()) +
                    timedelta(hours=1) * django_models.F('reservation_duration_hours'),
                    output_field=django_models.TimeField()
                )
            ).filter(
                reservation_time__lt=reservation_end_datetime.time(),
                existing_end_time__gt=reservation_start_datetime.time()
            )

            booked_table_ids = conflicting_reservations.values_list('tables__id', flat=True)

            available_table_ids = list(all_active_tables.exclude(id__in=booked_table_ids).values_list('id', flat=True))
            return JsonResponse({'available_table_ids': available_table_ids})
        except (ValueError, TypeError):
            pass

    return JsonResponse({'available_table_ids': []})


@login_required
def edit_reservation(request, pk):
    reservation = get_object_or_404(TableReservation, pk=pk, user=request.user)

    if request.method == 'POST':
        # Получаем данные из формы
        reservation_date = request.POST.get('reservation_date')
        reservation_time = request.POST.get('reservation_time')
        reservation_duration_hours = request.POST.get('reservation_duration_hours')
        selected_table_ids = request.POST.getlist('tables')

        try:
            reservation_date = datetime.strptime(reservation_date, '%Y-%m-%d').date()
            reservation_time = datetime.strptime(reservation_time, '%H:%M').time()
            reservation_duration_hours = int(reservation_duration_hours)
        except (ValueError, TypeError):
            messages.error(request, "Некорректные данные в форме.")
            return redirect('restaurant:edit_reservation', pk=pk)

        # Проверка ограничений времени работы ресторана (аналогично в BookingView)
        start_time = reservation_time
        effective_end_hour = start_time.hour + reservation_duration_hours
        is_valid_time = False

        if start_time >= time(18, 0):
            if effective_end_hour <= 26:
                is_valid_time = True
        elif start_time < time(2, 0):
            if reservation_duration_hours <= (2 - start_time.hour):
                is_valid_time = True

        if not is_valid_time:
            messages.error(request, "Продолжительность бронирования выходит за рамки работы ресторана.")
            return redirect('restaurant:edit_reservation', pk=pk)

        # Проверка доступности (аналогично в BookingView)
        reservation_start_datetime = datetime.combine(reservation_date, reservation_time)
        reservation_end_datetime = reservation_start_datetime + timedelta(hours=reservation_duration_hours)

        conflicting_reservations = TableReservation.objects.filter(
            reservation_date=reservation_date,
            tables__in=selected_table_ids
        ).exclude(pk=reservation.pk).filter(  # Исключаем текущую бронь из проверки
            reservation_time__lt=reservation_end_datetime.time(),
            # Используем аннотацию или более простой способ для проверки окончания
            # Упрощаем проверку: ищем пересечения по времени
            # (нов_старт < ст_окончание) AND (ст_старт < нов_окончание)
            # reservation_time < end_new_time AND (reservation_time + duration) > start_new_time
            # Это сложно через ORM, поэтому используем аннотацию или предварительный расчет
        ).annotate(
            existing_end_time=ExpressionWrapper(
                Cast(django_models.F('reservation_time'), output_field=django_models.TimeField()) +
                timedelta(hours=1) * django_models.F('reservation_duration_hours'),
                output_field=django_models.TimeField()
            )
        ).filter(
            existing_end_time__gt=reservation_start_datetime.time()
        )

        if conflicting_reservations.exists():
            messages.error(request, "Некоторые из выбранных вами столов уже забронированы на это время.")
            return redirect('restaurant:edit_reservation', pk=pk)

        # Обновляем бронь
        reservation.reservation_date = reservation_date
        reservation.reservation_time = reservation_time
        reservation.reservation_duration_hours = reservation_duration_hours
        reservation.tables.set(selected_table_ids)

        reservation.save()
        messages.success(request, "Бронирование успешно обновлено!")
        return redirect('restaurant:profile')

    else:  # GET запрос
        # Передаем текущие данные в шаблон редактирования
        context = {
            'reservation': reservation,
            'tables': Table.objects.filter(is_active=True),
        }
        return render(request, 'restaurant/edit_reservation.html', context)