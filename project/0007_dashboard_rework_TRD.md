# TRD: Dashboard Rework - Separate Current Month Summary and Expense List

**Ticket:** [#0007](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/7)  
**Version:** 1.0  
**Date:** 2025-01-06  
**Related PRD:** `0007_dashboard_rework_PRD.md`

## Technical Overview

This document details the technical implementation for reworking the dashboard to separate the current month summary from the expense list, creating distinct sections for better user experience and establishing a foundation for future widget-based enhancements.

## Current State Analysis

### Files Affected
- **Primary:** `/expenses/templates/expenses/dashboard.html` (lines 1-84)
- **No changes required:** `/expenses/views.py`, `/expenses/urls.py`, models, or CSS

### Current Template Structure
```html
<div class="card">
    <div class="card-header">Current Month Summary - YYYY-MM</div>
    <div class="card-body">
        <!-- Summary stats in grid-3-cols -->
        <!-- Combined expense items table -->
    </div>
</div>
```

### Current Data Flow
- View: `dashboard()` in `/expenses/views.py:11-50`
- Context variables preserved:
  - `current_month`, `pending_items`, `paid_items`
  - `total_pending`, `total_paid`, `total_month`
  - `current_date`, `has_any_months`

## Technical Design

### New Template Structure
```html
<!-- Summary Widget Section -->
<div class="card">
    <div class="card-header">Current Month Summary</div>
    <div class="card-body">
        <!-- Only summary stats grid -->
    </div>
</div>

<!-- Expense List Section -->
<div class="card">
    <div class="card-header">Current Month Expenses</div>
    <div class="card-body">
        <!-- Only expense items table -->
    </div>
</div>
```

### Implementation Strategy

#### Phase 1: Split Template Structure
1. **Extract Summary Widget** (lines 26-36)
   - Move `grid-3-cols` summary stats to first card
   - Preserve total calculations and formatting
   - Keep existing conditional logic for no data states

2. **Extract Expense List** (lines 38-78)
   - Move expense items table to second card  
   - Preserve table structure, styling, and actions
   - Keep pending/paid item iterations and styling

3. **Handle Edge Cases**
   - No months scenario (lines 22-24)
   - Current month not processed (lines 79-81)
   - No expense items (lines 76-78)

#### Phase 2: Enhance Headers and Context
1. **Summary Widget Header**
   - Show month identifier when available
   - Clear labeling for summary data

2. **Expense List Header**  
   - Contextual header based on data availability
   - Preserve month context display

## Detailed Implementation

### Template Changes (`dashboard.html`)

#### Current Structure (lines 8-83):
```html
<div class="card">
    <div class="card-header">
        {% if has_any_months %}
            Current Month Summary
            {% if current_month %}
                - {{ current_month.year }}-{{ current_month.month|stringformat:"02d" }}
            {% else %}
                - {{ current_date.year }}-{{ current_date.month|stringformat:"02d" }} (Not processed yet)
            {% endif %}
        {% else %}
            Welcome to PyGGy
        {% endif %}
    </div>
    <div class="card-body">
        <!-- Welcome message OR summary + table -->
    </div>
</div>
```

#### New Structure:
```html
<!-- Summary Widget -->
<div class="card">
    <div class="card-header">
        {% if has_any_months %}
            Current Month Summary
            {% if current_month %}
                - {{ current_month.year }}-{{ current_month.month|stringformat:"02d" }}
            {% else %}
                - {{ current_date.year }}-{{ current_date.month|stringformat:"02d" }} (Not processed yet)
            {% endif %}
        {% else %}
            Welcome to PyGGy
        {% endif %}
    </div>
    <div class="card-body">
        {% if not has_any_months %}
            <p>No months have been created yet. Start by processing your first month to begin tracking expenses.</p>
            <p>Go to <strong>Months → Add initial month</strong> to choose your starting month.</p>
        {% elif current_month %}
            <div class="grid-3-cols mb-3">
                <div>
                    <p><strong>Total Month:</strong> ${{ total_month|floatformat:2 }}</p>
                </div>
                <div>
                    <p><strong>Pending:</strong> ${{ total_pending|floatformat:2 }} ({{ pending_items|length }} items)</p>
                </div>
                <div>
                    <p><strong>Paid:</strong> ${{ total_paid|floatformat:2 }} ({{ paid_items|length }} items)</p>
                </div>
            </div>
        {% else %}
            <p>The current month hasn't been processed yet.</p>
        {% endif %}
    </div>
</div>

<!-- Expense List Section -->
{% if has_any_months and current_month %}
<div class="card">
    <div class="card-header">
        Current Month Expenses - {{ current_month.year }}-{{ current_month.month|stringformat:"02d" }}
    </div>
    <div class="card-body">
        {% if pending_items or paid_items %}
            <table class="table">
                <thead>
                    <tr>
                        <th>Due Date</th>
                        <th class="amount-column">Amount</th>
                        <th>Expense</th>
                        <th>Payee</th>
                        <th class="actions-column">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in pending_items %}
                    <tr class="expense-item-pending">
                        <td>{{ item.due_date|date:"Y-m-d" }}</td>
                        <td class="amount-column">${{ item.amount|floatformat:2 }}</td>
                        <td>{{ item.expense.title }}</td>
                        <td>{% if item.expense.payee %}{{ item.expense.payee.name }}{% else %}-{% endif %}</td>
                        <td class="actions-column">
                            <a href="{% url 'expense_item_pay' item.pk %}" class="btn btn-success btn-sm" title="Mark as Paid" aria-label="Mark as Paid"><i class="fas fa-circle-check"></i></a>
                            <a href="{% url 'expense_detail' item.expense.pk %}" class="btn btn-secondary btn-sm" title="View Details" aria-label="View Details"><i class="fas fa-eye"></i></a>
                        </td>
                    </tr>
                    {% endfor %}
                    {% for item in paid_items %}
                    <tr class="expense-item-paid">
                        <td>{{ item.due_date|date:"Y-m-d" }}</td>
                        <td class="amount-column">${{ item.amount|floatformat:2 }}</td>
                        <td>{{ item.expense.title }}</td>
                        <td>{% if item.expense.payee %}{{ item.expense.payee.name }}{% else %}-{% endif %}</td>
                        <td class="actions-column">
                            <a href="{% url 'expense_item_unpay' item.pk %}" class="btn btn-warning btn-sm" title="Mark as Unpaid" aria-label="Mark as Unpaid"><i class="fas fa-rotate-left"></i></a>
                            <a href="{% url 'expense_detail' item.expense.pk %}" class="btn btn-secondary btn-sm" title="View Details" aria-label="View Details"><i class="fas fa-eye"></i></a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <p>No expense items this month.</p>
        {% endif %}
    </div>
</div>
{% endif %}
```

## Edge Case Handling

### Scenario 1: No Months Exist (`has_any_months = False`)
- **Display:** Summary widget only with welcome message
- **Hide:** Expense list section completely
- **Behavior:** Guide user to create first month

### Scenario 2: Current Month Not Processed (`current_month = None`)
- **Display:** Summary widget with "not processed" message  
- **Hide:** Expense list section
- **Behavior:** Preserve current UX flow

### Scenario 3: No Expense Items (`pending_items` and `paid_items` empty)
- **Display:** Both widgets with appropriate empty state messages
- **Behavior:** Show structure but indicate no data

### Scenario 4: Normal Operation
- **Display:** Both widgets with full data
- **Behavior:** Standard dashboard functionality

## CSS and Styling

### No CSS Changes Required
- Existing `.card`, `.card-header`, `.card-body` classes preserved
- Current responsive grid system (`grid-3-cols`) maintained
- All existing styling classes for tables, buttons, and status preserved
- Mobile responsiveness unchanged

### Spacing Considerations
- Cards naturally spaced with existing `.card` margin-bottom
- Grid layouts maintain current spacing with existing utilities
- No new CSS classes needed

## Testing Strategy

### Functional Testing
1. **All Edge Cases**
   - No months exist → Welcome message only
   - Current month not processed → Summary only
   - No expense items → Empty state messages
   - Normal operation → Both sections populated

2. **Data Integrity**
   - All calculations identical (total_month, total_pending, total_paid)
   - Item counts match current behavior
   - Date formatting preserved

3. **Interactive Elements**
   - Pay/unpay buttons function identically
   - View details links work
   - All existing actions preserved

### UI/UX Testing
1. **Visual Hierarchy**
   - Clear separation between summary and details
   - Logical information flow (summary → details)
   - Consistent styling and spacing

2. **Responsive Design**
   - Mobile layout preservation
   - Grid responsiveness maintained
   - Button sizing and spacing preserved

## Risk Mitigation

### Low-Risk Implementation
- **Template-only changes:** No business logic modification
- **Preserve existing classes:** All CSS and styling maintained  
- **Identical data flow:** Same context variables and calculations
- **Conservative approach:** Minimal structural changes

### Validation Steps
1. **Before/After Comparison:** Ensure identical functionality
2. **Cross-browser Testing:** Verify layout consistency
3. **Mobile Testing:** Confirm responsive behavior
4. **Edge Case Verification:** Test all conditional scenarios

## Future Enhancement Foundation

### Widget Architecture Preparation
This implementation establishes patterns for future widgets:
- **Modular cards:** Each section in own card container
- **Consistent headers:** Clear labeling pattern
- **Flexible layout:** Easy to add new widget cards
- **Preserved styling:** Compatible with existing theme

### Potential Future Widgets
- Recent transactions summary
- Spending trends chart
- Upcoming payment alerts
- Monthly comparison metrics
- Quick action buttons

## Implementation Checklist

- [ ] Back up current `dashboard.html`
- [ ] Implement summary widget section
- [ ] Implement expense list section  
- [ ] Test all edge cases
- [ ] Verify responsive design
- [ ] Validate all interactive elements
- [ ] Confirm visual consistency
- [ ] Performance check (no degradation)

## Rollback Plan

Simple template revert if issues arise:
1. Restore original `dashboard.html` from backup
2. No database or code changes to revert
3. Zero downtime rollback capability

## Success Criteria

✅ **Technical Completion:**
- Two distinct card sections implemented
- All existing functionality preserved
- No visual regressions
- Responsive design maintained
- Code follows project standards
- All edge cases handled identically