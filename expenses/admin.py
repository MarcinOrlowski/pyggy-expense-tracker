from django.contrib import admin
from .models import Payee, PaymentMethod, Payment, Month, Expense, ExpenseItem, Settings


@admin.register(Payee)
class PayeeAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "expense_item",
        "amount",
        "payment_date",
        "payment_method",
        "transaction_id",
    ]
    list_filter = ["payment_method", "payment_date"]
    search_fields = ["expense_item__expense__title", "transaction_id"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "payment_date"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("expense_item", "expense_item__expense", "payment_method")
        )


@admin.register(Month)
class MonthAdmin(admin.ModelAdmin):
    list_display = ["year", "month", "created_at"]
    list_filter = ["year", "month"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "payee",
        "expense_type",
        "amount",
        "start_date",
        "closed_at",
    ]
    list_filter = ["expense_type", "closed_at", "payee"]
    search_fields = ["title", "payee__name"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "start_date"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("payee")


@admin.register(ExpenseItem)
class ExpenseItemAdmin(admin.ModelAdmin):
    list_display = [
        "expense",
        "month",
        "due_date",
        "amount",
        "status",
    ]
    list_filter = ["month", "expense__expense_type"]
    search_fields = ["expense__title", "expense__payee__name"]
    readonly_fields = ["created_at", "updated_at", "status"]
    date_hierarchy = "due_date"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("expense", "expense__payee", "month")
        )


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ["currency", "locale", "updated_at"]
    fields = ["currency", "locale"]
    readonly_fields = ["created_at", "updated_at"]

    def has_add_permission(self, request):
        # Ensure only one instance
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False
