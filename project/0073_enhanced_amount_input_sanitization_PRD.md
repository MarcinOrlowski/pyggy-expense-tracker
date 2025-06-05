# Enhanced Amount Input Sanitization PRD

**Ticket**: [Enhanced amount input sanitization with international format support](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/73)

## Problem Statement

Users in locales where comma is the standard decimal separator must manually convert their inputs to
dot notation when entering expense amounts. Copy-pasted amounts with formatting characters (spaces,
currency symbols, thousand separators) require manual cleanup before entry. This creates friction in
data entry and may lead to user errors or abandonment of expense logging.

## Solution Overview

Implement intelligent input sanitization that accepts both comma and dot as decimal separators while
automatically removing common formatting characters from copy-pasted amounts. The system will
transparently convert all inputs to the standard dot notation for database storage, maintaining data
consistency while providing a user-friendly input experience.

## User Stories

1. As a user from a comma-decimal locale, I want to enter "10,50" as an amount, so that I can use my
   natural number format without conversion
1. As a user copying amounts from bank statements, I want to paste "€ 1 234,56" and have it
   automatically cleaned to "1234.56", so that I don't need to manually format the input
1As a user entering dollar amounts, I want to paste "$1,234.56" and have it work correctly, so
   that thousand separators don't break my input
1As a user making a mistake, I want clear feedback when my input is invalid, so that I understand
   what format is expected

## Acceptance Criteria

- [ ] System accepts both comma (`,`) and dot (`.`) as valid decimal separators
- [ ] Input sanitization removes spaces, currency symbols ($, €, zł, zl), and handles thousand separators
- [ ] Examples work correctly: "10,50" → "10.50", "1 234,56" → "1234.56", "$1,234.56" → "1234.56", "12,34 zł" → "12.34", "34,1 zł" → "34.1"
- [ ] Browser validation does not interfere with sanitization (uses text input instead of number input)
- [ ] Database storage remains consistent using dot notation for all decimal values
- [ ] Validation provides clear error messages for invalid input formats
- [ ] Existing dot notation inputs continue to work without changes (backwards compatibility)
- [ ] Sanitization works on all amount fields: expense amounts, budget initial amounts

## Out of Scope

- Locale-specific display formatting (showing amounts back to users in their preferred format)
- Currency conversion or multi-currency support
- Advanced number formatting beyond basic sanitization
- Input field localization beyond decimal separator support
- Historical data migration or conversion

## Success Metrics

1. Users can successfully enter comma-decimal amounts without validation errors
2. Copy-paste operations with formatted amounts work without manual cleanup
3. No regression in existing dot-notation input functionality
