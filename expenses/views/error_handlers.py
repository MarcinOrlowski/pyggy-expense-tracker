from django.shortcuts import render


def custom_404(request, exception=None):
    """Custom 404 error handler that shows user-friendly error page."""
    return render(request, "404.html", status=404)
