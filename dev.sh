#!/bin/bash

# Universal Development Helper Script for Pyggy Expense Tracker
# Supports both containerized (Docker) and local (venv) development workflows

set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Environment detection
is_docker_available() {
    command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1
}

get_main_service() {
    if ! is_docker_available; then
        return 1
    fi
    
    # Get all services from compose file
    local services
    services=$(docker compose config --services 2>/dev/null)
    
    if [[ -z "$services" ]]; then
        return 1
    fi
    
    # Prefer common main service names, fallback to first service
    for preferred in "web" "app" "django" "backend" "server"; do
        if echo "$services" | grep -q "^${preferred}$"; then
            echo "$preferred"
            return 0
        fi
    done
    
    # Fallback to first service
    echo "$services" | head -n1
}

is_container_running() {
    local main_service
    main_service=$(get_main_service)
    
    if [[ -z "$main_service" ]]; then
        return 1
    fi
    
    docker compose ps "$main_service" 2>/dev/null | grep -q "Up"
}

has_venv() {
    [[ -d "$PROJECT_ROOT/venv" ]]
}

activate_venv() {
    if has_venv; then
        if [[ -z "${VIRTUAL_ENV:-}" ]]; then
            log_info "Activating virtual environment..."
            source "$PROJECT_ROOT/venv/bin/activate"
        fi
        if [[ -z "${VIRTUAL_ENV:-}" ]]; then
            log_error "Failed to activate virtual environment"
            return 1
        fi
    else
        log_error "Virtual environment not found. Please create one with: python -m venv venv"
        return 1
    fi
}

# Help system
show_help() {
    cat << 'EOF'
Universal Development Helper Script for Pyggy Expense Tracker

USAGE:
    ./dev.sh <command> [options]

CONTAINER MANAGEMENT:
    start               Start Docker containers
    stop                Stop Docker containers  
    restart             Restart Docker containers
    rebuild             Rebuild and restart Docker containers
    status              Show container status
    logs                Show container logs
    shell               Open shell in web container

DEVELOPMENT TASKS:
    lint                Run code linting (mypy, markdownlint)
    test                Run all tests (unit tests, pytest, flake8)
    scss                Compile SCSS files
    static              Collect static files
    
DATABASE OPERATIONS:
    migrate             Run Django migrations
    seed                Load initial data fixtures
    reset-db            Reset database (migrate + seed)
    
DEVELOPMENT SERVERS:
    serve               Start development server (auto-detects env)
    serve-local         Force local development server
    serve-container     Force container development server
    
UTILITY:
    clean               Clean up temporary files and caches
    setup               Initial project setup
    help                Show this help message

EXAMPLES:
    # Quick development workflow
    ./dev.sh start && ./dev.sh migrate && ./dev.sh serve
    
    # Code quality checks
    ./dev.sh lint && ./dev.sh test
    
    # Reset and seed database
    ./dev.sh reset-db
    
    # Work with containers
    ./dev.sh start
    ./dev.sh logs
    ./dev.sh shell
    
    # Local development
    ./dev.sh serve-local

ENVIRONMENT DETECTION:
    - Auto-detects Docker and Docker Compose availability
    - Auto-detects running containers and main service name
    - Falls back to local venv when containers not available
    - Use force commands (serve-local/serve-container) to override

EOF
}

# Container management functions
container_start() {
    if ! is_docker_available; then
        log_error "Docker or docker compose not available"
        return 1
    fi
    
    log_info "Starting Docker containers..."
    docker compose up -d
    log_success "Containers started"
}

container_stop() {
    if ! is_docker_available; then
        log_error "Docker or docker compose not available"
        return 1
    fi
    
    log_info "Stopping Docker containers..."
    docker compose down
    log_success "Containers stopped"
}

container_restart() {
    container_stop
    container_start
}

container_rebuild() {
    if ! is_docker_available; then
        log_error "Docker or docker compose not available"
        return 1
    fi
    
    log_info "Rebuilding and restarting Docker containers..."
    docker compose down
    docker compose build
    docker compose up -d
    log_success "Containers rebuilt and started"
}

container_status() {
    if ! is_docker_available; then
        log_error "Docker or docker compose not available"
        return 1
    fi
    
    echo "Container Status:"
    docker compose ps
}

