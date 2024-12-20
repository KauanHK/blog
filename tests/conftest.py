import os
import tempfile
import pytest
from blog import create_app
from blog.db import get_db, init_db

from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from werkzeug.test import TestResponse
from typing import Generator




with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app() -> Generator[Flask, None, None]:

    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()


class AuthActions(object):

    def __init__(self, client: FlaskClient) -> None:
        self._client = client

    def login(self, username: str = 'a', password: str = 'a') -> TestResponse:
        return self._client.post(
            '/auth/login',
            data = {
                'username': username,
                'password': password
            }
        )
    
    def logout(self) -> TestResponse:
        return self._client.get('/auth/logout')
    

@pytest.fixture
def auth(client: FlaskClient) -> AuthActions:
    return AuthActions(client)