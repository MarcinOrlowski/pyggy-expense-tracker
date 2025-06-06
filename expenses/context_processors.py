import os
import sys
from .models import Budget


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
