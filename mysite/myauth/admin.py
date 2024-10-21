from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile, User

# Определяем инлайн-редактор для профиля
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False  # Чтобы нельзя было удалить профиль через админку
    verbose_name_plural = 'Profile'

# Регистрация инлайна в модели пользователя
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

# Перерегистрируем модель пользователя с новым админом
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)