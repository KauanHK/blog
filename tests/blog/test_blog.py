import pytest
from blog.db import get_db
from flask import Flask
from flask.testing import FlaskClient
from conftest import AuthActions



def test_index(client: FlaskClient, auth: AuthActions):
    """
    1. Faz uma requisição GET para '/'
    2. Verifica se response.data contém 'Login'
    3. Verifica se response.data contém 'Registrar-se'
    4. 'auth' faz login
    5. Faz uma requisição GET para '/'
    6. Verifica se response.data contém 'Log Out'
    7. Verifica se response.data contém 'test title'
    8. Verifica se response.data contém 'test | '
    9. Verifica se response.data contém 'href="/1/update'
    """

    response = client.get('/')
    assert b'Login' in response.data
    assert b'Registrar-se' in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'test | ' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/update/1"' in response.data


@pytest.mark.parametrize(
    'path',
    (
        '/create',
        '/update/1',
        '/delete/1'
    )
)
def test_login_required(client: FlaskClient, path: str) -> None:
    """
    1. POST para 'path'
    2. Verifica se foi direcionado para '/auth/login'
    """

    response = client.post(path)
    assert response.headers['Location'] == '/auth/login'

def test_author_required(app: Flask, client: FlaskClient, auth: AuthActions) -> None:
    """
    1. Atualiza o autor do post
    2. 'auth' faz login
    3. Verifica se o status da requisição para editar o post que não é de autoria de 'auth' é igual a 403
    4. idem para deletar
    5. Faz uma requisição GET para '/'
    6. Verifica se response não contém link para editar o post
    """

    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    assert client.post('/update/1').status_code == 403
    assert client.post('/delete/1').status_code == 403
    assert b'href="/update/1"' not in client.get('/').data


@pytest.mark.parametrize(
    'path',
    (
        '/update/2',
        '/delete/2'
    )
)
def test_exists_required(client: FlaskClient, auth: AuthActions, path: str) -> None:
    """
    1. 'auth' faz login
    2. Verifica se o status da requisição POST para 'path' é igual a 404
    """

    auth.login()
    assert client.post(path).status_code == 404


def test_create(client: FlaskClient, auth: AuthActions, app: Flask) -> None:
    """
    1. 'auth' faz login
    2. Verifica se o status da requisição GET para '/create' é igual a 200
    3. POST para '/create'
    4. Verifica se o post foi criado
    """

    auth.login()
    assert client.get('/create').status_code == 200
    client.post(
        '/create',
        data = {
            'title': 'created',
            'body': ''
        }
    )

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 1


def test_update(client: FlaskClient, auth: AuthActions, app: Flask):
    """
    1. 'auth' faz login
    2. Verifica se o status da requisição GET para '/update/1' é igual a 200
    3. POST para '/update/1'
    4. Verifica se o post foi atualizado
    """

    auth.login()
    assert client.get('/update/1').status_code == 200
    client.post(
        '/update/1',
        data = {
            'title': 'updated',
            'body': 'body atualizado!'
        }
    )

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize(
    'path',
    (
        '/create',
        '/update/1'
    )
)
def test_create_update_validate(client: FlaskClient, auth: AuthActions, path: str):
    """
    1. 'auth' faz login
    2. POST para 'path' para criar um post com os campos vazios
    3. Verifica se response contém a mensagem de erro esperada
    """

    auth.login()
    response = client.post(
        path,
        data = {
            'title': '',
            'body': ''
        }
    )
    # Adicionar verificação para o body
    assert b'A postagem deve ter um t' in response.data


def test_delete(client: FlaskClient, auth: AuthActions, app: Flask):
    """
    1. 'auth' faz login
    2. POST para deletar o post
    3. Verifica se foi direcionado para '/'
    4. Verifica se o post foi apagado
    """

    auth.login()
    response = client.post('/delete/1')
    assert response.headers['Location'] == '/'

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None


def test_reply(app: Flask, client: FlaskClient, auth: AuthActions):

    auth.login()

    response = client.post(
        '/reply/1',
        data = {
            'body': 'Body teste ...'
        }
    )
    assert response.headers['Location'] == '/'

    with app.app_context():
        db = get_db()
        reply = db.execute(
            'SELECT body FROM reply WHERE id = ?',
            (1,)
        ).fetchone()
        assert reply['body'] == 'Body teste ...'
