from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import User


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["first_name", "last_name", "email", "phone", "telegram_chat_id", "city", "photo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем Bootstrap-классы и плейсхолдеры
        self.fields["first_name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите имя пользователя"}
        )
        self.fields["last_name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите фамилию пользователя"}
        )
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите email"}
        )
        self.fields["phone"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите телефон (только цифры)"}
        )
        self.fields["telegram_chat_id"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите Телеграмм"}
        )
        self.fields["city"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Ваш город"}
        )

        self.fields["photo"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Фото пользователя"}
        )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and not phone.isdigit():
            raise forms.ValidationError("Номер телефона должен содержать только цифры.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError("Введите корректный email-адрес.")

            # Проверка уникальности email
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    "Пользователь с таким email уже существует."
                )
        return email


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "telegram_chat_id", "city", "photo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем Bootstrap-классы и плейсхолдеры
        self.fields["first_name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите имя пользователя"}
        )

        self.fields["last_name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите имя пользователя"}
        )
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите email"}
        )
        self.fields["phone"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите телефон (только цифры)"}
        )

        self.fields["telegram_chat_id"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите telegram_chat_id"}
        )
        self.fields["city"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Ваш город"}
        )
        self.fields["photo"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Загрузите фото"}
        )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and not phone.isdigit():
            raise forms.ValidationError("Номер телефона должен содержать только цифры.")
        return phone

    def clean_email(self):
        """Валидация поля 'email': проверка формата и уникальности (кроме текущего пользователя).
        Returns:
            str: Очищенное значение email.
        Raises:
            ValidationError: Если email некорректен или уже используется другим пользователем.
        """
        email = self.cleaned_data.get("email")
        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError("Введите корректный email-адрес.")

            # Проверка уникальности, исключая текущего пользователя
            if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
                raise forms.ValidationError("Этот email уже используется.")
        return email