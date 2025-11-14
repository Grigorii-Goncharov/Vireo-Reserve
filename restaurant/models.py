# restaurant/models.py

from django.db import models
from django.contrib.auth.models import User
from config import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class Table(models.Model):
    '''Модель карты столиков'''
    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveSmallIntegerField(help_text="Количество мест за столом")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Стол #{self.number} (на {self.capacity})"

    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"


class TableReservation(models.Model):

    STATUS = [
        ("pending", "Ожидание"),
        ("confirmed", "Подтверждено"),
        ("canceled", "Отменено"),
    ]

    '''Модель заказа столика'''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Клиент",
        null=True, blank=True  # Для анонимных бронирований
    )
    tables = models.ManyToManyField(Table, verbose_name="Столики")

    reservation_date = models.DateField(verbose_name="Дата бронирования")
    reservation_time = models.TimeField(verbose_name="Время бронирования")
    reservation_duration_hours = models.PositiveSmallIntegerField(
        verbose_name="Продолжительность бронирования (часы)",
        validators=[MinValueValidator(1), MaxValueValidator(8)],  # Ограничение от 1 до 8 часов
        help_text="Введите продолжительность бронирования в часах (от 1 до 8)"
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма",
        editable=False  # будет считаться автоматически вручную в views.py
    )
    screenshot = models.ImageField(
        upload_to='reservation/screenshots/',
        blank=True,
        null=True,
        verbose_name="Скриншот карты зала"
    )

    status = models.CharField(max_length=20, choices=STATUS, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def __str__(self):
        return f"Бронь {self.user.first_name if self.user else 'Аноним'} на {self.reservation_date} в {self.reservation_time}"

    # --- ЗАМЕНИТЬ метод save на ЭТОТ ---
    def save(self, *args, **kwargs):
        # Вызываем родительский save без дополнительной логики при создании
        # Вычисление total_amount происходит вручную в views.py
        super().save(*args, **kwargs)


class Feedback(models.Model):
    email = models.EmailField(verbose_name="Email", help_text="Электронная почта клиента")
    message = models.TextField(verbose_name="Сообщение", help_text="Отзыв клиента")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    class Meta:
        verbose_name = "Обратная связь"
        verbose_name_plural = "Обратная связь"

    def __str__(self):
        return f"Сообщение от {self.email}"