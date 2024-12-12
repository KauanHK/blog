import os
from flask import Flask



def create_app(test_config = None) -> Flask:
    """Cria o app Flask com as configurações fornecidas por 'test_config'."""

    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(
        SECRET_KEY = '123',
        DATABASE = os.path.join(app.instance_path, 'blog.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent = True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, world!'

    # Inicialização do app
    from . import db
    db.init_app(app)

    # Registro dos blueprint's
    from . import auth, blog
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app