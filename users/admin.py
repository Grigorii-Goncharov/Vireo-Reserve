from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name",  "phone", "email" , "city" , "is_active", "is_staff", "photo")
    search_fields = ("first_name", "last_name",  "phone", "email" , "city",)
