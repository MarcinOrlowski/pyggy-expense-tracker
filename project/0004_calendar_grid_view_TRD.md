# Technical Requirements Document (TRD) - Calendar Grid View Implementation

## 1. Overview
This document provides the technical implementation details for the calendar grid view feature as specified in the PRD. The calendar will be a read-only view showing unpaid payment due dates for the current month.

## 2. Architecture

### 2.1 Components
- **View**: `calendar_view` in `expenses/views.py`
- **Template**: `expenses/templates/expenses/calendar.html`
- **Include**: `expenses/templates/expenses/includes/calendar_grid.html`
- **CSS**: Addition to existing stylesheet

### 2.2 Data Flow
1. View fetches current month from database
2. Query unpaid items for current month
3. Check for overdue items from previous months
4. Build calendar data structure
5. Render template with calendar data

## 3. Implementation Details

### 3.1 View Implementation

```python
def calendar_view(request):
    """Display calendar grid view with payment due indicators."""
    import calendar
    from datetime import date
    
    today = date.today()
    
    try:
        current_month = Month.objects.get(year=today.year, month=today.month)
        
        # Get days with unpaid items in current month
        due_days = set(
            current_month.expense_items.filter(
                payment_date__isnull=True,
                due_date__isnull=False
            ).values_list('due_date__day', flat=True)
        )
        
        # Check if any overdue items exist from previous months
        has_overdue = ExpenseItem.objects.filter(
            payment_date__isnull=True,
            due_date__lt=today
        ).exclude(
            month=current_month
        ).exists()
        
        # Add today to due_days if there are overdue items
        if has_overdue and today.month == current_month.month and today.year == current_month.year:
            due_days.add(today.day)
    except Month.DoesNotExist:
        current_month = None
        due_days = set()
    
    # Build calendar weeks (Monday start)
    cal = calendar.monthcalendar(today.year, today.month)
    # Rotate to start week on Monday
    for week in cal:
        week[:] = week[-1:] + week[:-1]
    
    context = {
        'month': current_month,
        'calendar_weeks': cal,
        'due_days': due_days,
        'today': today,
        'month_name': calendar.month_name[today.month],
        'year': today.year,
    }
    
    return render(request, 'expenses/calendar.html', context)
```

### 3.2 URL Configuration

Add to `expenses/urls.py`:
```python
path('calendar/', views.calendar_view, name='calendar'),
```

### 3.3 Template Implementation

**calendar.html**:
```django
{% extends "expenses/base.html" %}

{% block title %}Calendar - {% if month %}{{ month.year }}-{{ month.month|stringformat:"02d" }}{% else %}{{ year }}-{{ today.month|stringformat:"02d" }}{% endif %}{% endblock %}

{% block content %}
<div class="content-header">
    <h1><i class="fas fa-calendar-days"></i> Calendar View</h1>
    <div class="header-actions">
        <a href="{% url 'dashboard' %}" class="btn btn-secondary">
            <i class="fas fa-gauge"></i> Dashboard
        </a>
    </div>
</div>

<div class="card calendar-container">
    <div class="card-header calendar-header">
        <h2>{{ month_name }} {{ year }}</h2>
    </div>
    <div class="card-body">
        {% include 'expenses/includes/calendar_grid.html' %}
    </div>
    <div class="card-footer">
        <small class="text-muted">
            <span class="calendar-indicator-legend">■</span> Payment due (including overdue)
        </small>
    </div>
</div>
{% endblock %}
```

**includes/calendar_grid.html**:
```django
<div class="calendar-grid">
    <!-- Weekday headers -->
    <div class="calendar-weekday">Mon</div>
    <div class="calendar-weekday">Tue</div>
    <div class="calendar-weekday">Wed</div>
    <div class="calendar-weekday">Thu</div>
    <div class="calendar-weekday">Fri</div>
    <div class="calendar-weekday">Sat</div>
    <div class="calendar-weekday">Sun</div>
    
    <!-- Calendar days -->
    {% for week in calendar_weeks %}
        {% for day in week %}
            {% if day == 0 %}
                <div class="calendar-day calendar-day--empty"></div>
            {% else %}
                <div class="calendar-day 
                    {% if month.year == today.year and month.month == today.month and day == today.day %}calendar-day--today{% endif %}
                    {% if day in due_days %}calendar-day--has-due{% endif %}">
                    {{ day }}
                </div>
            {% endif %}
        {% endfor %}
    {% endfor %}
</div>
```

### 3.4 CSS Implementation

The calendar uses CSS variables for comprehensive theming:

