from django.test import TestCase, Client
from django.urls import reverse
from datetime import date
from decimal import Decimal
from django.utils import timezone
from .models import Budget, Month, Expense, ExpenseItem, Payee, PaymentMethod


class PaymentRedirectTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create budget
        self.budget = Budget.objects.create(
            name="Test Budget",
            start_date=date.today(),
            initial_amount=Decimal("1000.00"),
        )

        # Create month
        self.month = Month.objects.create(
            budget=self.budget, year=date.today().year, month=date.today().month
        )

        # Create payee
        self.payee = Payee.objects.create(name="Test Payee")

        # Create payment method
        self.payment_method = PaymentMethod.objects.create(name="Cash")

        # Create expense
        self.expense = Expense.objects.create(
            budget=self.budget,
            title="Test Expense",
            payee=self.payee,
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal("100.00"),
            start_date=date.today(),
            day_of_month=date.today().day,
        )

        # Create unpaid expense item
        self.expense_item = ExpenseItem.objects.create(
            expense=self.expense,
            month=self.month,
            amount=Decimal("100.00"),
            due_date=date.today(),
            status="pending",
        )

    def test_payment_redirects_to_dashboard(self):
        """Test that recording payment redirects to budget dashboard"""
        url = reverse(
            "expense_item_pay",
            kwargs={"budget_id": self.budget.id, "pk": self.expense_item.pk},
        )

        post_data = {
            "status": "paid",
            "payment_date": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "payment_method": self.payment_method.id,
        }

        response = self.client.post(url, post_data)

        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        expected_url = reverse("dashboard", kwargs={"budget_id": self.budget.id})
        self.assertRedirects(response, expected_url)

    def test_unpayment_redirects_to_dashboard(self):
        """Test that unmarking payment redirects to budget dashboard"""
        # First mark the item as paid
        self.expense_item.status = "paid"
        self.expense_item.payment_date = timezone.now()
        self.expense_item.payment_method = self.payment_method
        self.expense_item.save()

        url = reverse(
            "expense_item_unpay",
            kwargs={"budget_id": self.budget.id, "pk": self.expense_item.pk},
        )

        response = self.client.post(url)

        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        expected_url = reverse("dashboard", kwargs={"budget_id": self.budget.id})
        self.assertRedirects(response, expected_url)
