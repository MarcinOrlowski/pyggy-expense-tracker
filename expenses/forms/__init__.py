"""Forms package for expense tracking application.

Import all form classes for backward compatibility.
"""

from .expense import ExpenseForm
from .payment import PaymentForm, ExpenseItemEditForm
from .payee import PayeeForm
from .budget import BudgetForm
from .payment_method import PaymentMethodForm
from .quick_expense import QuickExpenseForm

# Make all form classes available when importing from expenses.forms
__all__ = [
    "ExpenseForm",
    "PaymentForm",
    "ExpenseItemEditForm",
    "PayeeForm",
    "BudgetForm",
    "PaymentMethodForm",
    "QuickExpenseForm",
]
