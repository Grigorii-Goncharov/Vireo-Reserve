from datetime import date, time

from django import forms

from .models import Table, TableReservation


class BookingForm(forms.ModelForm):
    """
    Форма для бронирования столиков в ресторане.
    Включает поля для выбора даты, времени, продолжительности и столиков.
    Проверяет, что время бронирования соответствует режиму работы ресторана.
    """

    tables = forms.ModelMultipleChoiceField(
        queryset=Table.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        label="Выберите столики",
        required=True,
    )

    class Meta:
        model = TableReservation
        fields = [
            "reservation_date",
            "reservation_time",
            "reservation_duration_hours",
            "tables",
        ]
        widgets = {
            "reservation_date": forms.DateInput(
                attrs={"type": "date", "min": date.today().isoformat()}
            ),
            "reservation_time": forms.TimeInput(attrs={"type": "time"}),
            "reservation_duration_hours": forms.NumberInput(
                attrs={"type": "number", "min": "1", "max": "8"}
            ),
        }

    def __init__(self, *args, **kwargs):
        """
        Инициализирует форму, устанавливая значения по умолчанию
        для даты (сегодня) и времени (18:00).
        """
        initial = kwargs.get("initial", {})

        if "reservation_date" not in initial:
            initial["reservation_date"] = date.today()
        if "reservation_time" not in initial:
            initial["reservation_time"] = time(18, 0)  # Всегда 18:00 по умолчанию

        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

        self.fields["reservation_duration_hours"].label = (
            "Продолжительность бронирования (часы)"
        )

    def clean(self):
        """
        Дополнительная валидация формы.
        Проверяет, чтобы время окончания бронирования
        не выходило за рамки рабочего времени ресторана (18:00 - 02:00).
        """
        cleaned_data = super().clean()
        reservation_time = cleaned_data.get("reservation_time")
        reservation_duration_hours = cleaned_data.get("reservation_duration_hours")

        if reservation_time and reservation_duration_hours is not None:
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
                raise forms.ValidationError(
                    "Время бронирования выходит за рамки работы ресторана (18:00 – 02:00)."
                )

        return cleaned_data
