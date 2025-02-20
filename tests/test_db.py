import sqlite3
import pytest
from blog.db import get_db
from flask import Flask


def test_get_close_db(app: Flask):

    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_init_db_command(runner, monkeypatch):
    
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('blog.db.init_db', fake_init_db)
    result = runner.invoke(args = ['init-db'])
    assert 'inicializado' in result.output
    assert Recorder.called