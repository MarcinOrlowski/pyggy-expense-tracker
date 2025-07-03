# Production Dockerfile for PyGGy Expense Tracker
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p staticfiles static/css && \
    chown -R appuser:appuser staticfiles static

# Switch to non-root user
USER appuser

# Compile SCSS and collect static files
RUN ./dev.sh scss && \
    python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Default command for production
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
