# Budget Management

Budgets in PyGGy serve as containers that organize related expenses and help you track spending
against planned amounts. Understanding how to create and manage budgets effectively is key to
successful expense tracking.

## What Are Budgets?

Budgets are organizational tools that:

- **Group related expenses** together for easier management
- **Set spending targets** with an initial amount per month
- **Track progress** by comparing actual expenses to budgeted amounts
- **Provide isolation** between different types of spending

## Budget Basics

### Creating Your First Budget

1. **Navigate to Budgets**: Click "Budgets" in the main navigation
2. **Add New Budget**: Click the "Add Budget" button
3. **Fill in the details**:

- **Name**: Choose a clear, descriptive name
- **Initial Amount**: Set your monthly budget target
- **Description**: Add optional context about this budget's purpose

### Budget Fields Explained

**Name**: The display name for your budget. Choose something that clearly identifies its purpose.

**Initial Amount**: Your starting budget balance. Can be positive (available funds), zero (starting
fresh), or negative (starting with a deficit).

**Description**: Optional field for additional context, notes, or rules about this budget.

## Budget Organization Strategies

### Single Budget Approach

Start with one budget called "Personal Expenses" or "Monthly Budget" if you prefer simplicity. This
works well for:

- Small households
- Simple financial situations
- Getting started with PyGGy

### Multiple Budget Strategies

#### By Expense Category

```text
- Household Bills (rent, utilities, insurance)
- Personal Expenses (food, entertainment, subscriptions)
- Transportation (car payment, gas, maintenance)
- Health & Medical (insurance, appointments, medications)
```

#### By Financial Stream

```text
- Personal Budget (individual spending)
- Joint Budget (shared household expenses)
- Business Expenses (work-related costs)
- Investment Property (rental property expenses)
```

#### By Family Member

```text
- John's Expenses
- Jane's Expenses
- Shared Family Expenses
- Kids' Activities
```

#### By Priority Level

```text
- Essential Expenses (rent, utilities, insurance)
- Important Expenses (groceries, transportation)
- Discretionary Expenses (entertainment, subscriptions)
```

## Working with Budgets

### Budget and Expense Relationship

- Every expense must be assigned to exactly one budget
- Expenses cannot be moved between budgets after creation
- Each budget tracks its own expense totals independently

### Viewing Budget Information

From the Budget list page, you can see:

- **Budget name and description**
- **Initial amount** (monthly target)
- **Current month totals**:
  - Total expense items for this month
  - Amount paid so far
  - Remaining balance

### Monthly Budget Tracking

PyGGy automatically calculates:

- **Budgeted**: Your initial amount (starting balance)
- **Planned**: Total of all expense items for the month
- **Paid**: Amount actually paid so far
- **Balance**: Starting balance minus planned expenses

## Advanced Budget Management

### Adjusting Budget Balance

You can modify the initial amount anytime:

1. Edit the budget from the budget list
2. Change the initial amount to reflect your current budget balance
3. This affects the budget calculations going forward

### Budget Performance Analysis

Monitor these key metrics:

- **Balance Tracking**: How your budget balance changes with planned expenses
- **Payment Progress**: Track how much of planned expenses are paid
- **Month-to-Month Trends**: Compare spending patterns across months

### Managing Budget Balance

When you need to adjust your budget:

- **Add funds**: Increase the initial amount when adding money to the budget
- **Review spending**: Analyze if planned expenses fit your available budget
- **Move expenses**: Consider if some expenses belong in different budgets
- **Defer expenses**: Postpone non-essential expenses to future months

## Best Practices

### Naming Conventions

Use clear, consistent naming:

- **Good**: "Household Bills", "Personal Spending", "Car Expenses"
- **Avoid**: "Budget1", "Misc", "Other"

### Initial Amount Setting

- Use 0.00 if starting fresh budget tracking
- Enter positive amounts if you have available funds in the budget
- Enter negative amounts if starting with a deficit or debt
- Adjust the amount when you add or remove funds from the budget

### Regular Review

- Check budget performance monthly
- Adjust budget amounts based on spending patterns
- Consider reorganizing if budgets become too broad or narrow

### Budget Granularity

**Too few budgets**: Everything mixed together, hard to track categories
**Too many budgets**: Overhead of managing many small buckets
**Just right**: Meaningful categories that help you understand spending

## Common Budget Scenarios

### Starting Fresh

1. Begin with one "General" budget (initial amount: `0.00`)
2. Add expenses and track for a month
3. Identify natural expense categories
4. Create additional budgets as needed
5. Move future expenses to appropriate budgets

### Starting with Existing Finances

1. Create budgets that match your current financial categories
2. Set initial amounts to reflect current balances (positive for available funds, negative for
   deficits)
3. Begin tracking expenses within these established budgets

### Seasonal Adjustments

For expenses that vary by season:

- Adjust budget amounts monthly
- Use separate budgets for seasonal categories
- Plan ahead for known seasonal spikes

### Shared Households

- Create budgets for shared vs. individual expenses
- Use descriptive names that indicate responsibility
- Consider separate budgets for joint financial goals

### Business vs. Personal

Keep business and personal expenses in separate budgets:

- Simplifies tax preparation
- Clearer financial picture
- Better expense categorization

## Troubleshooting

### "I can't find my expense"

- Check which budget the expense was assigned to
- Use the expense list to see all expenses across budgets
- Consider if the expense might be in an archived or closed state

### "My budget totals don't match"

- Verify you're looking at the correct month
- Check if expenses span multiple months (split payments)
- Ensure all payments are recorded in the system

### "I want to reorganize my budgets"

- You cannot move existing expenses between budgets
- Create new budgets with desired organization
- Create new expenses in the correct budgets going forward
- Close old expenses in incorrect budgets as needed

---

*Effective budget organization sets the foundation for meaningful expense tracking. Next,
explore [Monthly Workflow](monthly_workflow) to understand how PyGGy handles month-to-month expense
management.*
