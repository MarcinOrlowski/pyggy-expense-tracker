# TRD: Add Optional Notes Field to Expense Entity

**Ticket:** #0019  
**Type:** Enhancement  
**Priority:** Normal  
**Milestone:** backlog  

## Technical Overview

This document outlines the technical implementation details for adding an optional notes field to the Expense entity. The implementation involves database schema changes, model updates, form modifications, and template enhancements.

## Architecture Impact

### Database Schema Changes

**Table:** `expenses_expense`
```sql
ALTER TABLE expenses_expense ADD COLUMN notes TEXT NULL;
```

**Field Specifications:**
- **Field Name:** `notes`
- **Type:** `TEXT` (unlimited length)
- **Constraints:** `NULL`, `BLANK`
- **Default:** `NULL`
- **Index:** Not required (optional text search in future)

### Model Layer Changes

**File:** `expenses/models.py`

```python
class Expense(models.Model):
    # ... existing fields ...
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes or additional context about this expense"
    )
    # ... rest of the model ...
```

**Rationale for TextField:**
- TextField provides unlimited storage capacity
- Form-level validation handles UI constraints
- More flexible for future requirements

### Form Layer Changes

**File:** `expenses/forms.py`

```python
class ExpenseForm(forms.ModelForm):
    notes = forms.CharField(
        max_length=1024,
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'cols': 50,
            'maxlength': 1024,
            'placeholder': 'Add additional notes or context about this expense',
            'class': 'form-control'
        }),
        help_text="Optional notes or additional context about this expense (max 1024 characters)"
    )
    
    class Meta:
        model = Expense
        fields = ['payee', 'title', 'expense_type', 'total_amount', 
                 'installments_count', 'started_at', 'notes']
        widgets = {
            # ... existing widgets ...
            # notes widget defined above as custom field
        }
```

**JavaScript Enhancement for Character Counter:**
```javascript
// Add to expense_form.html
function setupNotesCounter() {
    const notesField = document.querySelector('textarea[name="notes"]');
    if (notesField) {
        const counter = document.createElement('small');
        counter.className = 'character-counter';
        notesField.parentNode.appendChild(counter);
        
        function updateCounter() {
            const remaining = 1024 - notesField.value.length;
            counter.textContent = `${remaining} characters remaining`;
            counter.className = remaining < 50 ? 'character-counter warning' : 'character-counter';
        }
        
        notesField.addEventListener('input', updateCounter);
        updateCounter();
    }
}
```

### Template Layer Changes

#### 1. Form Template (`expenses/templates/expenses/expense_form.html`)

**Addition after started_at field:**
```html
<div class="form-group">
    <label for="{{ form.notes.id_for_label }}">{{ form.notes.label }}:</label>
    {{ form.notes }}
    {% if form.notes.help_text %}
        <small>{{ form.notes.help_text }}</small>
    {% endif %}
    {% if form.notes.errors %}
        <div class="message error">{{ form.notes.errors }}</div>
    {% endif %}
</div>
```

#### 2. Detail Template (`expenses/templates/expenses/expense_detail.html`)

**Addition in expense details card:**
```html
<div class="grid-2-cols">
    <div>
        <!-- existing fields -->
    </div>
    <div>
        <!-- existing fields -->
    </div>
</div>

{% if expense.notes %}
<div class="notes-section">
    <p><strong>Notes:</strong></p>
    <div class="notes-content">{{ expense.notes|linebreaks }}</div>
</div>
{% endif %}
```

#### 3. List Template (`expenses/templates/expenses/expense_list.html`)

**Addition of notes indicator column:**
```html
<thead>
    <tr>
        <th>Title</th>
        <th>Payee</th>
        <th>Type</th>
        <th class="amount-column">Total Amount</th>
        <th>Started</th>
        <th>Installments</th>
        <th>Notes</th> <!-- New column -->
        <th class="actions-column">Actions</th>
    </tr>
</thead>
<tbody>
    {% for expense in expenses %}
    <tr>
        <!-- existing columns -->
        <td>
            {% if expense.notes %}
                <i class="fas fa-sticky-note" title="Has notes"></i>
            {% else %}
                -
            {% endif %}
        </td>
        <!-- actions column -->
    </tr>
    {% endfor %}
</tbody>
```

### CSS Enhancements

**File:** `src/scss/_components.scss`

```scss
// Notes specific styles
.notes-section {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);
}

.notes-content {
    background-color: var(--background-light);
    padding: 0.75rem;
    border-radius: 4px;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.character-counter {
    display: block;
    text-align: right;
    margin-top: 0.25rem;
    color: var(--text-muted);
    
    &.warning {
        color: var(--color-warning);
        font-weight: 500;
    }
}

// Notes indicator in table
.fas.fa-sticky-note {
    color: var(--color-info);
}
```

