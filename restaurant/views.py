from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.exceptions import ValidationError

from .models import Table, TableReservation, Feedback
from .forms import BookingForm  # Предполагается, что вы создадите BookingForm
from config import settings


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
        # Передаём доступные столы в шаблон
        context['tables'] = Table.objects.filter(is_active=True)
        context['form'] = BookingForm()  # Предполагается, что вы создадите BookingForm
        return context

    def post(self, request, *args, **kwargs):
        form = BookingForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user if request.user.is_authenticated else None
            reservation.save()
            form.save_m2m()  # Сохраняем ManyToMany связи (столики)

            # Пересчитываем сумму
            total = sum(table.price for table in reservation.tables.all())
            reservation.total_amount = total
            reservation.save()

            messages.success(request, "Ваше бронирование успешно оформлено!")
            return redirect('restaurant:booking_success', pk=reservation.pk)
        else:
            messages.error(request, "Ошибка при заполнении формы. Проверьте введённые данные.")

        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class BookingSuccessView(DetailView):
    model = TableReservation
    template_name = "restaurant/booking_success.html"
    context_object_name = "reservation"

    def get_queryset(self):
        return TableReservation.objects.filter(user=self.request.user) \
            if self.request.user.is_authenticated else TableReservation.objects.none()


class ProfileView(LoginRequiredMixin, ListView):
    model = TableReservation
    template_name = "restaurant/profile.html"
    context_object_name = "reservations"
    paginate_by = 10

    def get_queryset(self):
        return TableReservation.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


@login_required
def cancel_reservation(request, pk):
    reservation = TableReservation.objects.get(pk=pk, user=request.user)
    if request.method == "POST":
        reservation.delete()
        messages.success(request, "Бронирование успешно отменено.")
        return redirect('restaurant:profile')
    return render(request, 'restaurant/cancel_reservation.html', {'reservation': reservation})