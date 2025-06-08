# Universal Development Helper Script TRD

**Ticket**: [Create universal development helper script for containerized and local workflows](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/181)
**PRD Reference**: 0181_create_universal_development_helper_script_PRD.md

## Technical Approach

We'll implement a single bash script (`dev.sh`) that acts as a command dispatcher, detecting the
environment (Docker containers vs local venv) and routing commands to appropriate implementations.
The script will use bash functions for modularity, colored output for better UX, and proper error
handling with exit codes. Environment detection will check for Docker availability, running
containers, and virtual environment presence to automatically choose the best execution method.

## Script Architecture

```bash
dev.sh
├── Environment Detection
│   ├── is_docker_available()
│   ├── is_container_running()
│   └── has_venv() / activate_venv()
├── Command Categories
│   ├── Container Management (start, stop, restart, status, logs, shell)
│   ├── Development Tasks (lint, test, scss, static)
│   ├── Database Operations (migrate, seed, reset-db)
│   └── Development Servers (serve, serve-local, serve-container)
└── Utilities (clean, setup, help)
```

## Command Mapping

| Command | Container Mode | Local Mode |
|---------|---------------|------------|
| `lint` | `docker-compose exec web mypy` + `markdownlint` | `flake8` + `markdownlint` |
| `test` | `docker-compose exec web python manage.py test` | `unittest` + `pytest` + `flake8` |
| `scss` | `docker-compose exec web python compile_scss.py` | `python compile_scss.py` |
| `migrate` | `docker-compose exec web python manage.py migrate` | `python manage.py migrate` |
| `serve` | Auto-detect and inform container running | Full local server setup |

## Security & Performance

- **Input validation**: Command whitelist prevents arbitrary command execution
- **Error handling**: All functions return proper exit codes with error messages
- **Performance**: Direct command execution, no additional overhead beyond environment detection
- **Permissions**: Script requires executable permissions, inherits user's Docker/Python permissions

## Technical Risks & Mitigations

1. **Risk**: Docker commands fail if daemon not running → **Mitigation**: Docker availability check
   with clear error messages
1. **Risk**: Virtual environment activation fails → **Mitigation**: Explicit venv validation and
   setup instructions
1. **Risk**: Script becomes complex and hard to maintain → **Mitigation**: Modular function design
   with clear separation of concerns

## Implementation Plan

- **Phase 1** (M): Core script structure + environment detection + help system - 2 hours
- **Phase 2** (M): Container management functions (start, stop, restart, status, logs, shell) - 1 hour
- **Phase 3** (M): Development tasks (lint, test, scss, static) with dual mode support - 1 hour
- **Phase 4** (S): Database operations (migrate, seed, reset-db) - 30 minutes
- **Phase 5** (S): Development servers + utility functions - 30 minutes
- **Phase 6** (S): Testing and validation with both environments - 1 hour

Dependencies: None (uses existing Docker, Python, and bash installations)

## Monitoring & Rollback

- **Feature flag**: Not applicable (script-based tool)
- **Key metrics**: Script execution success rate, command completion time
- **Rollback**: Keep existing scattered scripts for backward compatibility; developers can continue
  using old scripts if needed
- **Validation**: Test all commands in both container and local modes before deployment
