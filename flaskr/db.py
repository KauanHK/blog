import sqlite3
from sqlite3 import Connection
from datetime import datetime
import click
from flask import current_app, g, Flask



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

def close_db(e = None) -> None:
    '''Termina a conexão com o banco de dados caso esteja conectado.'''

    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Banco de dados inicializado.')


sqlite3.register_converter(
    'timestamp', lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app: Flask):

    # O flask chama a função quando depois de retornar o response
    app.teardown_appcontext(close_db)

    # Adiciona um novo comando que pode ser chamado com o comando 'flask'
    app.cli.add_command(init_db_command)