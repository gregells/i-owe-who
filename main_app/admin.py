from django.contrib import admin
from .models import Ledger, Expense

# Register your models here.
admin.site.register(Ledger)
admin.site.register(Expense)