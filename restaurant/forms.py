# restaurant/forms.py

from django import forms
from .models import TableReservation, Table
from datetime import datetime, date, time

class BookingForm(forms.ModelForm):
    tables = forms.ModelMultipleChoiceField(
        queryset=Table.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        label="Выберите столики",
        required=True
    )

    class Meta:
        model = TableReservation
        fields = ['reservation_date', 'reservation_time', 'reservation_duration_hours', 'tables']
        widgets = {
            'reservation_date': forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}),
            'reservation_time': forms.TimeInput(attrs={'type': 'time'}),
            # Убираем TimeInput для duration_hours, используем NumberInput
            'reservation_duration_hours': forms.NumberInput(attrs={'type': 'number', 'min': '1', 'max': '8'}),
        }

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})

        if 'reservation_date' not in initial:
            initial['reservation_date'] = date.today()
        if 'reservation_time' not in initial:
            now = datetime.now()
            rounded_time = time(
                hour=now.hour + (1 if now.minute >= 30 else 0),
                minute=30 if now.minute < 30 else 0
            )
            if rounded_time.hour > 23:
                rounded_time = time(23, 59)
            elif rounded_time.minute == 60:
                 rounded_time = time(
                     hour=rounded_time.hour + 1,
                     minute=0
                 )
                 if rounded_time.hour > 23:
                     rounded_time = time(23, 59)

            initial['reservation_time'] = rounded_time

        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

        # Устанавливаем лейбл для нового поля
        self.fields['reservation_duration_hours'].label = "Продолжительность бронирования (часы)"