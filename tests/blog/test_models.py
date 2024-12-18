import pytest
from flask import Flask
from flask.testing import FlaskClient

from conftest import AuthActions
from blog.db import get_db
from blog.models import User, Post



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
