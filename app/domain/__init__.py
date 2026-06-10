"""Domain modules — deep modules with narrow interfaces.

OrderState:    order lifecycle state machine
Authorization: unified permission checking
"""

from .order_state import OrderState
from .auth import Authorization, require
