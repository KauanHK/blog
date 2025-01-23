import pytest
from flask import g, session
from blog.db import get_db

from flask import Flask
from flask.testing import FlaskClient
from conftest import AuthActions
from blog.messages import (
    USERNAME_INVALIDO, SENHA_INVALIDA, USERNAME_JA_REGISTRADO, USERNAME_INCORRETO, SENHA_INCORRETA
)


def test_register(client: FlaskClient, app: Flask) -> None:
    """
    1. Verifica se o status da requisição para '/auth/register' é igual a 200
    2. Envia as credenciais {'username': 'a', 'password': 'a'}
    3. Verifica se foi direcionado para '/auth/login'
    4. Verifica se foi registrado no banco de dados
    """
    
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data = {
            'username': 'w',
            'password': 'w',
            'confirm_password': 'w'
        }
    )
    assert response.headers['Location'] == '/auth/login'

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = ?",
            ('w',)
        ).fetchone() is not None


@pytest.mark.parametrize(
    ('username', 'password', 'message'),
    (
        ('', '', USERNAME_INVALIDO.encode()),
        ('a', '', SENHA_INVALIDA.encode()),
        ('a', '123', USERNAME_JA_REGISTRADO.encode())
    )
)
def test_register_validate_input(client: FlaskClient, username: str, password: str, message: bytes) -> None:
    """
    1. Envia um post para '/auth/register' com as credenciais fornecidas como parâmetro
    2. Verifica se 'message' está em response.data
    """

    response = client.post(
        '/auth/register',
        data = {
            'username': username,
            'password': password,
            'confirm_password': password
        }
    )
    assert message in response.data


def test_login(client: FlaskClient, auth: AuthActions) -> None:
    """
    1. Verifica se o status da requisição para '/auth/login' é igual a 200
    2. 'auth' faz login
    3. Verifica se o cliente foi direcionado para '/'
    4. Requisição GET para '/'
    5. Verifica se 'session' armazena o id do usuário
    6. Verifica se 'g.user' armazena o username e se ele é igual a 'test'
    """

    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == '/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user.username == 'a'


@pytest.mark.parametrize(
    ('username', 'password', 'message'),
    (
        ('h', 'test', USERNAME_INCORRETO.encode()),
        ('a', 'b', SENHA_INCORRETA.encode())
    )
)
def test_login_validate_input(auth: AuthActions, username: str, password: str, message: str) -> None:
    """
    1. 'auth' faz login com as credenciais 'username' e 'password'
    2. Verifica se response.data contém 'message'
    """

    response = auth.login(username, password)
    assert message in response.data


def test_logout(client: FlaskClient, auth: AuthActions) -> None:
    """
    1. Faz login
    2. Faz logout
    3. Verifica se session não está armazenando um id de usuário
    """

    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session