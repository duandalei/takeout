"""WTForms 表单定义"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, HiddenField
from wtforms import IntegerField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(2, 50)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 128)])
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(2, 50)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 128)])
    real_name = StringField('真实姓名', validators=[DataRequired(), Length(1, 50)])
    phone = StringField('电话', validators=[DataRequired(), Length(5, 20)])
    email = StringField('邮箱', validators=[Optional(), Email()])
    address = StringField('地址', validators=[Optional(), Length(max=200)])
    role = SelectField('角色', choices=[
        ('customer', '顾客'),
        ('merchant', '商家'),
        ('rider',    '骑手'),
    ], validators=[DataRequired()])
    submit = SubmitField('注册')


class RestaurantForm(FlaskForm):
    name = StringField('店铺名称', validators=[DataRequired(), Length(2, 100)])
    address = StringField('店铺地址', validators=[DataRequired(), Length(2, 200)])
    phone = StringField('联系电话', validators=[DataRequired(), Length(5, 20)])
    description = TextAreaField('店铺描述', validators=[Optional(), Length(max=500)])
    submit = SubmitField('保存')


class MenuCategoryForm(FlaskForm):
    name = StringField('分类名称', validators=[DataRequired(), Length(1, 50)])
    submit = SubmitField('保存')


class MenuItemForm(FlaskForm):
    category_id = SelectField('所属分类', coerce=int, validators=[DataRequired()])
    name = StringField('菜品名称', validators=[DataRequired(), Length(1, 100)])
    description = TextAreaField('描述', validators=[Optional(), Length(max=500)])
    price = DecimalField('价格 (元)', validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField('状态', choices=[
        ('available',   '上架'),
        ('unavailable', '下架'),
    ])
    submit = SubmitField('保存')


class OrderForm(FlaskForm):
    """下单表单 — 前端动态添加菜品，这里只保留必需字段"""
    restaurant_id = HiddenField('商家ID', validators=[DataRequired()])
    delivery_address = StringField('配送地址', validators=[DataRequired(), Length(2, 200)])
    note = TextAreaField('备注', validators=[Optional(), Length(max=500)])
    submit = SubmitField('提交订单')


class ReviewForm(FlaskForm):
    rating = SelectField('评分', choices=[
        (5, '⭐⭐⭐⭐⭐ 非常满意'),
        (4, '⭐⭐⭐⭐ 满意'),
        (3, '⭐⭐⭐ 一般'),
        (2, '⭐⭐ 不满意'),
        (1, '⭐ 很差'),
    ], coerce=int, validators=[DataRequired()])
    comment = TextAreaField('评价内容', validators=[Optional(), Length(max=500)])
    submit = SubmitField('提交评价')
