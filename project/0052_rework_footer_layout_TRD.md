# Footer Layout Rework TRD

**Last Updated**: 2025-02-06
**Ticket**: [Rework footer layout with split design](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/52)
**PRD Reference**: 0052_rework_footer_layout_PRD.md

## Technical Approach

We'll modify the existing footer in `base.html` to use flexbox layout with two sections (left and
right), updating the SCSS in `_components.scss` to support responsive behavior. The application
version will be hardcoded initially (v1.0.0) in the template. We'll use CSS media queries to stack
footer sections vertically on mobile devices (<768px).

## Data Model

No data model changes required - this is a pure frontend UI enhancement.

## API Design

Not applicable - this is a static UI component with no backend interaction.

## Implementation Details

### HTML Structure (`expenses/templates/expenses/base.html`)

```html
<footer>
    <div class="container">
        <div class="footer-content">
            <div class="footer-left">
                <p>&copy; 2025 Pyggy Expense Tracker</p>
                <p class="version">Version 1.0.0</p>
            </div>
            <div class="footer-right">
                <a href="https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues" target="_blank" rel="noopener">Report Issue</a>
                <span class="separator">|</span>
                <a href="https://github.com/MarcinOrlowski/pyggy-expense-tracker/" target="_blank" rel="noopener">GitHub</a>
            </div>
        </div>
    </div>
</footer>
```

### CSS Changes (`src/scss/_components.scss`)

- Add `.footer-content` with `display: flex` and `justify-content: space-between`
- Style `.footer-left` and `.footer-right` sections
- Add `.version` with smaller, muted text styling
- Add `.separator` for visual separation between links
- Media query at 768px breakpoint for mobile stacking

## Security & Performance

- Links include `rel="noopener"` for security when opening in new tabs
- No JavaScript required - pure CSS solution for performance
- Minimal CSS additions (~20 lines) with no impact on page load

## Technical Risks & Mitigations

1. **Risk**: Footer height change might affect page layout → **Mitigation**: Test with various content lengths to ensure `margin-top: auto` still works
2. **Risk**: Long version strings might break layout → **Mitigation**: Use `text-overflow: ellipsis` for version text

## Implementation Plan

- Phase 1 (S): Update HTML structure in base.html - 30 min
- Phase 2 (S): Add SCSS styles for desktop layout - 30 min
- Phase 3 (S): Add responsive media queries - 30 min
- Phase 4 (S): Test on various screen sizes - 30 min

Dependencies: None - uses existing CSS variables and container styles

## Monitoring & Rollback

- Feature flag: Not required for CSS-only change
- Key metrics: Visual regression testing on footer appearance
- Rollback: Git revert of the commit if any issues arise
