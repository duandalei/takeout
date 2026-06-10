"""Authorization seam.

Deep module with one narrow interface: `require(role=..., owns=...)`.
Replaces the scattered pattern of @login_required + @role_required(...)
+ inline ownership queries that was repeated across 4 route files.

Usage:
    @require(role='merchant', owns='restaurant')
    def some_route(id):
        # g.current_restaurant is already resolved
        ...

    @require()                # just requires login
    @require(role='rider')    # requires login + rider role
"""

from functools import wraps
from flask import session, request, redirect, url_for, flash, g


class Authorization:
    """Single seam for all authorization checks.

    One adapter today (Flask decorator).  Could become middleware, a
    FastAPI dependency, or a CLI guard tomorrow — the `can()` interface
    doesn't change.
    """

    @staticmethod
    def can(actor, action, resource=None):
        """Return bool — is this actor allowed to do this action on this resource?"""
        role = actor.get('role', '')
        action_roles = {
            'manage_restaurant': {'merchant'},
            'manage_menu':       {'merchant'},
            'place_order':       {'customer'},
            'cancel_order':      {'customer', 'merchant'},
            'review_order':      {'customer'},
            'accept_delivery':   {'rider'},
            'manage_delivery':   {'rider'},
        }
        allowed_roles = action_roles.get(action, set())
        if '*' in allowed_roles:
            return True
        return role in allowed_roles


def require(role=None, owns=None):
    """Decorator factory — unified auth gate.

    Args:
        role: required role string (e.g. 'merchant', 'rider').
              None means any logged-in user.
        owns: resource type to resolve and ownership-check.
              'restaurant' — resolves current merchant's restaurant,
              injects `g.current_restaurant`.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # 1. Login check
            if 'user_id' not in session:
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login', next=request.path))

            # 2. Role check
            if role is not None and session.get('role') != role:
                flash('无权访问此页面', 'danger')
                return redirect(url_for('home'))

            # 3. Ownership resolution
            if owns == 'restaurant':
                from app.models import Restaurant
                restaurant = Restaurant.query.filter_by(
                    owner_id=session['user_id']
                ).first()
                if not restaurant:
                    flash('请先创建店铺', 'warning')
                    return redirect(url_for('restaurant.create'))
                g.current_restaurant = restaurant

                # If route has a resource ID param, verify ownership
                for param_name in ['id', 'restaurant_id']:
                    resource_id = kwargs.get(param_name)
                    if resource_id is not None:
                        # Check if this resource belongs to the merchant
                        if not _check_ownership(owns, resource_id,
                                                session['user_id']):
                            flash('无权操作', 'danger')
                            return redirect(request.referrer or url_for('home'))

            return f(*args, **kwargs)
        return decorated
    return decorator


def _check_ownership(resource_type, resource_id, user_id):
    """Check that user_id owns resource_id of the given type."""
    if resource_type == 'restaurant':
        from app.models import Restaurant
        restaurant = Restaurant.query.filter_by(owner_id=user_id).first()
        if not restaurant:
            return False
        # The resource_id might be a restaurant_id directly or
        # an entity that belongs to the restaurant (menu item, category)
        # We check the most common case: resource_id IS the restaurant
        return resource_id == restaurant.restaurant_id
    return True
