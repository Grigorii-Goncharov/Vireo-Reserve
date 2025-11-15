from datetime import date, datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models as django_models
from django.db.models import ExpressionWrapper
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, TemplateView

from .forms import BookingForm
from .models import Feedback, Table, TableReservation


class HomeView(TemplateView):
    template_name = "restaurant/home.html"

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        message = request.POST.get("message")
        if email and message:
            Feedback.objects.create(email=email, message=message)
            messages.success(
                request, "Ваше сообщение успешно отправлено! Спасибо за обратную связь."
            )
            return redirect("restaurant:home")
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
    login_url = "users:login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tables"] = Table.objects.filter(is_active=True)

        # Создаём форму с начальными значениями — они уже заданы в BookingForm
        context["form"] = BookingForm()

        # --- НОВОЕ: Получаем забронированные столы и временные интервалы ---
        today = date.today()
        reservations_today = TableReservation.objects.filter(
            reservation_date=today,
            status__in=["pending", "confirmed"],
        ).select_related().prefetch_related('tables')

        # Собираем информацию о забронированных столах и интервалах
        reserved_tables_with_intervals = []
        for res in reservations_today:
            for table in res.tables.all():
                start_time = res.reservation_time
                duration_hours = res.reservation_duration_hours
                end_time = datetime.combine(today, start_time) + timedelta(hours=duration_hours)
                reserved_tables_with_intervals.append({
                    'table': table,
                    'start_time': start_time,
                    'end_time': end_time.time(),
                    'reservation_id': res.id,
                })

        context["reserved_tables_with_intervals"] = reserved_tables_with_intervals

        return context

    def post(self, request, *args, **kwargs):
        form = BookingForm(request.POST)
        if form.is_valid():
            reservation_date = form.cleaned_data["reservation_date"]
            reservation_time = form.cleaned_data["reservation_time"]
            reservation_duration_hours = form.cleaned_data["reservation_duration_hours"]
            selected_tables = form.cleaned_data["tables"]

            # --- Проверка ограничений времени работы ресторана ---
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
                messages.error(
                    request,
                    "Продолжительность бронирования выходит за рамки работы ресторана.",
                )
                context = self.get_context_data()
                context["form"] = form
                return self.render_to_response(context)

            # --- Проверка доступности ---
            reservation_start_datetime = datetime.combine(
                reservation_date, reservation_time
            )
            reservation_end_datetime = reservation_start_datetime + timedelta(
                hours=reservation_duration_hours
            )

            conflicting_reservations = (
                TableReservation.objects.filter(
                    reservation_date=reservation_date, tables__in=selected_tables
                )
                .filter(
                    reservation_time__lt=reservation_end_datetime.time(),
                )
                .annotate(
                    existing_end_time=ExpressionWrapper(
                        Cast(
                            django_models.F("reservation_time"),
                            output_field=django_models.TimeField(),
                        )
                        + timedelta(hours=1)
                        * django_models.F("reservation_duration_hours"),
                        output_field=django_models.TimeField(),
                    )
                )
                .filter(existing_end_time__gt=reservation_start_datetime.time())
            )

            if conflicting_reservations.exists():
                messages.error(
                    request,
                    "Некоторые из выбранных вами столов уже забронированы на это время.",
                )
                context = self.get_context_data()
                context["form"] = form
                return self.render_to_response(context)

            # --- Конец проверки доступности ---

            reservation = form.save(commit=False)
            reservation.user = request.user if request.user.is_authenticated else None
            reservation.total_amount = 0
            reservation.save()
            reservation.tables.set(selected_tables)
            reservation.save()

            messages.success(request, "Ваше бронирование успешно оформлено!")
            return redirect("restaurant:booking_success", pk=reservation.pk)
        else:
            messages.error(
                request, "Ошибка при заполнении формы. Проверьте введённые данные."
            )

        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


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
        return TableReservation.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(TableReservation, pk=pk, user=request.user)
    if request.method == "POST":
        reservation.status = "canceled"
        reservation.save()
        messages.success(request, "Бронирование успешно отменено.")
        return redirect("restaurant:profile")
    return render(
        request, "restaurant/cancel_reservation.html", {"reservation": reservation}
    )


