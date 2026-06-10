"""Restaurant routes: list / detail / create / edit / toggle status."""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, g
from app.models import db, Restaurant, MenuCategory, MenuItem
from app.forms import RestaurantForm, MenuCategoryForm, MenuItemForm
from app.routes.auth import login_required, role_required
from app.domain.auth import require

restaurant_bp = Blueprint('restaurant', __name__)


# ============================================================
# Browse all open restaurants
# ============================================================
@restaurant_bp.route('/')
def list_restaurants():
    keyword = request.args.get('q', '').strip()
    query = Restaurant.query.filter_by(status='open')
    if keyword:
        query = query.filter(
            Restaurant.name.contains(keyword) |
            Restaurant.description.contains(keyword)
        )
    restaurants = query.order_by(Restaurant.created_at.desc()).all()
    return render_template('restaurant/list.html', restaurants=restaurants, keyword=keyword)


# ============================================================
# Restaurant detail + menu
# ============================================================
@restaurant_bp.route('/<int:id>')
def detail(id):
    restaurant = Restaurant.query.get_or_404(id)
    categories = (
        MenuCategory.query
        .filter_by(restaurant_id=id)
        .order_by(MenuCategory.sort_order)
        .all()
    )
    return render_template('restaurant/detail.html',
                           restaurant=restaurant,
                           categories=categories)


# ============================================================
# My restaurant (merchant only)
# ============================================================
@restaurant_bp.route('/my')
@require(role='merchant', owns='restaurant')
def my_restaurant():
    restaurant = g.current_restaurant
    categories = (
        MenuCategory.query
        .filter_by(restaurant_id=restaurant.restaurant_id)
        .order_by(MenuCategory.sort_order)
        .all()
    )
    return render_template('restaurant/my.html',
                           restaurant=restaurant,
                           categories=categories)


# ============================================================
# Create restaurant
# ============================================================
@restaurant_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('merchant')
def create():
    existing = Restaurant.query.filter_by(owner_id=session['user_id']).first()
    if existing:
        flash('您已有店铺', 'info')
        return redirect(url_for('restaurant.my_restaurant'))

    form = RestaurantForm()
    if form.validate_on_submit():
        restaurant = Restaurant(
            owner_id=session['user_id'],
            name=form.name.data,
            address=form.address.data,
            phone=form.phone.data,
            description=form.description.data,
        )
        db.session.add(restaurant)
        db.session.commit()

        flash('店铺创建成功！', 'success')
        return redirect(url_for('restaurant.my_restaurant'))

    return render_template('restaurant/create.html', form=form)


# ============================================================
# Edit restaurant
# ============================================================
@restaurant_bp.route('/edit', methods=['GET', 'POST'])
@require(role='merchant', owns='restaurant')
def edit():
    restaurant = g.current_restaurant

    form = RestaurantForm(obj=restaurant)
    if form.validate_on_submit():
        restaurant.name = form.name.data
        restaurant.address = form.address.data
        restaurant.phone = form.phone.data
        restaurant.description = form.description.data
        db.session.commit()
        flash('店铺信息已更新', 'success')
        return redirect(url_for('restaurant.my_restaurant'))

    return render_template('restaurant/edit.html', form=form, restaurant=restaurant)


# ============================================================
# Toggle restaurant status (open/closed)
# ============================================================
@restaurant_bp.route('/toggle-status')
@require(role='merchant', owns='restaurant')
def toggle_status():
    restaurant = g.current_restaurant
    restaurant.status = 'closed' if restaurant.status == 'open' else 'open'
    db.session.commit()
    flash(f'店铺已{"歇业" if restaurant.status == "closed" else "恢复营业"}', 'info')
    return redirect(url_for('restaurant.my_restaurant'))


# ============================================================
# Add menu category
# ============================================================
@restaurant_bp.route('/category/add', methods=['GET', 'POST'])
@require(role='merchant', owns='restaurant')
def add_category():
    restaurant = g.current_restaurant

    form = MenuCategoryForm()
    if form.validate_on_submit():
        max_sort = (
            db.session.query(db.func.max(MenuCategory.sort_order))
            .filter_by(restaurant_id=restaurant.restaurant_id)
            .scalar() or 0
        )
        category = MenuCategory(
            restaurant_id=restaurant.restaurant_id,
            name=form.name.data,
            sort_order=max_sort + 1,
        )
        db.session.add(category)
        db.session.commit()
        flash('分类添加成功', 'success')
        return redirect(url_for('restaurant.my_restaurant'))

    return render_template('restaurant/category_form.html', form=form, action='添加')
