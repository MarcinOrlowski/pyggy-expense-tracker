# Constants File with Automated Version Management PRD

**Ticket**: [Implement Constants File with Automated Version Management](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/160)

## Problem Statement

The application currently has hardcoded version information scattered across templates, creating version synchronization issues. The footer template displays "v1.0.0" while CHANGES.md indicates the current development version is "v1.1", leading to inconsistent version display. Manual version updates are error-prone and require remembering to update multiple locations.

## Solution Overview

Create a centralized version service that provides application version information through a clean API that can be easily extended later. Initially returns hardcoded version but designed for future automation (git tags, file parsing, environment variables). This service will be accessible throughout the application via Django context processors, ensuring consistent version display while maintaining flexibility for future enhancements.

## User Stories

1. As a developer, I want to update the application version in one place, so that it displays consistently across all templates
2. As a user, I want to see the correct current version in the footer, so that I know which version of the application I'm using
3. As a developer, I want a flexible version system, so that I can later implement automated version detection without changing calling code
4. As a maintainer, I want version synchronization between CHANGES.md and displayed version, so that releases are consistent

## Acceptance Criteria

- [ ] Version service class provides `get_version()` and `get_version_string()` methods
- [ ] Context processor makes version available in all templates via `app_version` variable
- [ ] Footer template uses centralized version instead of hardcoded "v1.0.0"
- [ ] Version service is easily extensible for future automation without breaking existing code
- [ ] All version-related code is centralized in the service layer
- [ ] Version display format matches existing "v1.0.0" pattern

## Out of Scope

- Automated version bumping from git tags or files (foundation only)
- CI/CD integration for version management
- Version comparison or compatibility checking
- Multiple version formats or environment-specific versions
- Command-line tools for version management

## Success Metrics

1. Single source of truth for version information with zero hardcoded versions in templates
2. Version synchronization issue resolved - footer displays current version within 1 development cycle
3. Service architecture enables future automation without code changes to calling components