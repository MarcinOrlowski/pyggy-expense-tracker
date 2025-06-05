# Monthly Workflow

PyGGy follows a month-by-month workflow that mirrors real-world budgeting and bill paying.
Understanding this workflow is essential for effective expense tracking and financial planning.

## The Monthly Cycle

### 1. Month Creation

PyGGy operates on discrete monthly periods that must be created sequentially:

- Months are created one at a time, in chronological order
- You cannot skip months or create future months out of sequence
- Each month automatically generates expense items for active recurring expenses

### 2. Expense Item Generation

When a month is created, PyGGy automatically:

- Creates expense items for all active recurring expenses
- Calculates due dates based on expense settings
- Applies business rules for expense type behavior
- Updates expense status (open/closed) based on type rules

### 3. Payment Tracking

Throughout the month, you:

- Record payments as bills are actually paid
- Track payment dates and methods
- Monitor spending against budget targets
- Review expense item status

### 4. Month Analysis

At month end, you can:

- Review total spending vs. budget
- Analyze payment patterns
- Identify overdue or unpaid items
- Prepare for next month planning

## Working with Months

### Viewing Months

- **Dashboard**: Shows current month's expense items and totals
- **Months List**: Historical view of all processed months
- **Month Detail**: Detailed view of specific month's activities

### Month Status Indicators

- **Current Month**: The active month for expense tracking
- **Future Months**: Cannot be created out of sequence
- **Past Months**: Historical data, may have restrictions on editing

### Creating the Next Month

1. **Navigate to Months**: Click "Months" in the main navigation
2. **Create Next Month**: Click the "Add Month" or "Process Next Month" button
3. **Automatic Processing**: PyGGy generates expense items for active expenses
4. **Review Results**: Check the new month's generated expense items

## Expense Items: The Monthly Reality

### What Are Expense Items?

Expense items are the monthly instances of your expenses:

- Each recurring expense generates one expense item per month
- Expense items represent actual bills you need to pay
- They track payment status, due dates, and amounts

### Expense Item Lifecycle

1. **Created**: Generated when month is processed
2. **Pending**: Waiting to be paid
3. **Paid**: Payment recorded with date and method
4. **Overdue**: Past due date without payment (visual indicator)

### Expense Item Details

Each expense item shows:

- **Source expense name** and details
- **Due date** (calculated from expense settings)
- **Amount** (from parent expense)
- **Payment status** (paid/unpaid)
- **Payment details** (date, method) if paid
- **Budget assignment** (inherited from expense)

## Payment Recording

### Recording a Payment

1. **Find the Expense Item**: On dashboard or month detail
2. **Click Pay Button**: Start payment recording process
3. **Enter Payment Details**:
  - **Payment Date**: When you actually paid (defaults to today)
  - **Payment Method**: How you paid (select from your methods)
  - **Amount**: Confirm payment amount (usually matches expense)
4. **Save Payment**: Complete the payment record

### Payment Information Tracked

- **Exact payment date** (can be different from due date)
- **Payment method used** (helps track spending by method)
- **Actual amount paid** (may differ from planned amount)
- **Reference to parent expense** (maintains connection)

### Editing Payments

- Payment details can usually be edited after recording
- Changes only affect the specific expense item
- Payment history is maintained for audit purposes

## Monthly Processing Rules

### Recurring Expense Behavior

**Endless Recurring**:

- Creates one expense item every month
- Continues until manually closed
- No automatic stopping condition

**Recurring with End Date**:

- Creates expense items until end date
- Automatically closes after end date
- End date is inclusive (creates item for end month)

**Split Payment**:

- Creates expense items for remaining installments
- Automatically closes after final installment
- Tracks progress toward completion

**One Time**:

- Already closed after initial creation
- No new expense items created

### Business Rule Enforcement

- **Sequential month creation**: Cannot skip months
- **Due date calculation**: Uses expense day-of-month settings
- **Amount inheritance**: Expense items use parent expense amounts
- **Budget assignment**: Inherited from parent expense

## Advanced Monthly Operations

### Handling Overdue Items

Overdue expense items (past due date, unpaid):

- Show visual indicators on dashboard
- Can be paid at any time
- Payment date can be backdated if needed
- Don't prevent new month creation

### Adjusting Due Dates

- Edit individual expense items for one-time changes
- Modify parent expense for ongoing changes
- Consider seasonal adjustments for utilities

### Managing Variable Amounts

For expenses with variable amounts (utilities):

1. Create recurring expense with estimated amount
2. Edit individual expense items when actual amounts known
3. Update parent expense amount if new pattern emerges

### Month Deletion Rules

- **Can delete**: Latest month if no payments recorded
- **Cannot delete**: Months with any paid expense items
- **Cannot delete**: Earlier months (must delete sequentially from latest)

## Monthly Analysis and Reporting

### Dashboard Insights

The dashboard provides real-time month analysis:

- **Budget vs. Actual**: Planned expenses compared to budget
- **Payment Progress**: How much of planned expenses are paid
- **Overdue Items**: Items past due date
- **Upcoming Due Dates**: Items due soon

### Month Detail Analysis

Month detail pages show:

- **Complete expense item list** for the month
- **Total amounts** (budgeted, planned, paid)
- **Payment method breakdown**
- **Budget category breakdown**

### Historical Comparison

Compare months to identify:

- **Spending trends**: Increasing or decreasing expenses
- **Payment patterns**: Early vs. late payment habits
- **Budget accuracy**: How well you estimate expenses
- **Seasonal variations**: Changes in utilities, etc.

## Best Practices

### Monthly Planning

- Review upcoming month's expenses before month creation
- Adjust expense amounts if you know they'll change
- Plan for seasonal variations in advance
- Consider one-time expenses for the coming month

### Payment Recording

- Record payments promptly for accurate tracking
- Use correct payment dates (not due dates)
- Double-check payment amounts
- Select appropriate payment methods

### Regular Review

- Check dashboard weekly to stay current
- Review overdue items regularly
- Analyze monthly totals against budgets
- Plan adjustments for following months

### Month-End Process

1. Ensure all payments for the month are recorded
2. Review budget performance
3. Check for any missed or incorrect payments
4. Plan any budget adjustments for next month
5. Create next month when ready

## Troubleshooting

### "I can't create next month"

- Ensure you're trying to create the immediate next month
- Check that you're not trying to skip a month
- Verify you have permission to create months

### "My expense item has wrong amount"

- Check the parent expense amount
- Edit the individual expense item for one-time changes
- Update parent expense for ongoing changes

### "Payment not showing in totals"

- Verify payment was saved successfully
- Check that payment date is in correct month
- Ensure payment amount was entered correctly

### "Missing expense items"

- Verify parent expenses are active (not closed)
- Check expense start dates and end dates
- Confirm month was created after expense was created

---

*The monthly workflow is the heart of PyGGy's approach to expense tracking. Master this process to
effectively manage your financial obligations. Next, learn
about [Payees & Payment Methods](payees_and_payments) to organize the who and how of your payments.*
