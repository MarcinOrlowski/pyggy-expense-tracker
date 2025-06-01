# Product Requirements Document (PRD) - Calendar Grid View for Expense Tracker

## 1. Overview
This document outlines the requirements for adding a calendar grid view feature to the Python Expense Tracker application. The calendar will provide a visual representation of unpaid items due for the current month.

## 2. Problem Statement
Currently, users can only view expense items in a list/table format. There's no visual way to see payment due dates distributed across a month, making it difficult to quickly identify:
- Which days have payments due
- Whether there are overdue payments from previous months
- The overall distribution of payment obligations throughout the month

## 3. Objectives
- Provide a visual calendar grid view for the current month
- Display which days have unpaid items due
- Show overdue items from previous months on today's date
- Maintain consistency with existing UI/UX patterns
- Ensure mobile responsiveness

## 4. User Stories
1. **As a user**, I want to see a calendar view of the current month so I can quickly identify which days have payments due.
2. **As a user**, I want to see overdue payments from previous months indicated on today's date.
3. **As a mobile user**, I want the calendar to be responsive and usable on smaller screens.
4. **As a user**, I want the calendar to respect my theme preference (dark theme).

## 5. Functional Requirements

### 5.1 Calendar Display
- Display current month in a traditional 7-day grid format
- Week starts on Monday
- Show header in "Calendar - YYYY-MM" format
- Include day names (Mon-Sun) as column headers
  - Weekend headers (Sat/Sun) have lighter background
  - Current weekday header highlighted with purple background
- Show all days of the month with proper week alignment
- Empty cells for days outside current month show subtle diagonal stripe pattern
- Widget incorporated into Dashboard page (23% width in 77%-23% split)
- Visual hierarchy for different day types:
  - Past days: Grayed out with reduced opacity
  - Today: Dark purple background with light text
  - Future weekdays: Light purple tint
  - Future weekends: Darker purple tint for visual distinction

### 5.2 Payment Indicators
- **Future Due Payments**: Green dot indicator for payments due in future days
- **Due Today**: Orange dot indicator for payments due on current day
- **Overdue Payments**: Bright red dot indicator for past days with unpaid items
- **Overdue from Previous Months**: Overdue items from previous months show on today's date
- **Current Day Highlight**: Today's date has dark purple background
- **No Payment Status**: No indicators for paid items or payment dates

### 5.3 Interactivity
- None - calendar is read-only display
- No click functionality on calendar days
- No popups or modals

### 5.4 Navigation
- Calendar view accessible from main navigation
- Shows current month only
- No month navigation in MVP

## 6. Non-Functional Requirements

### 6.1 Design & UX
- Consistent with existing Dracula-inspired dark theme
- Use existing color palette (purple/cyan accents)
- Follow existing card-based UI patterns
- Maintain visual hierarchy and readability

### 6.2 Performance
- Calendar should load quickly without blocking UI
- Efficient data queries to avoid N+1 problems
- Consider pagination or lazy loading for day details

### 6.3 Responsiveness
- Mobile-first approach
- Calendar grid adapts to screen sizes
- Touch-friendly interaction targets
- Readable text and indicators on small screens

### 6.4 Accessibility
- Sufficient color contrast for indicators
- Alternative text for visual indicators

## 7. Technical Considerations
- Integrate with existing Django view/template architecture
- Reuse existing Month and ExpenseItem models
- Leverage existing CSS styling patterns
- No JavaScript required - pure server-side rendering
- Minimal database queries (2 total)

## 8. MVP Scope
For the initial implementation, focus on:
1. Basic calendar grid for current month only
2. Single visual indicator for days with unpaid items due
3. Overdue items shown on today's date
4. Mobile responsive layout
5. Dark theme support
6. Read-only display (no interactivity)

## 9. Success Metrics
- User can view calendar within 2 seconds
- Calendar is usable on devices down to 320px width
- All unpaid and overdue dates are accurately represented
