"""Authorization seam — single decorator: @require(role=..., owns=...)."""

from functools import wraps
from flask import session, request, redirect, url_for, flash, g


def require(role=None, owns=None):
    """Decorator — unified auth gate.

    Args:
        role: required role string (e.g. 'merchant', 'rider'). None = any logged-in user.
        owns: 'restaurant' — resolves merchant's restaurant into g.current_restaurant.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login', next=request.path))

            if role is not None and session.get('role') != role:
                flash('无权访问此页面', 'danger')
                return redirect(url_for('home'))

            if owns == 'restaurant':
                from app.models import Restaurant
                restaurant = Restaurant.query.filter_by(
                    owner_id=session['user_id']
                ).first()
                if not restaurant:
                    flash('请先创建店铺', 'warning')
                    return redirect(url_for('restaurant.create'))
                g.current_restaurant = restaurant

                for param_name in ['id', 'restaurant_id']:
                    resource_id = kwargs.get(param_name)
                    if resource_id is not None and resource_id != restaurant.restaurant_id:
                        flash('无权操作', 'danger')
                        return redirect(request.referrer or url_for('home'))

            return f(*args, **kwargs)
        return decorated
    return decorator
