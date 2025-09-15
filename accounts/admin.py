from django.contrib import admin
from .models import Account
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class AccountsAdmin(UserAdmin):
    list_display = ('email','first_name','last_name','username','last_login','is_active','date_joined')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login','date_joined')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Account,AccountsAdmin)




