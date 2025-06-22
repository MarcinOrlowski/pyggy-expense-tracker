"""Views package for expense tracking application.

Import all view functions for backward compatibility.
"""
from .dashboard import dashboard
from .expense import (
    expense_list,
    expense_create,
    expense_detail,
    expense_edit,
    expense_delete,
)
from .month import month_list, month_detail, month_delete, month_process
from .payment import (
    expense_item_pay,
    expense_item_unpay,
    expense_item_edit,
    expense_item_payments,
    expense_item_delete,
)
from .payee import (
    payee_list,
    payee_create,
    payee_edit,
    payee_delete,
    payee_hide,
    payee_unhide,
)
from .payment_method import (
    payment_method_list,
    payment_method_create,
    payment_method_edit,
    payment_method_delete,
)
from .budget import budget_list, budget_create, budget_edit, budget_delete
from .help import help_index, help_page
from .error_handlers import custom_404

# Make all view functions available when importing from expenses.views
__all__ = [
    # Dashboard
    "dashboard",
    # Expense views
    "expense_list",
    "expense_create",
    "expense_detail",
    "expense_edit",
    "expense_delete",
    # Month views
    "month_list",
    "month_detail",
    "month_delete",
    "month_process",
    # Payment views
    "expense_item_pay",
    "expense_item_unpay",
    "expense_item_edit",
    "expense_item_payments",
    "expense_item_delete",
    # Payee views
    "payee_list",
    "payee_create",
    "payee_edit",
    "payee_delete",
    "payee_hide",
    "payee_unhide",
    # Payment method views
    "payment_method_list",
    "payment_method_create",
    "payment_method_edit",
    "payment_method_delete",
    # Budget views
    "budget_list",
    "budget_create",
    "budget_edit",
    "budget_delete",
    # Help views
    "help_index",
    "help_page",
    # Error handlers
    "custom_404",
]
