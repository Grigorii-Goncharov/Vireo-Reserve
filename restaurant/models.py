from django.db import models
from django.contrib.auth.models import User  # или твоя кастомная модель
from config import settings
from django.core.exceptions import ValidationError


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
    '''Модель заказа столика'''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Клиент"
    )
    tables = models.ManyToManyField(Table, verbose_name="Столики")

    reservation_date = models.DateField(verbose_name="Дата бронирования")
    reservation_time = models.TimeField(verbose_name="Время бронирования")
    reservation_period = models.DurationField(verbose_name="Длительность бронирования")

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма",
        editable=False  # будет считаться автоматически
    )
    screenshot = models.ImageField(
        upload_to='reservation/screenshots/',  # Убрана лишняя 'media/'
        blank=True,
        null=True,
        verbose_name="Скриншот карты зала"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def __str__(self):
        return f"Бронь {self.user.first_name} на {self.reservation_date} в {self.reservation_time}"

    def save(self, *args, **kwargs):
        # Обновляем total_amount только при обновлении (если объект уже сохранён)
        if self.pk:
            total = sum(table.price for table in self.tables.all())
            self.total_amount = total
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