from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    EmailValidator,
    FileExtensionValidator,
    RegexValidator,
)
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):

    first_name = models.CharField(max_length=50, verbose_name="Имя Гостя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия Гостя")
    email = models.EmailField(
        unique=True,
        verbose_name="Электронная почта",
        validators=[EmailValidator()],
    )
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Телефон должен быть в формате: '+999999999'. До 15 цифр.",
            )
        ],
        blank=True,
        null=True,
        verbose_name="Телефон",
    )
    token = models.CharField(
        max_length=120,
        verbose_name="Токен",
        null=True,
        blank=True,
        help_text="Используется для временных операций, например, сброса пароля.",
    )

    photo = models.ImageField(
        upload_to="images/",
        verbose_name="Аватар",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                ["png", "jpg", "jpeg"], "Только изображения формата png, jpg, jpeg"
            )
        ],
    )

    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")

    telegram_chat_id = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Telegram Chat ID"
    )

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")
    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )

    USERNAME_FIELD = "email"  # Используем email для аутентификации
    REQUIRED_FIELDS = (
        []
    )  # Поля, обязательные при создании суперпользователя через createsuperuser (кроме email и пароля)

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