#### Layout & Structure
- CSS Grid with 7 columns for days of the week
- Subtle diagonal stripe pattern background (135deg) for empty cells
- 1px gaps between cells with muted color separators
- Responsive design that stacks vertically on mobile (<768px)
- Takes up 23% of dashboard width (2.5fr vs 0.75fr grid ratio)

#### Color Scheme & Visual Hierarchy
- **Past days**: Grayed out (60% opacity) with `--bg-secondary` background
- **Today**: Dark purple background (`#5849a6`) with prominent styling
- **Future weekdays**: Light purple tint (`rgba(88, 73, 166, 0.25)`)
- **Future weekends**: Darker purple tint (`rgba(50, 40, 100, 0.5)`) for distinction

#### Headers
- **Regular weekday headers**: Standard background (`--bg-secondary`)
- **Weekend headers**: Lighter background (`--bg-tertiary`)
- **Current weekday header**: Purple highlight matching today's cell

#### Payment Indicators (6px circles in top-right corner)
- **Green dot**: Future payments due (`--color-green`)
- **Orange dot**: Payments due today (`--color-orange`)
- **Bright red dot**: Overdue payments (`#ff2020`)

#### Interactive Elements
- Hover effects with scale transform and color changes
- Smooth transitions (0.2s) for all interactions
- Today's cell scales to 110% on hover

/* Responsive Design */
@media (max-width: 768px) {
    .calendar-day {
        font-size: 0.875rem;
    }
    
    .calendar-weekday {
        font-size: 0.75rem;
        padding: 0.25rem;
    }
    
    .calendar-container {
        max-width: 100%;
    }
}

@media (max-width: 480px) {
    .calendar-grid {
        gap: 1px;
        padding: 1px;
    }
    
    .calendar-day {
        font-size: 0.75rem;
    }
}
```

### 3.5 Navigation Update

Update `expenses/templates/expenses/base.html` navigation section:
```django
<div class="nav-actions">
    <a href="{% url 'dashboard' %}" class="btn btn-icon" title="View Dashboard" aria-label="Go to Dashboard"><i class="fas fa-tachometer-alt"></i></a>
    <a href="{% url 'calendar' %}" class="btn btn-icon" title="View Calendar" aria-label="View Calendar"><i class="fas fa-calendar-days"></i></a>
    <a href="{% url 'expense_list' %}" class="btn btn-icon" title="View Expenses" aria-label="View Expenses List"><i class="fas fa-receipt"></i></a>
    <!-- ... other links ... -->
</div>
```

## 4. Database Queries

The implementation uses two efficient queries:
1. **Current month unpaid items**: Single query with day extraction
2. **Overdue check**: Single exists() query for previous months

Total database hits: 2 (plus 1 for month retrieval)

## 5. Performance Considerations

- No JavaScript = instant interactivity
- Minimal CSS = fast rendering
- Server-side only = no client processing
- Efficient queries = fast data retrieval
- Small payload = quick page load

## 6. Browser Compatibility

- CSS Grid supported in all modern browsers
- Aspect-ratio supported in browsers from 2021+
- Fallback: Calendar still functional without aspect-ratio
- No JavaScript = maximum compatibility

## 7. Testing Checklist

### 7.1 Functional Tests
- [ ] Calendar displays current month correctly
- [ ] Week starts on Monday
- [ ] Days with unpaid items show orange indicator
- [ ] Today's date has cyan border
- [ ] Overdue items cause today to be marked
- [ ] Empty cells for days outside month
- [ ] Calendar renders when no month exists

### 7.2 Visual Tests
- [ ] Dark theme consistency
- [ ] Mobile responsive layout
- [ ] Readable on small screens
- [ ] Proper spacing and alignment

### 7.3 Edge Cases
- [ ] Months with 28, 29, 30, 31 days
- [ ] First day of month on different weekdays
- [ ] No unpaid items (empty indicators)
- [ ] All days have unpaid items
- [ ] No month created yet (first time use)

## 8. Implementation Steps

1. Add view function to `expenses/views.py`
2. Create template files
3. Add CSS to existing stylesheet
4. Update URL configuration
5. Add navigation link
6. Test implementation

## 9. Future Considerations

While out of scope for MVP, the following could be added later:
- Month navigation (previous/next)
- Click for day details
- Different indicators for different payment types
- Calendar widget on dashboard

## 10. Acceptance Criteria

- [x] Calendar shows current month in grid format
- [x] Week starts on Monday
- [x] Days with unpaid items are visually indicated
- [x] Overdue items show on today's date
- [x] Today's date is highlighted
- [x] Mobile responsive design
- [x] No JavaScript required
- [x] Integrates with existing navigation
- [x] Handles case when no month exists
