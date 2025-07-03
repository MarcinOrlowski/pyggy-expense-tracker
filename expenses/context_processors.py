import os
import sys
from .models import Budget
from .services import VersionService


def current_budget(request):
    """Make current budget available in all templates."""
    budget_id = (
        request.resolver_match.kwargs.get("budget_id")
        if request.resolver_match
        else None
    )
    budget = None

    if budget_id:
        try:
            budget = Budget.objects.get(id=budget_id)
        except Budget.DoesNotExist:
            budget = None

    return {"current_budget": budget, "current_budget_id": budget_id}


def testing_context(request):
    """Provide testing context for templates."""
    testing = (
        "test" in sys.argv or "pytest" in sys.modules or "GITHUB_ACTIONS" in os.environ
    )
    return {"testing": testing}


def app_version_context(request):
    """Make app_version and milestone info available in all templates."""
    version_service = VersionService()
    return {
        "app_version": version_service.get_version_string(),
        "github_issues_url": version_service.get_github_issues_url(),
    }


def section_context(request):
    """Add section-specific CSS class based on URL name patterns."""
    if not request.resolver_match or not request.resolver_match.url_name:
        return {"section_class": ""}

    url_name = request.resolver_match.url_name

    # Simple mapping based on URL name prefixes
    # Order matters - more specific patterns first
    section_map = {
        "budget": "section-budgets",
        "dashboard": "section-dashboard",
        "expense_item": "section-payments",  # Must come before 'expense'
        "expense": "section-expenses",
        "month": "section-months",
        "payee": "section-payees",
        "payment_method": "section-payment-methods",
        "help": "section-help",
    }

    # Find matching section by checking URL name prefix
    for prefix, section_class in section_map.items():
        if url_name.startswith(prefix):
            return {"section_class": section_class}

    return {"section_class": ""}
