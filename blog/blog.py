from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from typing import Any
from .auth import login_required
from .db import get_db

from .messages import POST_NAO_EXISTE, SEM_TITULO, SEM_BODY


bp = Blueprint('blog', __name__)


def get_post(id: int, check_author: bool = True) -> dict[str, Any]:

    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username, like_count '
        'FROM post p JOIN user u ON p.author_id = u.id '
        'WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, POST_NAO_EXISTE)

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

def deu_like(post_id: int, user_id: int) -> bool:

    db = get_db()
    like = db.execute(
        'SELECT * FROM like WHERE post_id = ? AND user_id = ?',
        (post_id, user_id)
    ).fetchone()

    return like is not None
        

@bp.route('/')
def index():

    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username, like_count '
        'FROM post p JOIN user u ON p.author_id = u.id '
        'ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts, deu_like=deu_like)


@bp.route('/create', methods=('GET','POST'))
@login_required
def create():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = SEM_TITULO
        
        elif not body:
            error = SEM_BODY
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id) '
                'VALUES (?,?,?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/create.html')


@bp.route('/update/<int:id>', methods=('GET', 'POST'))
@login_required
def update(id: int):

    post = get_post(id)

    if request.method == 'POST':

        title = request.form['title']
        body = request.form['body']

        if not title:
            flash(SEM_TITULO)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ? '
                'WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/update.html', post=post)


@bp.route('/delete/<int:id>', methods=('POST',))
@login_required
def delete(id: int):

    # Verifica se o post existe e se o autor é o usuário logado
    # Se não, é lançada uma exceção
    get_post(id)

    db = get_db()
    db.execute(
        'DELETE FROM post WHERE id = ?',
        (id,)
    )
    db.commit()
    return redirect(url_for('blog.index'))