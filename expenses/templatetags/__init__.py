"""Template tags package for expense tracking application.

Import all template tag modules to ensure they are registered with Django.
"""

from . import currency  # noqa: F401
from . import currency_symbol  # noqa: F401
from . import format_amount  # noqa: F401
from . import amount_with_class  # noqa: F401
from . import create_date  # noqa: F401