def check_availability(request):
    date_str = request.GET.get("date")
    time_str = request.GET.get("time")
    duration_str = request.GET.get("duration")

    if date_str and time_str and duration_str:
        try:
            reservation_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            reservation_time = datetime.strptime(time_str, "%H:%M").time()
            reservation_duration_hours = int(duration_str)
            reservation_start_datetime = datetime.combine(
                reservation_date, reservation_time
            )
            reservation_end_datetime = reservation_start_datetime + timedelta(
                hours=reservation_duration_hours
            )

            # Проверка ограничений времени работы ресторана
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
                return JsonResponse({"available_table_ids": []})

            all_active_tables = Table.objects.filter(is_active=True)

            conflicting_reservations = (
                TableReservation.objects.filter(reservation_date=reservation_date)
                .annotate(
                    existing_end_time=ExpressionWrapper(
                        Cast(
                            django_models.F("reservation_time"),
                            output_field=django_models.TimeField(),
                        )
                        + timedelta(hours=1)
                        * django_models.F("reservation_duration_hours"),
                        output_field=django_models.TimeField(),
                    )
                )
                .filter(
                    reservation_time__lt=reservation_end_datetime.time(),
                    existing_end_time__gt=reservation_start_datetime.time(),
                )
            )

            booked_table_ids = conflicting_reservations.values_list(
                "tables__id", flat=True
            )

            available_table_ids = list(
                all_active_tables.exclude(id__in=booked_table_ids).values_list(
                    "id", flat=True
                )
            )
            return JsonResponse({"available_table_ids": available_table_ids})
        except (ValueError, TypeError):
            pass

    return JsonResponse({"available_table_ids": []})


@login_required
def edit_reservation(request, pk):
    reservation = get_object_or_404(TableReservation, pk=pk, user=request.user)

    if request.method == "POST":
        reservation_date = request.POST.get("reservation_date")
        reservation_time = request.POST.get("reservation_time")
        reservation_duration_hours = request.POST.get("reservation_duration_hours")
        selected_table_ids = request.POST.getlist("tables")

        try:
            reservation_date = datetime.strptime(reservation_date, "%Y-%m-%d").date()
            reservation_time = datetime.strptime(reservation_time, "%H:%M").time()
            reservation_duration_hours = int(reservation_duration_hours)
        except (ValueError, TypeError):
            messages.error(request, "Некорректные данные в форме.")
            return redirect("restaurant:edit_reservation", pk=pk)

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
            messages.error(
                request,
                "Продолжительность бронирования выходит за рамки работы ресторана.",
            )
            return redirect("restaurant:edit_reservation", pk=pk)

        reservation_start_datetime = datetime.combine(
            reservation_date, reservation_time
        )
        reservation_end_datetime = reservation_start_datetime + timedelta(
            hours=reservation_duration_hours
        )

        conflicting_reservations = (
            TableReservation.objects.filter(
                reservation_date=reservation_date, tables__in=selected_table_ids
            )
            .exclude(pk=reservation.pk)
            .annotate(
                existing_end_time=ExpressionWrapper(
                    Cast(
                        django_models.F("reservation_time"),
                        output_field=django_models.TimeField(),
                    )
                    + timedelta(hours=1)
                    * django_models.F("reservation_duration_hours"),
                    output_field=django_models.TimeField(),
                )
            )
            .filter(existing_end_time__gt=reservation_start_datetime.time())
        )

        if conflicting_reservations.exists():
            messages.error(
                request,
                "Некоторые из выбранных вами столов уже забронированы на это время.",
            )
            return redirect("restaurant:edit_reservation", pk=pk)

        reservation.reservation_date = reservation_date
        reservation.reservation_time = reservation_time
        reservation.reservation_duration_hours = reservation_duration_hours
        reservation.tables.set(selected_table_ids)
        reservation.save()
        messages.success(request, "Бронирование успешно обновлено!")
        return redirect("restaurant:profile")

    else:
        context = {
            "reservation": reservation,
            "tables": Table.objects.filter(is_active=True),
        }
        return render(request, "restaurant/edit_reservation.html", context)