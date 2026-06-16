"""Domain modules — deep modules with narrow interfaces.

OrderState: order lifecycle state machine
require:    unified auth decorator
"""

from .order_state import OrderState
from .auth import require
