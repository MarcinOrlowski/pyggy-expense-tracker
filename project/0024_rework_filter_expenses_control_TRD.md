# Technical Requirements Document (TRD)

## Ticket #0024: Rework Filter Expenses Control to Take One Line Only

### 1. Technical Overview

This document outlines the technical implementation details for consolidating the expense filter controls into a single-line interface, replacing the current multi-line card-based layout.

### 2. Architecture Impact

- **Frontend Only**: Changes are limited to HTML templates and SCSS styles
- **No Backend Changes**: Django views and models remain unchanged
- **No Database Impact**: No migrations or data changes required
- **No API Changes**: Form submission and processing logic stays the same

### 3. Implementation Details

#### 3.1 File Modifications

**Files to Modify:**

1. `expenses/templates/expenses/expense_list.html` - Update filter HTML structure
2. `src/scss/_components.scss` - Add new filter-bar styles
3. `src/scss/_responsive.scss` - Add responsive behavior for filter-bar

**Files to Compile:**

- `compile_scss.py` - Run after SCSS changes to generate CSS

#### 3.2 HTML Structure Changes

**Current Structure (to be removed):**

```html
<div class="card">
    <div class="card-header">Filter Expenses</div>
    <div class="card-body">
        <form method="get">
            <div class="flex-row">
                <div class="form-group flex-1">...</div>
                <div class="form-group flex-1">...</div>
            </div>
            <div class="form-actions">...</div>
        </form>
    </div>
</div>
```

**New Structure:**

```html
<div class="filter-bar">
    <form method="get" class="filter-form">
        <div class="filter-group">
            <label for="type">Expense Type:</label>
            <select name="type" id="type">
                <option value="">All Types</option>
                {% for value, label in expense_types %}
                    <option value="{{ value }}" {% if value == selected_type %}selected{% endif %}>{{ label }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="filter-group">
            <label for="payee">Payee:</label>
            <select name="payee" id="payee">
                <option value="">All Payees</option>
                {% for payee in payees %}
                    <option value="{{ payee.pk }}" {% if payee.pk == selected_payee %}selected{% endif %}>{{ payee.name }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="filter-actions">
            <button type="submit" class="btn btn-filter"><i class="fas fa-filter icon-left"></i>Filter</button>
            <a href="{% url 'expense_list' %}" class="btn btn-secondary"><i class="fas fa-eraser icon-left"></i>Clear</a>
        </div>
    </form>
</div>
```

#### 3.3 SCSS Styles Implementation

**New styles to add to `_components.scss`:**

```scss
// Filter Bar Styles
.filter-bar {
    background: var(--bg-tertiary);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(189, 147, 249, 0.2);
    box-shadow: 0 2px 8px rgba(0,0,0,0.5);
}

.filter-form {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    flex-wrap: wrap;
}

.filter-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex: 0 1 auto;
}

.filter-group label {
    margin: 0;
    font-weight: 500;
    color: var(--color-cyan);
    white-space: nowrap;
}

.filter-group select {
    width: auto;
    min-width: 150px;
    padding: 0.375rem 0.75rem;
    border: 1px solid rgba(189, 147, 249, 0.3);
    border-radius: 4px;
    font-size: 0.9rem;
    background-color: var(--bg-secondary);
    color: var(--text-primary);
    transition: all 0.3s;
}

.filter-group select:focus {
    outline: none;
    border-color: var(--color-purple);
    box-shadow: 0 0 0 2px var(--color-purple-muted);
    background-color: var(--bg-primary);
}

.filter-actions {
    display: flex;
    gap: 0.5rem;
    margin-left: auto;
}

// Filter button specific styles
.btn-filter {
    background-color: var(--color-purple);
    border: 1px solid var(--color-purple);
    color: var(--bg-primary);
    padding: 0.375rem 0.75rem;
}

.btn-filter:hover {
    background-color: transparent;
    color: var(--color-purple);
    transform: none;
    box-shadow: 0 0 10px var(--color-purple-muted);
}
```

**Responsive styles to add to `_responsive.scss`:**

```scss
// Filter bar responsive
@media (max-width: 768px) {
    .filter-form {
        flex-direction: column;
        align-items: stretch;
        gap: 0.75rem;
    }

    .filter-group {
        flex-direction: column;
        align-items: stretch;
        gap: 0.25rem;
    }

    .filter-group select {
        width: 100%;
    }

    .filter-actions {
        margin-left: 0;
        justify-content: center;
        margin-top: 0.5rem;
    }
}
```

### 4. Implementation Steps

1. **Update HTML Template**
   - Open `expenses/templates/expenses/expense_list.html`
   - Replace lines 9-39 (the filter card section) with new filter-bar structure
   - Ensure form functionality remains intact

2. **Add SCSS Styles**
   - Add filter-bar styles to `src/scss/_components.scss`
   - Add responsive styles to `src/scss/_responsive.scss`
   - Ensure styles follow existing design patterns

3. **Compile SCSS**
   - Run `python compile_scss.py` to generate updated CSS
   - Verify CSS compilation is successful

4. **Testing Checklist**
   - [ ] Filter functionality works as before
   - [ ] Selected values persist after filtering
   - [ ] Clear button resets filters
   - [ ] Layout is single-line on desktop (>768px)
   - [ ] Layout stacks properly on mobile (<768px)
   - [ ] Dark theme colors are consistent
   - [ ] No visual glitches or alignment issues

### 5. Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Flexbox support required (all modern browsers)
- No JavaScript dependencies

### 6. Performance Considerations

- Reduced DOM elements (removed card wrapper)
- Less CSS to process
- Expected minor performance improvement

### 7. Security Considerations

- No security impact
- Form maintains CSRF protection
- No new input validation required

### 8. Rollback Plan

- Keep backup of original `expense_list.html`
- SCSS changes are additive (old styles can coexist)
- Git revert if needed

### 9. Testing Scenarios

**Desktop Testing:**

1. Verify single-line layout at 1920x1080
2. Test filter functionality with various selections
3. Ensure proper spacing between elements
4. Check hover states on buttons and dropdowns

**Mobile Testing:**

1. Verify stacked layout at 375x667 (iPhone SE)
2. Test touch interactions with dropdowns
3. Ensure buttons are tap-friendly
4. Verify no horizontal scroll

**Edge Cases:**

1. Long payee names in dropdown
2. No payees available
3. Filter with no results
4. Multiple filter combinations

### 10. Documentation Updates

- No user documentation required (UI is self-explanatory)
- Update any developer documentation if it references the filter UI

### 11. Deployment Notes

- No special deployment requirements
- Standard CSS cache busting may be needed
- No database migrations
- No service restarts required
