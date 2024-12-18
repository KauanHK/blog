import pytest
from flask import Flask
from flask.testing import FlaskClient
import sqlite3

from conftest import AuthActions
from blog.db import get_db
from blog.models import User, Post, ModelType
from typing import Any
from collections.abc import Callable



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


@pytest.mark.parametrize(
    ('username', 'password'),
    (
        ('bob', '123'),
        ('a', 'a'),
        ('z', 'z')
    )
)
def test_user_get(app: Flask, username: str, password: str):

    with app.app_context():

        User.create_and_save(username, password, raise_integrity = False)

        user = User.get(username = username)
        assert user.username == username
