# Docker Setup Guide

This guide explains how to use Docker with the PyGGy Expense Tracker application.

## Quick Start (Development)

For local development with pre-built image:

```bash
# Clone the repository
git clone https://github.com/MarcinOrlowski/pyggy-expense-tracker.git
cd pyggy-expense-tracker

# Copy environment variables
cp .env.example .env

# Build the development image (only needed once)
docker compose build

# Start the application
docker compose up

# In another terminal, create a superuser
docker compose exec web python manage.py createsuperuser

# Load initial data (optional)
docker compose exec web python manage.py loaddata fixtures/initial_data.json
```

The application will be available at http://localhost:8000

Note: The development image is built once and cached locally as `pyggy-expense-tracker:dev`. It will be reused on subsequent runs unless you explicitly rebuild it.

## Building and Publishing Docker Image

### 1. Build the Image

```bash
# Build the image with all dependencies
docker build -t pyggy-expense-tracker:latest .

# Tag for Docker Hub (replace 'yourusername' with your Docker Hub username)
docker tag pyggy-expense-tracker:latest yourusername/pyggy-expense-tracker:latest
```

### 2. Test the Image Locally

```bash
# Run the built image
docker run -p 8000:8000 \
  -v $(pwd)/db.sqlite3:/app/db.sqlite3 \
  -e DJANGO_SECRET_KEY=your-secret-key \
  pyggy-expense-tracker:latest
```

### 3. Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Push the image
docker push yourusername/pyggy-expense-tracker:latest
```

## Using Pre-built Image

Once your image is on Docker Hub, others can use it with the `compose.prod.yml` file:

```bash
# Edit compose.prod.yml to use your image name
# Replace 'yourusername/pyggy-expense-tracker:latest' with your actual image

# Run using the pre-built image
docker compose -f compose.prod.yml up
```

## Docker Compose Files

### compose.yml (Development)
- Builds a local development image with all dependencies pre-installed
- Mounts source code for hot-reloading
- Image is built once and reused (tagged as `pyggy-expense-tracker:dev`)
- Ideal for development

### compose.prod.yml (Production/Distribution)
- Uses pre-built image from Docker Hub
- No source code mounting (except settings override)
- Faster startup
- Ideal for deployment or sharing

## Docker Files

### Dockerfile
- Production-ready image with all dependencies
- Includes static file compilation
- Suitable for Docker Hub distribution

### Dockerfile.dev
- Development image with dependencies only
- Excludes application code (mounted as volume)
- Faster rebuilds when dependencies change

## Environment Variables

Configure these in your `.env` file:

- `DJANGO_SECRET_KEY`: Django secret key (required for production)
- `DJANGO_DEBUG`: Set to `False` for production
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Volumes

The following volumes are used:

- `./db.sqlite3`: SQLite database persistence
- `./staticfiles`: Compiled static files (development only)
- `./static`: Static assets (development only)

## Common Commands

```bash
# View logs
docker compose logs -f

# Run Django management commands
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell

# Stop the application
docker compose down

# Stop and remove volumes (WARNING: deletes database)
docker compose down -v

# Rebuild image after requirements change
docker compose build --no-cache
```

## Troubleshooting

### Permission Issues
If you encounter permission issues with the database file:
```bash
# Fix permissions
chmod 666 db.sqlite3
```

### Port Already in Use
If port 8000 is already in use:
```bash
# Change the port in compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### Dependencies Not Installing
If dependencies fail to install:
```bash
# Rebuild development image without cache
docker compose build --no-cache
docker compose up
```

### Updating Dependencies
When requirements.txt changes:
```bash
# Rebuild the development image
docker compose build
docker compose up

# Or in one command
docker compose up --build
```