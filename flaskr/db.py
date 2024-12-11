import sqlite3
from sqlite3 import Connection
from datetime import datetime
import click
from flask import current_app, g



def get_db() -> Connection:
    '''Retorna a conexão com o banco de dados.
    Se ainda não houver uma conexão, cria uma.'''

    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types = sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db() -> None:
    '''Termina a conexão com o banco de dados caso esteja conectado.'''

    db = g.pop('db', None)
    if db is not None:
        db.close()