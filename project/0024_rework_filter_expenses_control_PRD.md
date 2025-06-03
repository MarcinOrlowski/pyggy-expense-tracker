# Product Requirements Document (PRD)

## Ticket #0024: Rework Filter Expenses Control to Take One Line Only

### 1. Overview

This enhancement aims to optimize the expense filter interface by consolidating all filter controls into a single, compact horizontal line, improving screen space utilization and user experience.

### 2. Problem Statement

The current expense filter implementation uses excessive vertical space due to:

- Card wrapper with dedicated header "Filter Expenses"
- Multi-row layout with filters and buttons on separate lines
- Unnecessary padding and margins from card component
- Total vertical footprint of approximately 120px for a simple filter function

### 3. Goals and Objectives

- **Primary Goal**: Reduce the filter interface to a single horizontal line
- **Secondary Goals**:
  - Maintain all existing filtering functionality
  - Preserve visual consistency with the application's dark theme
  - Improve user experience with quicker access to filters
  - Optimize screen real estate, especially for users with limited vertical space

### 4. Proposed Solution

#### 4.1 Visual Design

- Remove card wrapper and "Filter Expenses" header completely
- Arrange all filter elements in a single horizontal line:
  - "Expense Type" label and dropdown
  - "Payee" label and dropdown  
  - Filter button
  - Clear button
- Maintain consistent spacing between elements
- Keep existing dark theme styling with purple/cyan color scheme

#### 4.2 Layout Structure

<<<<<<< HEAD
```text
=======
```
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629
[Expense Type: ▼] [Payee: ▼] [🔍 Filter] [🧹 Clear]
```

#### 4.3 Responsive Behavior

- Desktop/Tablet (>768px): All elements on single line
- Mobile (<768px): Stack elements in a logical order to prevent horizontal overflow
- Maintain touch-friendly spacing on mobile devices

### 5. User Stories

1. **As a user**, I want to see more expense entries on my screen without scrolling, so I can quickly review my expenses.
2. **As a user**, I want quick access to filtering options without visual clutter, so I can efficiently find specific expenses.
3. **As a mobile user**, I want the filter controls to adapt to my screen size while remaining functional.

### 6. Functional Requirements

1. **Filter Functionality**
   - Maintain existing filter logic for Expense Type and Payee
   - Preserve "All Types" and "All Payees" default options
   - Keep current form submission behavior

2. **Visual Requirements**
   - Single-line layout for desktop/tablet views
   - Inline labels with dropdowns
   - Consistent button styling with existing application theme
   - No card wrapper or separate header

3. **Interactive Requirements**
   - Filter button submits the form with selected criteria
   - Clear button resets filters and redirects to unfiltered list
   - Dropdown selections persist after filtering

### 7. Non-Functional Requirements

1. **Performance**: No degradation in page load or filter execution time
2. **Accessibility**: Maintain proper form labels and ARIA attributes
3. **Browser Compatibility**: Support all currently supported browsers
4. **Code Quality**: Clean, maintainable CSS with proper class naming

### 8. Technical Constraints

- Must work within existing Django template structure
- Utilize existing SCSS compilation workflow
- Maintain compatibility with current form handling in views.py
- No JavaScript required for basic functionality

### 9. Success Criteria

1. Filter controls occupy only one horizontal line on desktop/tablet
2. All filtering functionality remains intact
3. Visual consistency with application theme is maintained
4. Responsive behavior works correctly on all screen sizes
5. Vertical space savings of at least 60% compared to current implementation

### 10. Out of Scope

- Changes to filter logic or behavior
- Additional filter fields
- JavaScript enhancements
- Changes to other parts of the expense list page

### 11. Mockup/Wireframe

**Current State:**

<<<<<<< HEAD
```text
=======
```
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629
┌─────────────────────────────────────┐
│ Filter Expenses                     │
├─────────────────────────────────────┤
│ Expense Type: [All Types    ▼]     │
│ Payee:        [All Payees   ▼]     │
│                                     │
│ [Filter] [Clear]                    │
└─────────────────────────────────────┘
```

**Proposed State:**

<<<<<<< HEAD
```text
=======
```
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629
Expense Type: [All Types ▼] Payee: [All Payees ▼] [Filter] [Clear]
```

### 12. Risks and Mitigation

- **Risk**: Layout might break on very small screens
  - **Mitigation**: Implement proper responsive stacking for mobile
- **Risk**: Inline layout might feel cramped
  - **Mitigation**: Careful spacing and testing across devices

### 13. Dependencies

- No external dependencies
- Uses existing Font Awesome icons
- Leverages current SCSS structure

### 14. Timeline

- Estimated implementation time: 2-3 hours
- Testing and refinement: 1 hour
