import pytest
from flask import Flask

from blog.db import get_db
from blog.models import User, Post, ModelType
from werkzeug.security import check_password_hash
from typing import Any


def get_user(username: str):
    db = get_db()
    return db.execute(
        'SELECT username FROM user WHERE username = ?',
        (username,)
    ).fetchone()


def test_save_user(app: Flask):

    username = 'bob'
    with app.app_context():
        
        assert get_user(username) is None

        user = User(username, '123')
        user.save()

        bob = get_user(username)
        assert bob['username'] == username


@pytest.mark.parametrize(
    'obj',
    (
        User('x', '123'),
        User('y', '123'),
        User('z', '123')
    )
)
def test_is_saved(app: Flask, obj: ModelType):

    with app.app_context():

        assert not obj.is_saved()
        obj = obj.save()
        assert obj.is_saved()


def test_user_create_and_save(app: Flask):

    username = 'robert'
    with app.app_context():

        User.create_and_save(username, '123')
        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE username = ?',
            (username,)
        ).fetchone()

        assert user['username'] == username
        assert check_password_hash(user['password'], '123')


@pytest.mark.parametrize(
    ('username', 'password'),
    (
        ('a', 'a'),
        ('b', 'b'),
        ('c', 'c'),
        ('d', 'd'),
    )
)
def test_user_get(app: Flask, username: str, password: str):

    with app.app_context():

        user = User.get(username = username)
        assert user.username == username
        assert check_password_hash(user.password_hash, password)


@pytest.mark.parametrize(
    ('model_type', 'kwargs', 'length'),
    (
        (Post, {'title': 'test title'}, 4),
        (Post, {'body': 'test body'}, 3),
        (Post, {'title': 'test title', 'body': 'test body'}, 2)
    )
)
def test_filter(app: Flask, model_type: ModelType, kwargs: dict[str, Any], length: int):

    with app.app_context():
        assert len(model_type.filter(**kwargs)) == length

