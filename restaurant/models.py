from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from config import settings


class Table(models.Model):
    """Модель карты столиков"""

    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveSmallIntegerField(help_text="Количество мест за столом")
    is_active = models.BooleanField(default=True)
    photo = models.ImageField(
        upload_to="tables/photos/", blank=True, null=True, verbose_name="Фото стола"
    )

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

    """Модель заказа столика"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Клиент",
        null=True,
        blank=True,  # Для анонимных бронирований
    )
    tables = models.ManyToManyField(Table, verbose_name="Столики")

    reservation_date = models.DateField(verbose_name="Дата бронирования")
    reservation_time = models.TimeField(verbose_name="Время бронирования")
    reservation_duration_hours = models.PositiveSmallIntegerField(
        verbose_name="Продолжительность бронирования (часы)",
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        help_text="Введите продолжительность бронирования в часах (от 1 до 8)",
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма",
        editable=False,  # будет рассчитываться вручную в views.py
    )

    status = models.CharField(max_length=20, choices=STATUS, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def __str__(self):
        return (
            f"Бронь {self.user.first_name if self.user else 'Аноним'} на {self.reservation_date} "
            f"в {self.reservation_time}"
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Feedback(models.Model):
    email = models.EmailField(
        verbose_name="Email", help_text="Электронная почта клиента"
    )
    message = models.TextField(verbose_name="Сообщение", help_text="Отзыв клиента")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    class Meta:
        verbose_name = "Обратная связь"
        verbose_name_plural = "Обратная связь"

    def __str__(self):
        return f"Сообщение от {self.email}"
