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
