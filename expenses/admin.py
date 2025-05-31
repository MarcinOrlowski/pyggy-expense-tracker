from django.contrib import admin
from .models import Payee, PaymentMethod, Month, Expense, ExpenseItem


@admin.register(Payee)
class PayeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Month)
class MonthAdmin(admin.ModelAdmin):
    list_display = ['year', 'month', 'created_at']
    list_filter = ['year', 'month']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'payee', 'expense_type', 'total_amount', 'started_at', 'closed_at']
    list_filter = ['expense_type', 'closed_at', 'payee']
    search_fields = ['title', 'payee__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'started_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payee')


@admin.register(ExpenseItem)
class ExpenseItemAdmin(admin.ModelAdmin):
    list_display = ['expense', 'month', 'due_date', 'amount', 'status', 'payment_date', 'payment_method']
    list_filter = ['status', 'month', 'expense__expense_type', 'payment_method']
    search_fields = ['expense__title', 'expense__payee__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'due_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('expense', 'expense__payee', 'month', 'payment_method')
