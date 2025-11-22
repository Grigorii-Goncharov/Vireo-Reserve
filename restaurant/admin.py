# restaurant/admin.py

from django.contrib import admin

from .models import Feedback, Table, TableReservation


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("number", "capacity", "is_active")
    list_filter = ("capacity", "is_active")
    search_fields = ("number",)
    list_editable = ("is_active",)


@admin.register(TableReservation)
class TableReservationAdmin(admin.ModelAdmin):
    list_display = (
        "user",  # Используем стандартное отображение пользователя
        "tables_list",  # Используем кастомный метод для отображения столов
        "reservation_date",
        "reservation_time",
        "reservation_duration_hours",
        "created_at",
        "status",
    )
    list_filter = (
        "reservation_date",
        "tables",
        "status",
    )  # 'tables' можно оставить в фильтрах
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
    )  # Лучше указать конкретные поля
    filter_horizontal = ("tables",)  # удобный виджет для ManyToMany
    readonly_fields = (
        "user",  # Используем стандартное отображение пользователя
        "tables_list",  # Используем кастомный метод для отображения столов
        "reservation_date",
        "reservation_time",
        "reservation_duration_hours",
        "created_at",
        "updated_at",
    )

    # Кастомный метод для отображения списка столов
    def tables_list(self, obj):
        return ", ".join([str(table) for table in obj.tables.all()])

    tables_list.short_description = "Столики"  # Заголовок колонки


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "message",
        "created_at",
    )
    readonly_fields = ("created_at",)
