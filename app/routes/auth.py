"""User auth routes: register / login / logout."""

from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User
from app.forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)


# ============================================================
# Register
# ============================================================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(username=form.username.data).first()
        if existing:
            flash('用户名已被注册', 'danger')
            return render_template('auth/register.html', form=form)

        user = User(
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data),
            real_name=form.real_name.data,
            phone=form.phone.data,
            address=form.address.data or None,
            role=form.role.data,
        )
        db.session.add(user)
        db.session.commit()

        flash('注册成功！请登录', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


# ============================================================
# Login
# ============================================================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if not user or not check_password_hash(user.password_hash, form.password.data):
            flash('用户名或密码错误', 'danger')
            return render_template('auth/login.html', form=form)

        session['user_id']   = user.user_id
        session['username']  = user.username
        session['role']      = user.role
        session['real_name'] = user.real_name

        next_url = request.args.get('next', url_for('home'))
        flash(f'欢迎回来，{user.real_name}！', 'success')
        return redirect(next_url)

    return render_template('auth/login.html', form=form)


# ============================================================
# Logout
# ============================================================
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('已安全退出', 'info')
    return redirect(url_for('home'))
