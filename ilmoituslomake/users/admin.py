from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User
from django.utils.translation import gettext, gettext_lazy as _

class UserAdminConfig(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_translator")

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_translator', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
admin.site.register(User, UserAdminConfig)
