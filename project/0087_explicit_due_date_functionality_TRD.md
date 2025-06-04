# TRD: Explicit Due Date Functionality (#0087)

## Technical Overview
This document outlines the technical implementation for exposing explicit due date functionality in the expense management system, including model restructuring, service logic updates, and UI enhancements.

## Architecture Changes

### Database Schema Changes

#### Expense Model Restructuring
```python
# Field renames for clarity
started_at → start_date          # When expense schedule begins
total_amount → amount           # Per-installment amount (split) or total (others)
installments_count → total_parts # Total number of installments
initial_installment → skip_parts # Number of initial installments to skip

# New field
day_of_month                    # Day for due date calculation with fallback logic
```

#### Migration Strategy
- **Phase 1**: Add new nullable fields
- **Phase 2**: Data migration from old to new fields  
- **Phase 3**: Remove old fields and apply constraints
- **Phase 4**: Update indexes and relationships

### Service Layer Changes

#### Due Date Processing Logic
```python
def create_expense_items_for_month(expense: Expense, month: Month):
    """
    Updated logic for expense item creation:
    
    For one-time expenses:
    - Create item if no items exist yet
    - Due date calculated using day_of_month for target month
    - No restriction based on start_date vs due_date relationship
    
    For recurring expenses:
    - Maintain existing start_date based logic
    - Due date calculated using day_of_month for target month
    """
```

#### Key Algorithm Changes
1. **One-Time Expense Processing**: Removed early return condition that prevented creation when start_date > month_end_date
2. **Due Date Calculation**: Enhanced `get_due_date_for_month()` with proper fallback for shorter months
3. **Item Creation**: Simplified logic to focus on due_date rather than start_date constraints

### Model Layer Enhancements

#### Expense Model Methods
```python
def get_due_date_for_month(self, year, month):
    """Calculate due date with day-of-month fallback logic"""
    last_day_of_month = calendar.monthrange(year, month)[1]
    actual_day = min(self.day_of_month, last_day_of_month)
    return date(year, month, actual_day)

def calculate_total_cost(self):
    """Calculate total cost based on expense type"""
    # Implementation varies by expense type
    
def get_remaining_parts(self):
    """Get remaining installments for split payments"""
    # Accounts for skip_parts in calculation
```

#### ExpenseItem Enhancements
- Enhanced due_date field visibility
- Updated validation logic for date editing restrictions
- Improved string representations for debugging

### Form Layer Updates

#### ExpenseForm Enhancements
- Updated field names to match new model structure
- Enhanced day_of_month field with auto-population from start_date
- Improved validation for split payment scenarios
- Added help text for user guidance

#### ExpenseItemEditForm Updates
- Enhanced due date editing with month-specific validation
- Dynamic help text showing allowed date ranges
- Support for one-time expense date flexibility

### Template and UI Changes

#### Expense Form Template
```html
<!-- Enhanced day_of_month field with auto-population -->
<script>
document.getElementById('id_start_date').addEventListener('change', function() {
    const startDate = new Date(this.value);
    if (!isNaN(startDate)) {
        document.getElementById('id_day_of_month').value = startDate.getDate();
    }
});
</script>
```

#### Admin Interface Updates
- Updated field names in admin configuration
- Maintained existing functionality with new field structure

### Testing Strategy

#### Test Coverage Areas
1. **Model Tests**: Field validation, due date calculation, total cost calculation
2. **Service Tests**: Expense item creation logic, month processing
3. **Form Tests**: Validation, field behavior, user input handling
4. **Integration Tests**: End-to-end expense creation and processing
5. **Migration Tests**: Data preservation during schema changes

#### Key Test Scenarios
- One-time expenses with future start dates
- Due date calculations for months with varying days
- Split payment processing with skip_parts
- Edge cases for date validation and month boundaries

## Technical Decisions

### Field Naming Rationale
- `start_date` over `started_at`: More intuitive for users and clearer intent
- `amount` over `total_amount`: Simplified based on context (per-installment vs total)
- `total_parts`/`skip_parts`: More descriptive than generic count terms

### Due Date Logic Design
- **Flexibility Priority**: Chose to allow flexible due date scheduling over strict start_date validation
- **User Experience**: Prioritized intuitive behavior where due dates can be set independently
- **Backward Compatibility**: Maintained existing behavior for recurring expense types

### Migration Strategy
- **Safety First**: Multi-phase migration to prevent data loss
- **Rollback Capability**: Each phase can be reversed if needed
- **Data Validation**: Comprehensive checks during migration process

## Performance Considerations

### Database Impact
- **Index Strategy**: Updated indexes for new field names
- **Query Optimization**: Due date calculations remain efficient
- **Migration Performance**: Chunked data updates for large datasets

### Runtime Performance
- **Caching**: Due date calculations can be cached if needed
- **Query Patterns**: No significant changes to existing query performance
- **Memory Usage**: Minimal impact from field restructuring

## Security Considerations

### Data Validation
- Enhanced input validation for new field structures
- Maintained existing security patterns for form processing
- Added validation for due date logic edge cases

### Access Control
- No changes to existing permission structures
- Maintained budget-scoped access controls
- Form validation prevents unauthorized data manipulation

## Deployment Strategy

### Migration Execution
1. **Pre-deployment**: Backup database
2. **Phase 1**: Deploy code with migration Phase 1 (add fields)
3. **Phase 2**: Run data migration scripts
4. **Phase 3**: Deploy final migration (remove old fields)
5. **Post-deployment**: Verify data integrity

### Rollback Plan
- Each migration phase can be rolled back independently
- Data preservation strategies for each rollback scenario
- Monitoring for post-deployment issues

## Monitoring and Maintenance

### Health Checks
- Verify due date calculations produce expected results
- Monitor expense item creation success rates
- Track any errors in month processing logic

### Performance Monitoring
- Database query performance for new field structures
- Form submission success rates
- Migration execution times and success rates

## Future Enhancements

### Potential Improvements
- Advanced due date scheduling (business days, custom patterns)
- Due date notification system
- Calendar integration for due date visualization
- Bulk due date management tools

### Technical Debt
- Consider consolidating related due date logic into dedicated service
- Evaluate caching strategies for frequently calculated due dates
- Review form validation patterns for consistency

---
**Created**: 2025-01-04  
**Status**: Implemented  
**Ticket**: [#0087](https://github.com/project/issues/87)  
**Implementation**: Complete - All tests passing (143/143)