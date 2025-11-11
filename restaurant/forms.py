from django import forms
from .models import TableReservation, Table
from datetime import datetime, date, time

class BookingForm(forms.ModelForm):
    tables = forms.ModelMultipleChoiceField(
        queryset=Table.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        label="Выберите столики",
        required=True # Убедимся, что поле обязательно
    )

    class Meta:
        model = TableReservation
        fields = ['reservation_date', 'reservation_time', 'reservation_period', 'tables']
        widgets = {
            'reservation_date': forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}), # Ограничиваем минимальную дату
            'reservation_time': forms.TimeInput(attrs={'type': 'time'}),
            'reservation_period': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        # Получаем initial из kwargs
        initial = kwargs.get('initial', {})

        # Если initial не содержит reservation_date и reservation_time, устанавливаем текущие
        if 'reservation_date' not in initial:
            initial['reservation_date'] = date.today()
        if 'reservation_time' not in initial:
            # Берем текущее время и округляем вверх до ближайшего получаса (например, 14:30, 15:00)
            now = datetime.now()
            # Округление вверх до следующего получаса/часа для простоты
            # Можно настроить по-другому, если нужно
            rounded_time = time(
                hour=now.hour + (1 if now.minute >= 30 else 0),
                minute=30 if now.minute < 30 else 0
            )
            # Если получилось больше 23:59, перейдем к следующему часу и 00 минут
            if rounded_time.hour > 23:
                # В этом случае, возможно, стоит установить на 00:00 следующего дня
                # Но для простоты оставим 23:59, или просто следующий час до 23
                rounded_time = time(23, 59)
            elif rounded_time.minute == 60:
                 rounded_time = time(
                     hour=rounded_time.hour + 1,
                     minute=0
                 )
                 if rounded_time.hour > 23:
                     rounded_time = time(23, 59) # или обработка на следующий день

            initial['reservation_time'] = rounded_time

        # Обновляем kwargs с новым initial
        kwargs['initial'] = initial
        # Вызываем родительский __init__
        super().__init__(*args, **kwargs)
