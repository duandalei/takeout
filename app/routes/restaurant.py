"""商家路由: 列表 / 详情 / 创建 / 编辑 / 上下线"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app.models import db, Restaurant, MenuCategory, MenuItem
from app.forms import RestaurantForm, MenuCategoryForm, MenuItemForm
from app.routes.auth import login_required, role_required

restaurant_bp = Blueprint('restaurant', __name__)


# ============================================================
# 浏览所有营业中的商家
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
# 商家详情 + 菜单
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
# 我的店铺 (商家专用)
# ============================================================
@restaurant_bp.route('/my')
@login_required
@role_required('merchant')
def my_restaurant():
    restaurant = Restaurant.query.filter_by(owner_id=session['user_id']).first()
    if not restaurant:
        flash('您还没有创建店铺，请先创建', 'info')
        return redirect(url_for('restaurant.create'))
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
# 创建店铺
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
# 编辑店铺
# ============================================================
@restaurant_bp.route('/edit', methods=['GET', 'POST'])
@login_required
@role_required('merchant')
def edit():
    restaurant = Restaurant.query.filter_by(owner_id=session['user_id']).first()
    if not restaurant:
        flash('请先创建店铺', 'warning')
        return redirect(url_for('restaurant.create'))

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
# 切换店铺状态 (营业/歇业)
# ============================================================
@restaurant_bp.route('/toggle-status')
@login_required
@role_required('merchant')
def toggle_status():
    restaurant = Restaurant.query.filter_by(owner_id=session['user_id']).first()
    if not restaurant:
        flash('请先创建店铺', 'warning')
        return redirect(url_for('restaurant.create'))

    restaurant.status = 'closed' if restaurant.status == 'open' else 'open'
    db.session.commit()
    flash(f'店铺已{"歇业" if restaurant.status == "closed" else "恢复营业"}', 'info')
    return redirect(url_for('restaurant.my_restaurant'))


# ============================================================
# 添加菜品分类
# ============================================================
@restaurant_bp.route('/category/add', methods=['GET', 'POST'])
@login_required
@role_required('merchant')
def add_category():
    restaurant = Restaurant.query.filter_by(owner_id=session['user_id']).first()
    if not restaurant:
        flash('请先创建店铺', 'warning')
        return redirect(url_for('restaurant.create'))

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
