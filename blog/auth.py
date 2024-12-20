from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
import functools
from typing import Callable
from .db import get_db

from .messages import (
    USERNAME_INVALIDO, SENHA_INVALIDA, USERNAME_JA_REGISTRADO, USERNAME_INCORRETO, SENHA_INCORRETA
)
from .models import User


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        db = get_db()

        if not username:
            flash(USERNAME_INVALIDO)
        elif not password:
            flash(SENHA_INVALIDA)
        else:
            try:
                User.create_and_save(username, password)
            except db.IntegrityError:
                flash(USERNAME_JA_REGISTRADO)
            else:
                flash(None)
                return redirect(url_for('auth.login'))
    
    
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        user = User.get(username = username)

        if user is None:
            flash(USERNAME_INCORRETO)
        elif not check_password_hash(user.password_hash, password):
            flash(SENHA_INCORRETA)
        else:
            flash(None)
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))
        

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():

    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
        return
    
    g.user = User.get(id = user_id)
    # g.user = get_db().execute(
    #     'SELECT * FROM user WHERE id = ?',
    #     (user_id,)
    # ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view: Callable):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    
    return wrapped_view