container_logs() {
    if ! is_docker_available; then
        log_error "Docker or docker compose not available"
        return 1
    fi
    
    log_info "Showing container logs (Ctrl+C to exit)..."
    docker compose logs -f
}

container_shell() {
    if ! is_docker_available; then
        log_error "Docker or docker compose not available"
        return 1
    fi
    
    if ! is_container_running; then
        log_error "Container is not running. Start it first with: $SCRIPT_NAME start"
        return 1
    fi
    
    local main_service
    main_service=$(get_main_service)
    log_info "Opening shell in $main_service container..."
    run_in_container bash
}

# Helper function for container commands
run_in_container() {
    local main_service
    main_service=$(get_main_service)
    
    if [[ -z "$main_service" ]]; then
        log_error "Could not determine main service from compose file"
        return 1
    fi
    
    docker compose exec "$main_service" "$@"
}

# Development task functions
task_lint() {
    if is_docker_available && is_container_running; then
        log_info "Running lint checks in container..."
        echo "mypy..."
        run_in_container mypy expenses/
        echo
        echo "markdownlint..."
        markdownlint --config .markdownlint.yaml.dist docs/*.md project/*.md README.md
    else
        log_info "Running lint checks locally..."
        activate_venv
        echo "flake8..."
        python -m flake8 expenses/
        echo "markdownlint..."
        markdownlint --config .markdownlint.yaml.dist docs/*.md project/*.md README.md
    fi
    log_success "Lint checks completed"
}

task_test() {
    if is_docker_available && is_container_running; then
        log_info "Running tests in container..."
        run_in_container python manage.py test
    else
        log_info "Running tests locally..."
        activate_venv
        echo "Unit tests..."
        python -m unittest discover --quiet
        if pip show pytest --quiet >/dev/null 2>&1; then
            pytest --quiet --no-header --no-summary
        fi
        echo "Code Lint..."
        python -m flake8 expenses/
    fi
    log_success "Tests completed"
}

task_scss() {
    log_info "Compiling SCSS files..."
    
    local scss_source="$PROJECT_ROOT/src/scss/main.scss"
    local css_output="$PROJECT_ROOT/staticfiles/scss/main.css"
    local css_map="$css_output.map"
    
    # Check if SCSS source exists
    if [[ ! -f "$scss_source" ]]; then
        log_error "SCSS source file not found: $scss_source"
        return 1
    fi
    
    # Ensure output directory exists
    mkdir -p "$(dirname "$css_output")"
    
    if is_docker_available && is_container_running; then
        log_info "Compiling SCSS in container..."
        run_in_container python -c "
import sass
from pathlib import Path

scss_source = Path('src/scss/main.scss')
css_output = Path('staticfiles/scss/main.css')

print(f'Compiling {scss_source} -> {css_output}')
try:
    result = sass.compile(
        filename=str(scss_source),
        output_style='expanded',
        source_map_filename=str(css_output) + '.map',
        source_map_root='../../src/scss/'
    )
    
    with open(css_output, 'w') as f:
        f.write(result[0])
    
    if result[1]:
        with open(str(css_output) + '.map', 'w') as f:
            f.write(result[1])
    
    print('✓ SCSS compiled successfully')
    print(f'  Output: {css_output}')
    print(f'  Size: {css_output.stat().st_size} bytes')
except Exception as e:
    print(f'✗ SCSS compilation failed: {e}')
    exit(1)
"
    else
        activate_venv
        log_info "Compiling SCSS locally..."
        python -c "
import sass
from pathlib import Path

scss_source = Path('src/scss/main.scss')
css_output = Path('staticfiles/scss/main.css')

print(f'Compiling {scss_source} -> {css_output}')
try:
    result = sass.compile(
        filename=str(scss_source),
        output_style='expanded',
        source_map_filename=str(css_output) + '.map',
        source_map_root='../../src/scss/'
    )
    
    with open(css_output, 'w') as f:
        f.write(result[0])
    
    if result[1]:
        with open(str(css_output) + '.map', 'w') as f:
            f.write(result[1])
    
    print('✓ SCSS compiled successfully')
    print(f'  Output: {css_output}')
    print(f'  Size: {css_output.stat().st_size} bytes')
except Exception as e:
    print(f'✗ SCSS compilation failed: {e}')
    exit(1)
"
    fi
    log_success "SCSS compilation completed"
}

task_static() {
    log_info "Collecting static files..."
    if is_docker_available && is_container_running; then
        run_in_container python manage.py collectstatic --noinput
    else
        activate_venv
        python manage.py collectstatic --noinput
    fi
    log_success "Static files collected"
}

# Database operations
db_migrate() {
    log_info "Running Django migrations..."
    if is_docker_available && is_container_running; then
        run_in_container python manage.py migrate
    else
        activate_venv
        python manage.py migrate
    fi
    log_success "Migrations completed"
}

db_seed() {
    log_info "Loading initial data fixtures..."
    if is_docker_available && is_container_running; then
        run_in_container python manage.py loaddata fixtures/initial_data.json
    else
        activate_venv
        python manage.py loaddata fixtures/initial_data.json
    fi
    log_success "Data seeding completed"
}

db_reset() {
    log_info "Resetting database..."
    db_migrate
    db_seed
    log_success "Database reset completed"
}

# Development server functions
serve_auto() {
    if is_docker_available && is_container_running; then
        log_info "Container detected, development server already running at http://localhost:8000"
        log_info "Use 'logs' command to see server output"
    else
        serve_local
    fi
}

serve_local() {
    log_info "Starting local development server..."
    activate_venv
    
    # Compile SCSS
    task_scss
    
    # Collect static files
    task_static
    
    # Run migrations
    db_migrate
    
    # Start development server
    log_info "Starting Django development server at http://localhost:8000..."
    python manage.py runserver 0.0.0.0:8000
}

serve_container() {
    if ! is_docker_available; then
        log_error "Docker not available"
        return 1
    fi
    
    if ! is_container_running; then
        log_info "Container not running, starting it..."
        container_start
    fi
    
    log_info "Development server running in container at http://localhost:8000"
    log_info "Use 'logs' command to see server output"
}

# Utility functions
cleanup() {
    log_info "Cleaning up temporary files and caches..."
    
    # Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # SCSS cache
    rm -rf .sass-cache/ 2>/dev/null || true
    
    # Django cache
    rm -rf staticfiles/.sass-processor/ 2>/dev/null || true
    
    log_success "Cleanup completed"
}

setup_project() {
    log_info "Setting up project for development..."
    
    # Check if venv exists, create if not
    if ! has_venv; then
        log_info "Creating virtual environment..."
        python -m venv venv
    fi
    
    # Activate venv and install dependencies
    activate_venv
    log_info "Installing Python dependencies..."
    pip install -r requirements-dev.txt
    
    # Setup database
    db_reset
    
    # Compile SCSS and collect static files
    task_scss
    task_static
    
    log_success "Project setup completed"
    log_info "You can now run: $SCRIPT_NAME serve"
}

# Main command dispatcher
main() {
    if [[ $# -eq 0 ]]; then
        show_help
        exit 0
    fi
    
    case "${1:-}" in
        # Container management
        "start")
            container_start
            ;;
        "stop")
            container_stop
            ;;
        "restart")
            container_restart
            ;;
        "rebuild")
            container_rebuild
            ;;
        "status")
            container_status
            ;;
        "logs")
            container_logs
            ;;
        "shell")
            container_shell
            ;;
            
        # Development tasks
        "lint")
            task_lint
            ;;
        "test")
            task_test
            ;;
        "scss")
            task_scss
            ;;
        "static")
            task_static
            ;;
            
        # Database operations
        "migrate")
            db_migrate
            ;;
        "seed")
            db_seed
            ;;
        "reset-db")
            db_reset
            ;;
            
        # Development servers
        "serve")
            serve_auto
            ;;
        "serve-local")
            serve_local
            ;;
        "serve-container")
            serve_container
            ;;
            
        # Utility
        "clean")
            cleanup
            ;;
        "setup")
            setup_project
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
            
        *)
            log_error "Unknown command: $1"
            echo
            echo "Run '$SCRIPT_NAME help' for usage information."
            exit 1
            ;;
    esac
}

# Change to project directory
cd "$PROJECT_ROOT"

# Run main function with all arguments
main "$@"