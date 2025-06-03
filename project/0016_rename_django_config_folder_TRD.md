# Rename Django Config Folder TRD

**Last Updated**: 2025-02-06
**Ticket**: [Rename expense_tracker Django config folder to match PyGGy project name](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/16)
**PRD Reference**: 0016_rename_django_config_folder_PRD.md

## Technical Approach

We'll rename the Django configuration directory from `expense_tracker/` to `pyggy/` using a systematic find-and-replace approach. This involves updating all Python module references in 5 core files and the README documentation. The changes are straightforward string replacements with no architectural modifications or database migrations required.

## Data Model

No changes to data model - this is purely a module naming change.

## Implementation Details

### Files to Modify:

1. **Directory Rename**
   - `mv expense_tracker/ pyggy/`

2. **Python Module Updates**

   ```python
   # manage.py
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyggy.settings')
   
   # pyggy/settings.py
   ROOT_URLCONF = 'pyggy.urls'
   WSGI_APPLICATION = 'pyggy.wsgi.application'
   
   # pyggy/wsgi.py
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyggy.settings')
   
   # pyggy/asgi.py
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyggy.settings')
   ```

3. **Documentation Updates**
   - Update README.md directory structure section
   - Update comments in Python files referencing project name

## Security & Performance

- Security: No impact - only module naming changes
- Performance: No impact - identical code execution
- Deployment: Requires restart of Django application

## Technical Risks & Mitigations

1. **Risk**: Missed references causing import errors → **Mitigation**: Comprehensive grep search before and after changes
2. **Risk**: Development environment confusion → **Mitigation**: Clear commit message and immediate team notification
3. **Risk**: Cached .pyc files with old imports → **Mitigation**: Delete all .pyc files and **pycache** directories

## Implementation Plan

- Step 1 (S): Rename directory - 1 minute
- Step 2 (S): Update Python module references in 5 files - 5 minutes
- Step 3 (S): Update README.md documentation - 2 minutes
- Step 4 (S): Test server startup and basic functionality - 5 minutes
- Step 5 (S): Clean up .pyc files and verify no old references - 2 minutes

Dependencies: None

## Monitoring & Rollback

- Feature flag: Not applicable for this change
- Key metrics: Server startup success, no ImportError exceptions
- Rollback: Simple git revert of the commit if any issues arise
