from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
from .models import Post, Like, Reply
from .messages import POST_NAO_EXISTE, SEM_TITULO, SEM_BODY


bp = Blueprint('blog', __name__)


def get_post(id: int, check_author: bool = True) -> Post:

    post = Post.get(id = id)
    if post is None:
        abort(404, POST_NAO_EXISTE)

    if check_author and post.user.id != g.user.id:
        abort(403)
    return post


def deu_like(post_id: int, user_id: int) -> bool:
    like = Like.get(post_id = post_id, user_id = user_id)
    return like is not None
        

@bp.route('/')
def index():
    posts = Post.get_all()
    return render_template('blog/index.html', posts=posts, deu_like=deu_like)


@bp.route('/create', methods=('GET','POST'))
@login_required
def create():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if not title:
            flash(SEM_TITULO)        
        elif not body:
            flash(SEM_BODY)
        else:
            flash(None)

            Post.create_and_save(
                title = title,
                body = body
            )
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


@bp.route('/like/<int:post_id>', methods=('GET',))
@login_required
def like(post_id: int):

    # Se o post não existir, será lançada uma exceção
    get_post(post_id, check_author=False)

    db = get_db()
    if deu_like(post_id, g.user.id):
        db.execute(
            'DELETE FROM like WHERE post_id = ? AND user_id = ?',
            (post_id, g.user.id)
        )
        db.execute(
            'UPDATE post SET like_count = like_count - 1 WHERE id = ?',
            (post_id,)
        )
        liked = False
    else:
        db.execute(
            'INSERT INTO like (post_id, user_id) VALUES (?,?)',
            (post_id, g.user.id)
        )
        db.execute(
            'UPDATE post SET like_count = like_count + 1 WHERE id = ?',
            (post_id,)
        )
        liked = True

    db.commit()

    like_count = db.execute(
        'SELECT like_count FROM post WHERE id = ?',
        (post_id,)
    ).fetchone()[0]

    return jsonify({
        'liked': liked,
        'like_count': like_count
    })



@bp.route('/reply/<int:post_id>', methods=('GET', 'POST'))
@login_required
def reply(post_id: int = None):

    get_post(post_id, check_author=False)
    if request.method == 'GET':
        return render_template('blog/reply.html')

    body = request.form['body']

    if not body:
        flash(SEM_BODY)
        return redirect(url_for('blog.reply', post_id=post_id))
        
    Reply.create_and_save(
        post = post_id,
        user = g.user.id,
        body = body
    )
    return redirect(url_for('blog.index'))