## Database Migration

**File:** `expenses/migrations/0008_expense_notes.py`

```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('expenses', '0007_add_settings_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='notes',
            field=models.TextField(
                blank=True,
                help_text='Optional notes or additional context about this expense',
                null=True
            ),
        ),
    ]
```

## Implementation Sequence

### Phase 1: Database and Model
1. Add `notes` field to Expense model
2. Generate and apply migration
3. Update model `__str__` method if needed

### Phase 2: Forms and Validation
1. Update ExpenseForm to include notes field
2. Add appropriate widget configuration
3. Test form validation

### Phase 3: Templates and UI
1. Update expense_form.html with notes field
2. Add character counter JavaScript
3. Update expense_detail.html to display notes
4. Update expense_list.html with notes indicator
5. Add CSS styling

### Phase 4: Testing and Validation
1. Test expense creation with notes
2. Test expense editing with notes
3. Test character limit validation
4. Test display in all views
5. Test migration on development data

## Technical Considerations

### Performance Impact
- **Minimal:** TextField addition has negligible performance impact
- **Storage:** Variable per expense based on actual content
- **Form Constraint:** UI enforces 1024 character limit for usability
- **Queries:** No impact on existing queries
- **Indexing:** Consider text search index in future if needed

### Backward Compatibility
- **100% Compatible:** All existing expenses will have `notes=NULL`
- **No Breaking Changes:** All existing functionality preserved
- **Migration Safe:** Non-destructive schema change

### Security Considerations
- **XSS Prevention:** Django's `linebreaks` filter automatically escapes HTML
- **Input Validation:** Max length enforced at model and form level
- **No Special Permissions:** Uses existing expense permissions

### Error Handling
- **Validation Errors:** Standard Django form validation for 1024 char limit
- **Database Errors:** Migration rollback if needed
- **Character Limit:** Client-side and server-side form validation (not database constraint)

## Testing Strategy

### Unit Tests
```python
# expenses/tests.py additions
def test_expense_notes_field_optional(self):
    """Test that notes field is optional"""
    expense = Expense.objects.create(
        title="Test Expense",
        expense_type="one_time",
        total_amount=100.00,
        started_at=date.today()
    )
    self.assertIsNone(expense.notes)

def test_expense_notes_form_max_length(self):
    """Test notes field form validation for max length"""
    long_notes = "x" * 1025
    form_data = {
        'title': 'Test',
        'expense_type': 'one_time',
        'total_amount': '100.00',
        'started_at': date.today(),
        'notes': long_notes
    }
    form = ExpenseForm(data=form_data)
    self.assertFalse(form.is_valid())
    self.assertIn('notes', form.errors)

def test_expense_notes_database_unlimited(self):
    """Test that database accepts notes longer than form limit"""
    # Direct model save bypasses form validation
    long_notes = "x" * 2000
    expense = Expense.objects.create(
        title="Test Expense",
        expense_type="one_time", 
        total_amount=100.00,
        started_at=date.today(),
        notes=long_notes
    )
    expense.refresh_from_db()
    self.assertEqual(len(expense.notes), 2000)
```

### Integration Tests
- Form submission with notes
- Template rendering with and without notes
- Character counter functionality
- Migration forward and backward

## Deployment Considerations

### Migration Deployment
1. **Zero Downtime:** Migration adds nullable column
2. **Rollback Safe:** Can be reversed if needed
3. **Data Preservation:** No data loss risk

### Environment Considerations
- **Development:** Apply migration locally first
- **Staging:** Test full user workflow
- **Production:** Standard migration deployment

## Future Enhancements

### Potential Improvements
1. **Rich Text:** Upgrade to rich text editor
2. **Search:** Full-text search on notes
3. **Templates:** Note templates for common scenarios
4. **Export:** Include notes in expense exports
5. **History:** Track notes changes over time

### Technical Debt Considerations
- Form validation provides UI constraints while maintaining database flexibility
- Monitor query performance with larger datasets
- Evaluate need for database indexing for text search

## Validation Checklist

- [ ] Model field added with correct constraints
- [ ] Migration generated and tested
- [ ] Form updated with proper widget
- [ ] Templates updated in all relevant views
- [ ] Character counter JavaScript implemented
- [ ] CSS styling added
- [ ] Unit tests written and passing
- [ ] Integration tests completed
- [ ] Manual testing completed
- [ ] Documentation updated

---

**Ready for Implementation:** All technical specifications defined and ready for development phase.