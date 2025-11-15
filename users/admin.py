from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "get_full_name",  # <-- Используем кастомный метод для отображения полного имени
        "phone",
        "email",
        "city",
        "is_active",
        "is_staff",
        "is_superuser",
        "photo",
    )
    search_fields = (
        "get_full_name",
        "phone",
        "email",
        "city",
    )

    # Кастомный метод для отображения полного имени
    def get_full_name(self, obj):
        # Используем встроенный метод get_full_name из модели AbstractUser
        # или создаем свой формат
        full_name = obj.get_full_name()
        # Если get_full_name() возвращает пустую строку (например, если first_name и last_name не заполнены),
        # можно вернуть, например, email или username
        return full_name if full_name else obj.email or obj.username

    # Заголовок колонки
    get_full_name.short_description = "Полное имя"
