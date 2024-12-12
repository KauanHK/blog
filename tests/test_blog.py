import pytest
from blog.db import get_db



def test_index(client, auth):

    response = client.get('/')
    assert b'Login' in response.data
    assert b'Registrar-se' in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'test | ' in response.data
    assert b'test\nbody' is response.data
    assert b'href="/1/update"' in response.data