# Rename Django Config Folder PRD

**Last Updated**: 2025-02-06
**Ticket**: [Rename expense_tracker Django config folder to match PyGGy project name](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/16)

## Problem Statement

The project has been renamed from "Expense Tracker" to "PyGGy", but the Django configuration directory is still named `expense_tracker`. This creates confusion for developers as the project name and configuration directory name don't match. New developers expect the main configuration to match the project name.

## Solution Overview

Rename the Django configuration directory from `expense_tracker` to `pyggy` to match the project name. Update all references throughout the codebase to use the new module name. This creates consistency between the project name and its configuration structure, making the codebase more intuitive.

## User Stories

1. As a developer, I want the Django config folder to match the project name, so that I can navigate the codebase intuitively
2. As a new contributor, I want consistent naming conventions, so that I can understand the project structure quickly
3. As a maintainer, I want clear project organization, so that I can onboard new developers efficiently

## Acceptance Criteria

- [ ] Django configuration directory renamed from `expense_tracker/` to `pyggy/`
- [ ] All Python imports updated to reference `pyggy` instead of `expense_tracker`
- [ ] Application starts successfully with `python manage.py runserver`
- [ ] All Django management commands work correctly (migrate, collectstatic, etc.)
- [ ] No broken imports or module reference errors
- [ ] Docker configurations updated to use new module path

## Out of Scope

- Renaming the `expenses/` app directory
- Changing any functionality or business logic
- Updating deployment configurations beyond Docker
- Modifying database content or structure
- Changing the project repository name

## Success Metrics

1. Zero import errors after deployment
2. All existing tests pass without modification
3. Development server starts within 5 seconds
