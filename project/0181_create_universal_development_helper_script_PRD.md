# Universal Development Helper Script PRD

**Ticket**: [Create universal development helper script for containerized and local workflows](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/181)

## Problem Statement

Developers and AI agents currently struggle with scattered development scripts (lint.sh, test.sh,
run_dev.sh) and inconsistent workflows between containerized and local development. This creates
confusion, slows down development, and makes it harder for new team members and automated tools to
effectively work with the project. The lack of a unified interface results in longer onboarding
times and potential errors when switching between development modes.

## Solution Overview

Create a single universal development helper script (`dev.sh`) that provides a unified interface for
all common development tasks. The script will auto-detect the environment (containerized vs local)
and execute appropriate commands, while providing comprehensive help documentation and examples.
Success means developers can perform any development task through one consistent interface,
regardless of their setup preference.

## User Stories

1. As a developer, I want to run any development command through a single script, so that I don't
   need to remember multiple scattered scripts
1. As an AI agent, I want clear help documentation with examples, so that I can efficiently assist
   with development tasks
1. As a new team member, I want auto-detection of my development environment, so that commands work
   regardless of whether I use Docker or local setup
1. As a developer, I want comprehensive error messages and status reporting, so that I can quickly
   diagnose and fix issues

## Acceptance Criteria

- [ ] Single script (`dev.sh`) provides access to all existing functionality (lint, test, serve, migrations, etc.)
- [ ] Script auto-detects Docker availability and running containers vs local venv setup
- [ ] Comprehensive help system shows available commands, usage examples, and explanations
- [ ] All container management operations work (start, stop, restart, status, logs, shell)
- [ ] All development tasks work in both containerized and local modes (lint, test, scss, static)
- [ ] Database operations work in both modes (migrate, seed, reset-db)
- [ ] Clear colored output with status messages (info, success, warning, error)
- [ ] Script handles errors gracefully with helpful error messages

## Out of Scope

- Advanced argument parsing beyond simple commands
- Configuration file management
- Integration with external CI/CD systems
- Custom command plugins or extensibility
- Bash completion generation
- Migration of existing scripts (they remain for backward compatibility)

## Success Metrics

1. Developers can complete common workflows using only `dev.sh` within 1 week of deployment
2. All existing script functionality remains accessible through the new interface
3. Zero increase in development task execution time compared to current scattered scripts
