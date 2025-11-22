import uuid

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Пользовательская форма для регистрации нового пользователя.
    Наследуется от UserCreationForm и включает дополнительные поля:
    first_name, last_name, email, phone, telegram_chat_id, city, photo.
    Добавляет валидацию номера телефона и email.
    При сохранении генерирует уникальное имя пользователя (username).
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "telegram_chat_id",
            "city",
            "photo",
        ]

    def __init__(self, *args, **kwargs):
        """
        Инициализирует форму и добавляет атрибуты для стилей (Bootstrap)
        и плейсхолдеры к полям.
        """
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
        """
        Валидация поля 'phone': проверка, что номер содержит только цифры.
        Returns:
            str: Очищенное значение номера телефона.
        Raises:
            ValidationError: Если номер содержит недопустимые символы.
        """
        phone = self.cleaned_data.get("phone")
        if phone and not phone.isdigit():
            raise forms.ValidationError("Номер телефона должен содержать только цифры.")
        return phone

    def clean_email(self):
        """
        Валидация поля 'email': проверка формата и уникальности.
        Returns:
            str: Очищенное значение email.
        Raises:
            ValidationError: Если email некорректен или уже используется.
        """
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

    def save(self, commit=True):
        """Метод сохранения username (если в модели нет поля, то нужно использовать метод для записи
        т.к. AbstractUser всегда должен иметь username)"""
        user = super().save(commit=False)
        # Генерируем уникальный username из email или UUID
        if not user.username:
            user.username = str(uuid.uuid4()).replace("-", "")[:200]

        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """
    Форма для редактирования профиля пользователя.
    Включает поля: first_name, last_name, email, phone, telegram_chat_id, city, photo.
    Добавляет валидацию номера телефона и email, проверяя уникальность email
    для других пользователей, кроме текущего.
    """

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "telegram_chat_id",
            "city",
            "photo",
        ]

    def __init__(self, *args, **kwargs):
        """
        Инициализирует форму и добавляет атрибуты для стилей (Bootstrap)
        и плейсхолдеры к полям.
        """
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
        """
        Валидация поля 'phone': проверка, что номер содержит только цифры.
        Returns:
            str: Очищенное значение номера телефона.
        Raises:
            ValidationError: Если номер содержит недопустимые символы.
        """
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
