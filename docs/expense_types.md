# Understanding Expense Types

PyGGy supports four distinct expense types, each designed for different payment scenarios.
Understanding when and how to use each type is crucial for effective expense tracking.

## The Four Expense Types

### 1. Endless Recurring

**Best for**: Bills that continue indefinitely with no known end date

**How it works**: Creates one expense item every month until you manually close the expense.

**Examples**:

- Monthly rent or mortgage payments
- Utility bills (electricity, gas, water)
- Subscription services (Netflix, Spotify, gym memberships)
- Insurance premiums
- Phone/internet bills

**Key characteristics**:

- Continues generating monthly expense items indefinitely
- Must be manually closed when no longer needed
- Perfect for ongoing monthly obligations

**When to choose**: Use this for any regular monthly bill that doesn't have a predetermined end
date.

### 2. One Time

**Best for**: Single, non-recurring purchases

**How it works**: Creates one expense item for the specified month only, then automatically closes.

**Examples**:

- Medical appointments or procedures
- Furniture purchases
- Gifts or special occasion expenses
- Repair services
- Annual fees (domain renewals, software licenses)

**Key characteristics**:

- Creates only one expense item
- Automatically closes after the expense item is created
- Cannot create additional items even if unpaid

**When to choose**: Use this for any expense that happens only once and doesn't repeat.

### 3. Split Payment

**Best for**: Fixed installment plans with a known number of payments

**How it works**: Creates expense items for the exact number of installments specified, then
automatically closes.

**Examples**:

- Car loans (36 payments, 60 payments, etc.)
- Personal loans with fixed terms
- Payment plans for large purchases
- Furniture financing
- Medical procedure payment plans

**Key characteristics**:

- Requires specifying total number of installments when created
- Creates exactly that many expense items over consecutive months
- Automatically closes when the final installment is created
- Amount field represents the per-installment amount, not total

**When to choose**: Use this when you know exactly how many payments you'll make.

### 4. Recurring with End Date

**Best for**: Regular payments that have a known end date

**How it works**: Creates monthly expense items until the specified end date, then automatically
closes.

**Examples**:

- Limited-time gym memberships
- Temporary subscription services
- Seasonal services (lawn care, snow removal)
- Short-term rentals
- Trial periods that convert to paid

**Key characteristics**:

- Requires setting an end date when created
- Creates monthly expense items until the end date
- Automatically closes after the end date passes
- End date is inclusive (expense items created through the end month)

**When to choose**: Use this for recurring expenses that you know will end on a specific date.

## Choosing the Right Type

### Decision Tree

Ask yourself these questions:

1. **Is this a one-time expense?**

- Yes → **One Time**

1. **Is this a recurring expense?**

- Yes, continue to question 3

1. **Do you know when it will end?**

- No → **Endless Recurring**
- Yes, continue to question 4

1. **Do you know the exact number of payments?**

- Yes → **Split Payment**
- No, but I know the end date → **Recurring with End Date**

### Common Scenarios

**Starting a new subscription** (Netflix, gym):

- If it's open-ended: **Endless Recurring**
- If it's a trial with known end: **Recurring with End Date**

**Taking out a loan**:

- Car loan with 48 payments: **Split Payment**
- Credit card debt (variable payments): **One Time** for each payment

**Seasonal services**:

- Year-round lawn care: **Endless Recurring**
- Summer-only pool service: **Recurring with End Date**

**Large purchases**:

- Buying furniture outright: **One Time**
- Financing furniture (12 payments): **Split Payment**

## Important Notes

### Amount Field Behavior

- **One Time, Endless Recurring, Recurring with End**: Amount is the full payment
- **Split Payment**: Amount is the per-installment amount (not the total)

### Start Date Rules

- All expenses must start in the current month or later
- Start date determines when the first expense item is created
- Day of month can be different from start date (for recurring due dates)

### Editing Restrictions

- Expense type cannot be changed after creation
- Some fields become read-only once expense items exist
- Amount can usually be edited, but changes only affect future expense items

### Automatic Closure

- **One Time**: Closes immediately after creation
- **Split Payment**: Closes after the final installment is created
- **Recurring with End**: Closes after the end date
- **Endless Recurring**: Never closes automatically (manual closure required)

## Advanced Tips

### Converting Between Types

You can't change expense types, but you can work around this:

- **Close the current expense** when you want to stop it
- **Create a new expense** with the correct type for ongoing needs

### Managing Seasonal Changes

For expenses that change seasonally:

- Use **Recurring with End Date** for seasonal periods
- Create new expenses for different seasons with different amounts

### Handling Variable Amounts

For bills with varying amounts (utilities):

- Use **Endless Recurring** with an estimated amount
- Edit individual expense items when actual amounts are known

### Trial Periods

For services with trial periods that convert:

- Start with **Recurring with End Date** for the trial
- Create **Endless Recurring** for the ongoing service

---

*Understanding these expense types will help you model your real-world financial obligations
accurately in PyGGy. Next, learn about [Budget Management](budgets) to organize these expenses
effectively.*
