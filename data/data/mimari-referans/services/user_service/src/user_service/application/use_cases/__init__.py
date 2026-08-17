"""Use cases: one class per application-level action.

Each use case exposes a single ``execute`` method (Single Responsibility),
receives its dependencies through the constructor and orchestrates domain
objects and ports. Business *rules* stay in the domain; use cases own the
business *flow*.
"""

from user_service.application.use_cases.get_user import GetUser
from user_service.application.use_cases.list_users import ListUsers
from user_service.application.use_cases.register_user import RegisterUser

__all__ = ["GetUser", "ListUsers", "RegisterUser"]
