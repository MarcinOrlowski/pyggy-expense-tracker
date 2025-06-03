# Docker Configuration for Development TRD

**Last Updated**: 2025-02-06
**Ticket**: [Add Docker configuration for development and production environments](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/26)
**PRD Reference**: 0026_docker_configuration_PRD.md

## Technical Approach

We'll create a multi-stage Dockerfile optimized for development with Python 3.12 base image, implementing a compose.yml file that orchestrates the Django application with volume mounts for hot-reloading. The setup will handle static files through Django's collectstatic and SCSS compilation via the existing compile_scss.py script. Environment variables will be managed through .env files with compose.yml variable substitution.

## Data Model

No database schema changes required. SQLite database file will be mounted as a Docker volume at `/app/db.sqlite3` to ensure persistence across container restarts.

## API Design

Not applicable - this is infrastructure configuration only.

## Security & Performance

- Secret key: Loaded from environment variable `DJANGO_SECRET_KEY`
- Debug mode: Controlled via `DJANGO_DEBUG` environment variable (default: True for development)
- Allowed hosts: Configurable via `DJANGO_ALLOWED_HOSTS` environment variable
- Container runs as non-root user (uid 1000)
- Development server bound to 0.0.0.0:8000 for container accessibility

## Technical Risks & Mitigations

1. **Risk**: SCSS compilation might fail in container → **Mitigation**: Install libsass dependencies in Dockerfile
2. **Risk**: File permissions conflicts on mounted volumes → **Mitigation**: Match container user UID with host user
3. **Risk**: Static files not served correctly → **Mitigation**: Run collectstatic on container startup

## Implementation Plan

- Phase 1 (S): Create Dockerfile with multi-stage build - 1 hour
- Phase 2 (S): Create compose.yml with service configuration - 1 hour
- Phase 3 (S): Add .env.example and environment handling - 30 minutes
- Phase 4 (S): Update README with Docker instructions - 30 minutes
- Phase 5 (S): Test full development workflow - 1 hour

Dependencies: None

## Monitoring & Rollback

- Feature flag: Not required - opt-in by using Docker commands
- Key metrics: Container startup time, development server response time
- Rollback: Developers can use existing `run.sh` script if Docker issues arise
