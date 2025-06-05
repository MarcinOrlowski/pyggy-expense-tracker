# Getting Started with PyGGy

This guide will walk you through setting up PyGGy and completing your first expense tracking
workflow. By the end, you'll understand the basics of budgets, expenses, and payment tracking.

## Prerequisites

Before starting, ensure PyGGy is installed and running. See the main [README.md](../README.md) in
the project root for installation instructions using Docker or manual setup.

## Your First Session: Complete Walkthrough

### Step 1: Access the Application

1. Start PyGGy (using `docker compose up` or `python manage.py runserver`)
2. Open your browser to `http://127.0.0.1:8000/`
3. You'll see the PyGGy dashboard

### Step 2: Create Your First Budget

Budgets organize your expenses into logical groups. You might have separate budgets for personal
expenses, business costs, or household bills.

1. **Navigate to Budgets**: Click "Budgets" in the main navigation
2. **Add New Budget**: Click the "Add Budget" button
3. **Fill in Details**:
  - **Name**: Choose something descriptive like "Personal Expenses" or "Household Bills"
  - **Initial Amount**: Enter your starting budget balance (e.g., 0.00 for new tracking, positive
    for available funds, or negative if starting with a deficit)
  - **Description**: Add optional notes about this budget's purpose
4. **Save**: Click "Save" to create your budget

*Note: The initial amount is your starting budget balance. Use 0.00 if starting fresh, positive
amounts for available funds, or negative amounts if starting with a deficit.*

### Step 3: Set Up Payment Methods

Before adding expenses, set up how you typically pay bills.

1. **Navigate to Payment Methods**: Click "Payment Methods" in the navigation
2. **Add Common Methods**: Create entries like:
  - "Bank Transfer"
  - "Credit Card"
  - "Cash"
  - "Check"
3. **For each method**: Just enter a name and optional description

### Step 4: Add Your First Payee

Payees are who you pay money to - landlords, utility companies, subscription services, etc.

1. **Navigate to Payees**: Click "Payees" in the navigation
2. **Add New Payee**: Click "Add Payee"
3. **Enter Details**:
  - **Name**: Company or person name (e.g., "Electric Company", "Netflix")
  - **Description**: Optional notes about this payee

### Step 5: Create Your First Expense

Now you'll create an expense - this defines what you need to pay regularly.

1. **Navigate to Expenses**: Click "Expenses" in the navigation
2. **Add New Expense**: Click "Add Expense"
3. **Choose Expense Details**:
  - **Budget**: Select the budget you created
  - **Payee**: Select the payee you created
  - **Name**: Descriptive name (e.g., "Monthly Rent", "Netflix Subscription")
  - **Amount**: How much you pay each time
  - **Expense Type**: Choose from:
    - **Endless Recurring**: Bills that continue indefinitely (rent, utilities)
    - **One Time**: Single payments (one-off purchases)
    - **Split Payment**: Fixed installments (loan payments)
    - **Recurring with End**: Limited-time recurring (gym membership with end date)
  - **Start Date**: When this expense begins (defaults to current month)
  - **Day of Month**: Which day of the month it's due (e.g., 1st, 15th)

4. **Save the Expense**

*PyGGy will automatically create an expense item for the current month when you save.*

### Step 6: View Your Dashboard

Return to the dashboard to see your expense tracking in action:

1. **Click "Dashboard"** in the navigation
2. **Review the Month Summary**:
  - Total budgeted amount
  - Total expenses created
  - Amount paid so far
  - Remaining balance
3. **Check Expense Items**: See the monthly instances of your expenses

### Step 7: Record a Payment

When you actually pay a bill, record it in PyGGy:

1. **Find the Expense Item**: On the dashboard, locate the expense item
2. **Click "Pay"**: Click the payment button next to the expense
3. **Enter Payment Details**:
  - **Payment Date**: When you made the payment (defaults to today)
  - **Payment Method**: How you paid (select from your payment methods)
  - **Amount**: Confirm the payment amount
4. **Save**: Record the payment

The expense item will now show as "Paid" and your dashboard totals will update.

## Understanding the Monthly Workflow

PyGGy follows a month-by-month approach:

1. **Current Month**: All your recurring expenses appear as expense items
2. **Pay Bills**: Record payments as you make them throughout the month
3. **Next Month**: PyGGy can create the next month, automatically generating new expense items for
   recurring expenses
4. **Review**: Look back at previous months to analyze spending patterns

## Next Steps

Now that you've completed the basic workflow:

- **Explore [Expense Types](expense_types)** to understand which type fits different bills
- **Learn about [Budget Management](budgets)** for advanced budgeting strategies
- **Understand [Monthly Workflow](monthly_workflow)** for month-to-month operations
- **Read [Payees & Payment Methods](payees_and_payments)** for organization tips

## Common First-Time Tips

- **Start Simple**: Begin with just a few regular expenses to get comfortable
- **Use Descriptive Names**: Clear expense names make tracking easier later
- **Set Realistic Budgets**: Your initial budget amounts can always be adjusted
- **Record Payments Promptly**: Keep your payment tracking current for accurate insights
- **One Budget First**: Start with one budget and add more as needed

## Troubleshooting

- **Can't find an expense?** Check if you're looking at the right budget - expenses are
  budget-specific
- **Missing expense items?** Recurring expenses only create items for the current month initially
- **Want to modify an expense?** You can edit most expense details, but some restrictions apply to
  prevent data inconsistency

---

*Ready to dive deeper? Explore the other documentation topics to master PyGGy's full capabilities.*
