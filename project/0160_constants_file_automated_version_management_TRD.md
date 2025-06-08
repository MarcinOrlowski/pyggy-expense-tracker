# Constants File with Automated Version Management TRD

**Ticket**: [Implement Constants File with Automated Version Management](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/160)
**PRD Reference**: 0160_constants_file_automated_version_management_PRD.md

## Technical Approach

We'll implement a `VersionService` class in `expenses/services/version_service.py` following
Django's service layer pattern. The service will provide version information through `get_version()`
and `get_full_version_string()` methods, initially returning hardcoded values but designed for
future automation. A Django context processor will make version data available in all templates via
an `app_version` variable, replacing the hardcoded "v1.0.0" in the footer template.

## Data Model

No database changes required. This implementation uses application-level services only.

## API Design

```python
# Version Service Interface
class VersionService:
    def get_version(self) -> str:
        """Returns semantic version (e.g., '1.1.0')"""
        
    def get_version_string(self) -> str:
        """Returns formatted version (e.g., 'v1.1.0')"""

# Context Processor Implementation
def app_version_context(request):
    """Makes app_version available in all templates"""
    return {'app_version': VersionService().get_version_string()}

# Template Usage
{{ app_version }}  # Outputs: "v1.1.0"
```

## Django Settings Configuration

```python
# pyggy/settings.py - Add to TEMPLATES context_processors:
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ... existing processors ...
                'expenses.context_processors.app_version_context',
            ],
        },
    },
]
```

## File Structure

```text
expenses/
├── services/
│   ├── __init__.py
│   └── version_service.py
├── context_processors.py (modified)
└── templates/expenses/base.html (modified)
pyggy/
└── settings.py (modified)
```

## Implementation Details

1. **VersionService**: `expenses/services/version_service.py`
   - Contains hardcoded version "1.1.0" initially
   - Extensible design for future automation

2. **Context Processor**: `expenses/context_processors.py`
   - Imports and instantiates VersionService
   - Calls `get_version_string()` method
   - Returns dict with `app_version` key

3. **Settings Registration**: `pyggy/settings.py`
   - Add context processor to TEMPLATES configuration

4. **Template Update**: `expenses/templates/expenses/base.html:78`
   - Replace hardcoded "v1.0.0" with `{{ app_version }}`

## Security & Performance

- No external dependencies or network calls required
- Context processor called once per template render (minimal overhead)
- Version service can be cached if future automation requires expensive operations
- No sensitive data exposed through version service

## Technical Risks & Mitigations

1. **Risk**: Context processor adds overhead to every template render → **Mitigation**: Lightweight
   service with no I/O operations, cached result if needed
1. **Risk**: Future automation might require file I/O on every request → **Mitigation**: Service
   design supports caching strategies and lazy loading

## Implementation Plan

- Phase 1 (S): Create VersionService class with hardcoded version "1.1.0" - 30 min
- Phase 2 (S): Create/update context processor to use version service - 15 min
- Phase 3 (S): Register context processor in Django settings - 10 min
- Phase 4 (S): Update base.html template to use {{ app_version }} - 15 min
- Phase 5 (S): Test version display across application - 15 min
- Phase 6 (S): Update CHANGES.md with implementation notes - 15 min

Dependencies: None

## Monitoring & Rollback

- Feature flag: Not required (low risk change)
- Key metrics: Version display consistency in footer template
- Rollback: Revert template change to hardcoded "v1.0.0" and remove context processor if issues arise
- Testing: Verify {{ app_version }} renders correctly in all page templates
