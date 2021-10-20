import flask_bcrypt
from flask import Blueprint, redirect, url_for, render_template, request, flash
from flask_login import current_user, login_user, logout_user

from kunsthandel import bcrypt, db
from kunsthandel.main.utils import role_required
from kunsthandel.models import User, Role
from kunsthandel.users.forms import LoginForm, UpdateAccountForm, CreateAccountForm, UpdateOwnAccountForm

users = Blueprint('users', __name__)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    return render_template('users/login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.home'))


@users.route('/users/me', methods=['GET', 'POST'])
@role_required(Role.User)
def edit_own_user():
    form = UpdateOwnAccountForm()
    user = User.query.get(current_user.id)
    if form.validate_on_submit():
        hashed_password = flask_bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for('users.edit_own_user'))
    return render_template("users/user_own.html", title="Edit User Account", user=user, form=form)


@users.route('/users/<int:id>', methods=['GET', 'POST'])
@role_required(Role.Administrator)
def edit_user(id):
    form = UpdateAccountForm()
    user = User.query.get(id)
    if form.validate_on_submit():
        user.username = form.username.data
        if form.password.data:
            hashed_password = flask_bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password
        user.role_id = form.role.data
        db.session.commit()
        flash("The account has been updated!", "success")
        return redirect(url_for('users.overview'))
    elif request.method == 'GET':
        form.old_username.data = user.username
        form.username.data = user.username
        form.password.data = user.password
        form.role.data = str(user.role_id)
    return render_template("users/user.html", title="Edit User " + user.username, user=user, form=form)


@users.route('/users/create', methods=['GET', 'POST'])
@role_required(Role.Administrator)
def create_user():
    form = CreateAccountForm()
    if form.validate_on_submit():
        hashed_password = flask_bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password, role_id=int(form.role.data))
        db.session.add(user)
        db.session.commit()
        flash("User account with id " + str(user.id) + " has been created!", "success")
        if request.args.get("multiple", False):
            return redirect(url_for('users.create_user', multiple=True))
        return redirect(url_for('users.overview'))
    elif request.method == 'GET':
        form.role.data = "1" # Default role
    return render_template("users/user.html", title="Create new user", user=None, form=form)


@users.route('/users/<int:id>/delete', methods=['POST'])
@role_required(Role.Administrator)
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("This user account has been deleted!", "success")
    return redirect(url_for("users.overview"))


@users.route('/users')
@role_required(Role.Administrator)
def overview():
    page = request.args.get('page', type=int)
    #per_page = int(request.args.get("display", 50))
    users = User.query.paginate(page=page, per_page=50)
    return render_template("users/users.html", title='Manage User Accounts', users=users)
