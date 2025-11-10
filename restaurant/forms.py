from django import forms
from .models import TableReservation, Table

class BookingForm(forms.ModelForm):
    tables = forms.ModelMultipleChoiceField(
        queryset=Table.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        label="Выберите столики"
    )

    class Meta:
        model = TableReservation
        fields = ['reservation_date', 'reservation_time', 'reservation_period', 'tables']
        widgets = {
            'reservation_date': forms.DateInput(attrs={'type': 'date'}),
            'reservation_time': forms.TimeInput(attrs={'type': 'time'}),
            'reservation_period': forms.TimeInput(attrs={'type': 'time'}),
        }