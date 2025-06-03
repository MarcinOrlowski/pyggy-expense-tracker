# Enhanced Amount Input Sanitization TRD

**Ticket**: [Enhanced amount input sanitization with international format support](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/73)
**PRD Reference**: 0073_enhanced_amount_input_sanitization_PRD.md

## Technical Approach
We'll implement input sanitization using a custom Django form field `SanitizedDecimalField` that inherits from `DecimalField`. This field will preprocess user input to remove formatting characters and normalize decimal separators before standard validation. Frontend JavaScript will provide real-time feedback during typing and paste operations. Uses `TextInput` widget instead of `NumberInput` to avoid browser validation conflicts that would block sanitization. The solution leverages Django's existing form validation pipeline and maintains backward compatibility with existing DecimalField usage.

## Data Model
No database schema changes required. All existing DecimalField columns (`total_amount`, `initial_amount`, `amount`) continue using dot notation for storage. The sanitization occurs only during form input processing.

## API Design
**Form Field Interface:**
```python
# New custom field class
SanitizedDecimalField(forms.DecimalField):
    def to_python(self, value):
        # Sanitizes: "1 234,56 €" → "1234.56"
        # Returns Decimal object or ValidationError
        
# Usage in forms
total_amount = SanitizedDecimalField(
    max_digits=13, decimal_places=2,
    min_value=Decimal('0.01'),
    widget=forms.TextInput(attrs={
        'placeholder': '10.50, 10,50, $10.50, €10,50'
    })
)
```

**JavaScript Interface:**
```javascript
// Real-time sanitization on input events
function sanitizeAmountInput(inputValue) {
    // Supports: $, €, zł, zl currencies
    // Returns sanitized string: "12,34 zł" → "12.34"
}

// Paste event handler
input.addEventListener('paste', handlePasteEvent);
```

## Security & Performance
- **Input validation**: Comprehensive regex patterns prevent malicious input injection
- **Performance**: Sanitization regex operations have O(n) complexity, negligible for typical amount strings
- **Data integrity**: Backend validation ensures only valid decimals reach the database
- **Backwards compatibility**: Existing dot notation inputs pass through unchanged

## Technical Risks & Mitigations
1. **Risk**: Browser number input validation blocks sanitization → **Mitigation**: Use TextInput widget instead of NumberInput to allow sanitization before validation
2. **Risk**: Complex international number formats break sanitization → **Mitigation**: Conservative regex patterns for supported currencies ($, €, zł, zl) only
3. **Risk**: JavaScript disabled users get confusing validation errors → **Mitigation**: Backend sanitization provides same functionality, frontend is enhancement only
4. **Risk**: Existing forms break due to field replacement → **Mitigation**: Drop-in replacement maintains same API, comprehensive testing

## Implementation Plan
- **Phase 1 (S)**: Create `SanitizedDecimalField` with comprehensive sanitization logic - 1 day
- **Phase 2 (S)**: Update `ExpenseForm` and `BudgetForm` to use new field - 0.5 days
- **Phase 3 (M)**: Implement JavaScript real-time sanitization for all amount inputs - 1 day
- **Phase 4 (S)**: Add comprehensive test coverage for all input scenarios - 1 day
- **Phase 5 (XS)**: Update form templates with improved user feedback - 0.5 days

Dependencies: None - uses existing Django form framework

## Monitoring & Rollback
- **Feature flag**: Not required - backward compatible change
- **Key metrics**: Form validation error rates, successful expense/budget creation rates
- **Rollback**: Revert form field changes - no database migration needed
- **Testing**: Comprehensive unit tests for all sanitization patterns plus integration tests for form submission flows