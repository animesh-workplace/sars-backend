from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class AccountAdmin(UserAdmin):
	list_display = ('id', 'username', 'email', 'is_active')
	fieldsets = (
        *UserAdmin.fieldsets,
        (
            'User defined fields',
            {
                'fields': (
                    'city',
                    'state',
                    'export',
                    'address',
                    'pin_code',
                    'download',
                    'institute',
                ),
            },
        ),
    )

admin.site.register(Accounts, AccountAdmin)
