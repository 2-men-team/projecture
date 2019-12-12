import functools

from flask import Blueprint, flash, g, redirect
from flask import render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from projecture.db import get_db, get_cursor

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')


def require_auth(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@auth_blueprint.before_app_request
def load_logged_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        cursor = get_cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        g.user = cursor.fetchone()


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        cursor = get_cursor()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'

        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))

        if cursor.fetchone() is not None:
            error = 'User with email {} is already registered.'.format(email)

        cursor.execute('SELECT id FROM users WHERE username = %s', (username,))

        if cursor.fetchone() is not None:
            error = 'User with username {} is already registered.'.format(email)

        if error is None:
            cursor.execute(
                'INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)',
                (username, generate_password_hash(password), email)
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None:
        return redirect(url_for('project.index'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = get_cursor()
        error = None

        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@auth_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

