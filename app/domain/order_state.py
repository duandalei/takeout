"""Order lifecycle state machine.

Deep module — a single narrow interface for all order and delivery
state transitions.  Replaces the hardcoded dict that lived inside
the order route handler and the ad-hoc status checks in delivery routes.
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class TransitionResult:
    """Returned by OrderState.transition() — the outcome of a state change request."""
    ok: bool
    new_status: Optional[str] = None
    error: Optional[str] = None


class OrderState:
    """Order lifecycle state machine.

    Single interface for all order/delivery transitions.  Callers only
    need to know the current order, the action name, and who is acting.
    All validation, guard logic, and status resolution lives behind this seam.

    Usage:
        result = OrderState.transition(order, 'confirm', actor)
        if result.ok:
            order.status = result.new_status
            db.session.commit()
        else:
            flash(result.error, 'warning')
    """

    # Maps (current_status, action) → new_status
    TRANSITIONS = {
        # Order intake / preparation
        ('pending',    'confirm'): 'confirmed',
        ('pending',    'cancel'):  'cancelled',
        ('confirmed',  'prepare'): 'preparing',
        ('confirmed',  'cancel'):  'cancelled',
        ('preparing',  'ready'):   'ready',
        # Delivery phase (was a separate table / state machine)
        ('ready',      'assign'):  'assigned',
        ('assigned',   'pickup'):  'picked_up',
        ('picked_up',  'deliver'): 'delivered',
    }

    # Who is allowed to perform each action
    ROLE_GUARDS = {
        'confirm': {'merchant'},
        'prepare': {'merchant'},
        'ready':   {'merchant'},
        'cancel':  {'customer', 'merchant'},
        'assign':  {'rider'},
        'pickup':  {'rider'},
        'deliver': {'rider'},
    }

    # Actions that require the merchant to own the order's restaurant
    MERCHANT_OWNERSHIP_ACTIONS = {'confirm', 'prepare', 'ready'}

    # Actions that require the customer to own the order
    CUSTOMER_OWNERSHIP_ACTIONS = {'cancel'}

    # Actions that require the rider to be assigned to the order
    RIDER_OWNERSHIP_ACTIONS = {'pickup', 'deliver'}

    # Status → Chinese display label
    STATUS_LABELS = {
        'pending':    '待处理',
        'confirmed':  '已确认',
        'preparing':  '备餐中',
        'ready':      '待取餐',
        'assigned':   '配送中',
        'picked_up':  '已取餐',
        'delivered':  '已送达',
        'cancelled':  '已取消',
    }

    # Actions that are side-effect triggers (caller handles after transition)
    SIDE_EFFECT_ACTIONS = {
        'assign':  'rider_assigned',
        'pickup':  'rider_picked_up',
        'deliver': 'rider_delivered',
    }

    ALL_STATUSES = [
        'pending', 'confirmed', 'preparing', 'ready',
        'assigned', 'picked_up', 'delivered', 'cancelled',
    ]

    @classmethod
    def transition(cls, order, action: str, actor: dict) -> TransitionResult:
        """Attempt to apply `action` to `order` on behalf of `actor`.

        Args:
            order: an Order model instance with .status, .customer_id,
                   .restaurant_id, .rider_id.
            action: the action name (e.g. 'confirm', 'cancel', 'pickup').
            actor: a dict with keys 'user_id' and 'role'.

        Returns:
            TransitionResult — .ok is True if the transition is valid.
        """
        # 1. Validate action exists
        if action not in cls.ROLE_GUARDS:
            return TransitionResult(ok=False, error=f'无效操作: {action}')

        # 2. Check role guard
        actor_role = actor.get('role', '')
        if actor_role not in cls.ROLE_GUARDS[action]:
            return TransitionResult(ok=False, error='无权操作')

        # 3. Check state transition validity
        key = (order.status, action)
        new_status = cls.TRANSITIONS.get(key)
        if new_status is None:
            return TransitionResult(
                ok=False,
                error=f'当前订单状态为「{cls.status_label(order.status)}」，无法执行此操作',
            )

        # 4. Resource ownership checks
        actor_id = actor.get('user_id')

        if action in cls.MERCHANT_OWNERSHIP_ACTIONS:
            # Merchant must own the restaurant that received this order
            if not cls._check_merchant_owns(order, actor_id):
                return TransitionResult(ok=False, error='无权操作此订单')

        if action in cls.CUSTOMER_OWNERSHIP_ACTIONS and actor_role == 'customer':
            if order.customer_id != actor_id:
                return TransitionResult(ok=False, error='无权操作此订单')

        if action in cls.RIDER_OWNERSHIP_ACTIONS:
            if order.rider_id != actor_id:
                return TransitionResult(ok=False, error='无权操作此配送')

        if action == 'assign':
            if order.rider_id is not None:
                return TransitionResult(ok=False, error='此订单已被其他骑手接单')

        return TransitionResult(ok=True, new_status=new_status)

    @classmethod
    def allowed_actions(cls, order, actor: dict) -> List[str]:
        """Return the list of action names that `actor` can perform on `order` right now.

        Useful for templates that render conditional action buttons.
        """
        allowed = []
        for action in cls.ROLE_GUARDS:
            result = cls.transition(order, action, actor)
            if result.ok:
                allowed.append(action)
        return allowed

    @classmethod
    def status_label(cls, status: str) -> str:
        """Chinese display label for a status code."""
        return cls.STATUS_LABELS.get(status, status)

    @classmethod
    def side_effect(cls, action: str) -> Optional[str]:
        """Return the side-effect key if `action` triggers one, else None."""
        return cls.SIDE_EFFECT_ACTIONS.get(action)

    # ── internal helpers ────────────────────────────────────────

    @staticmethod
    def _check_merchant_owns(order, user_id: int) -> bool:
        """Check that user_id owns the restaurant attached to this order."""
        from app.models import Restaurant
        restaurant = Restaurant.query.filter_by(owner_id=user_id).first()
        if not restaurant:
            return False
        return order.restaurant_id == restaurant.restaurant_id
