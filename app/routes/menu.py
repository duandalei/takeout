"""Menu routes: menu item CRUD / toggle status."""

from flask import Blueprint, render_template, redirect, url_for, flash, session
from app.models import db, Restaurant, MenuCategory, MenuItem
from app.forms import MenuItemForm
from app.domain.auth import require

menu_bp = Blueprint('menu', __name__)


def _current_restaurant():
    """Resolve the current merchant user's restaurant."""
    return Restaurant.query.filter_by(owner_id=session['user_id']).first()


# ============================================================
# Add menu item
# ============================================================
@menu_bp.route('/add', methods=['GET', 'POST'])
@require(role='merchant')
def add():
    restaurant = _current_restaurant()
    if not restaurant:
        flash('请先创建店铺', 'warning')
        return redirect(url_for('restaurant.create'))

    form = MenuItemForm()
    form.category_id.choices = [
        (c.category_id, c.name)
        for c in MenuCategory.query
        .filter_by(restaurant_id=restaurant.restaurant_id)
        .order_by(MenuCategory.sort_order)
        .all()
    ]
    if form.validate_on_submit():
        item = MenuItem(
            restaurant_id=restaurant.restaurant_id,
            category_id=form.category_id.data,
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            status=form.status.data,
        )
        db.session.add(item)
        db.session.commit()
        flash('菜品添加成功', 'success')
        return redirect(url_for('restaurant.my_restaurant'))

    return render_template('menu/form.html', form=form, action='添加菜品')


# ============================================================
# Edit menu item
# ============================================================
@menu_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@require(role='merchant')
def edit(id):
    restaurant = _current_restaurant()
    if not restaurant:
        flash('请先创建店铺', 'warning')
        return redirect(url_for('restaurant.create'))

    item = MenuItem.query.get_or_404(id)
    if item.restaurant_id != restaurant.restaurant_id:
        flash('无权操作', 'danger')
        return redirect(url_for('restaurant.my_restaurant'))

    form = MenuItemForm(obj=item)
    form.category_id.choices = [
        (c.category_id, c.name)
        for c in MenuCategory.query
        .filter_by(restaurant_id=restaurant.restaurant_id)
        .order_by(MenuCategory.sort_order)
        .all()
    ]
    if form.validate_on_submit():
        item.category_id = form.category_id.data
        item.name = form.name.data
        item.description = form.description.data
        item.price = form.price.data
        item.status = form.status.data
        db.session.commit()
        flash('菜品已更新', 'success')
        return redirect(url_for('restaurant.my_restaurant'))

    return render_template('menu/form.html', form=form, action='编辑菜品')


# ============================================================
# Delete menu item
# ============================================================
@menu_bp.route('/delete/<int:id>')
@require(role='merchant')
def delete(id):
    restaurant = _current_restaurant()
    if not restaurant:
        flash('请先创建店铺', 'warning')
        return redirect(url_for('restaurant.create'))

    item = MenuItem.query.get_or_404(id)
    if item.restaurant_id != restaurant.restaurant_id:
        flash('无权操作', 'danger')
        return redirect(url_for('restaurant.my_restaurant'))

    db.session.delete(item)
    db.session.commit()
    flash('菜品已删除', 'info')
    return redirect(url_for('restaurant.my_restaurant'))


# ============================================================
# Toggle menu item status (available/unavailable)
# ============================================================
@menu_bp.route('/toggle/<int:id>')
@require(role='merchant')
def toggle(id):
    restaurant = _current_restaurant()
    if not restaurant:
        flash('请先创建店铺', 'warning')
        return redirect(url_for('restaurant.create'))

    item = MenuItem.query.get_or_404(id)
    if item.restaurant_id != restaurant.restaurant_id:
        flash('无权操作', 'danger')
        return redirect(url_for('restaurant.my_restaurant'))

    item.status = 'available' if item.status == 'unavailable' else 'unavailable'
    db.session.commit()
    flash(f'菜品已{"上架" if item.status == "available" else "下架"}', 'info')
    return redirect(url_for('restaurant.my_restaurant'))
