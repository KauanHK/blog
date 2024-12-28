from flask import g, abort
from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_db
from abc import ABC, abstractmethod
from typing import Self, Union, overload, Any
from .messages import FORBIDDEN, POST_NAO_EXISTE
import sqlite3



def _get_conditions_sql(kwargs: dict):
    values = []
    for k in kwargs:
        values.append(f'{k} = ?')
    return ' AND '.join(values)

class Model(ABC):

    def __init_subclass__(cls):
        cls.table = cls.__name__.lower()

    @classmethod
    def _get(cls, **kwargs) -> Self | None:

        db = get_db()
        command = f'SELECT * FROM {cls.table} WHERE ' + _get_conditions_sql(kwargs)
        obj = db.execute(
            command, tuple(kwargs.values())
        ).fetchone()

        return cls(*obj) if obj else None
    
    @classmethod
    def get(cls, **kwargs) -> Self | None:
        """
        Retorna um objeto com a condições dadas.

        ```
        objs = Model.get(id = 2)
        ```
        
        """

        return cls._get(**kwargs)
    
    @classmethod
    def filter(cls, **kwargs) -> list[Self]:
        """
        Retorna uma lista de objetos que satisfazem as condições

        ```
        user = User.get(id = 2)
        posts = Post.filter(user = user)
        ```
        """

        return get_db().execute(
            f'SELECT * FROM {cls.table} WHERE ' + _get_conditions_sql(kwargs),
            tuple(kwargs.values())
        ).fetchall()
    
    @classmethod
    def get_all(cls) -> list[Self]:
        """Retorna uma lista de objetos correspondente a todas linhas da tabela."""
        
        all = get_db().execute(
            f'SELECT * FROM {cls.__name__.lower()}'
        ).fetchall()
        return [cls(**kwargs) for kwargs in all]

    
    @classmethod
    def _create_and_save(cls, **kwargs) -> Self:

        obj = cls(**kwargs)
        return obj.save()
        

    @classmethod
    def create_and_save(cls, **kwargs) -> Self:
        """Cria e salva no banco de dados"""
        return cls._create_and_save(**kwargs)
    
    def is_saved(self) -> bool:
        """Retorna True se está salvo no banco de dados, senão False."""
        
        if self.id is None:
            return False
        
        db = get_db()
        line = db.execute(
            f'SELECT * FROM {self.table} WHERE id = ?',
            (self.id,)
        ).fetchone()
        
        return line is not None


    @abstractmethod
    def save(self) -> Self:
        """Salva no banco de dados."""
        ...

    

class User(Model):

    @overload
    def __init__(self, username: str, password: str) -> None: ...
    @overload
    def __init__(self, id: int, username: str, password_hash: str) -> None: ...

    def __init__(self, *args, **kwargs) -> None:

        if len(args) == 2:
            self.id = None
            self.username = args[0]
            self.password_hash = generate_password_hash(args[1])

        elif len(args) == 3:
            self.id = args[0]
            self.username = args[1]
            self.password_hash = args[2]

        elif len(kwargs) == 2:
            self.id = None
            self.username = kwargs['username']
            self.password_hash = kwargs['password']

        elif len(kwargs) == 3:
            self.id = kwargs['id']
            self.username = kwargs['username']
            self.password_hash = kwargs['password_hash']

        else:
            raise ValueError(f'init de User espera dois ou três argumentos, mas recebeu {len(args)}\nargs')
        
    def save(self) -> Self:
        
        db = get_db()
        db.execute(
            'INSERT INTO user (username, password) VALUES (?,?)',
            (self.username, self.password_hash)
        )
        db.commit()
        return User.get(username = self.username)

    @classmethod
    def create_and_save(cls, username: str, password: str) -> Self:
        return cls._create_and_save(
            username = username,
            password = generate_password_hash(password)
        )

    def __repr__(self) -> str:
        return f'User(username={self.username})'


class Post(Model):

    @overload
    def __init__(
        self,
        title: str,
        body: str,
    ) -> None: ...

    @overload
    def __init__(
        self,
        id: int,
        user_id: int,
        title: str,
        body: str,
        like_count: int,
        created: str
    ) -> None: ...

    def __init__(self, *args, **kwargs) -> None:
        
        if len(args) == 2:
            if g.user is None:
                raise ValueError('Usuário não logado.')
            self._user = g.user
            self.title = args[0]
            self.body = args[1]

        elif len(args) == 6:
            self.id = args[0]
            self._user = args[1]
            self.title = args[2]
            self.body = args[3]
            self.like_count = args[4]
            self.created = args[5]

        elif len(kwargs) == 2:
            if g.user is None:
                raise ValueError('Usuário não logado.')
            self._user = g.user
            self.title = kwargs['title']
            self.body = kwargs['body']

        elif len(kwargs) == 6:
            self.id = kwargs['id']
            self._user = kwargs['user_id']
            self.title = kwargs['title']
            self.body = kwargs['body']
            self.like_count = kwargs['like_count']
            self.created = kwargs['created']

        else:
            raise ValueError(f'Esperava 2 ou 5 argumentos, recebeu {len(args)}\n{args}')


    @property
    def user(self) -> User:

        if not isinstance(self._user, User):
            self._user = User.get(id = self._user)
            if self._user is None:
                raise ValueError('Autor do post não está registrado.')
        return self._user
    
    @property
    def likes(self) -> list["Like"]:
        return Like.filter(post_id = self.id)
    
    @property
    def replies(self) -> list["Reply"]:

        db = get_db()
        data = db.execute(
            'SELECT * FROM reply WHERE post_id = ?',
            (self.id,)
        ).fetchall()

        replies = [Reply(**data_reply) for data_reply in data]
        return replies
    
    def add_reply(self, body: str) -> "Reply":
        """
        Adiciona um Reply ao banco de dados. O usuário autor do reply será o usuário logado.
        """
        
        return Reply.create_and_save(
            post_id = self.id,
            user_id = g.user.id,
            body = body
        )

    
    @classmethod
    def get(cls, check_author: bool = True, **kwargs) -> Self:
        """
        Retorna um Post com as condições fornecidas em kwargs. 
        Se o post não existir, ou check_author for True e o usuário logado não for o autor do post, 
        lança uma exceção 404 ou 403.

        :param check_author: Se True, verifica se o usuário logado é o autor do post encontrado. Caso não seja, lança uma exceção
        """

        post = cls._get(**kwargs)
        if post is None:
            abort(404, POST_NAO_EXISTE)
        if check_author and post.user.id != g.user.id:
            abort(403, FORBIDDEN)
        return post
        
    
    def save(self) -> Self:

        db = get_db()
        db.execute(
            'INSERT INTO post (user_id, title, body) VALUES (?,?,?)',
            (self.user.id, self.title, self.body)
        )
        db.commit()
        return Post.get(user_id = self.user.id, title = self.title, body = self.body)

    def __repr__(self) -> str:
        return f'Post(title = {self.title[:10]}, body={self.body[:10]}, user={self.user.username})'


class Like(Model):

    @overload
    def __init__(
        self,
        post: Post,
        user: User,
    ) -> None: ...
        
    @overload
    def __init__(
        self,
        id: int,
        post_id: int,
        user_id: int,
        created: str
    ) -> None: ...

    def __init__(self, *args, **kwargs) -> None:

        if len(args) == 2:
            self._post = args[0]
            self._user = args[1]
        
        elif len(args) == 4:
            self.id = args[0]
            self._post = args[1]
            self._user = args[2]
            self.created = args[3]

        elif len(kwargs) == 2:
            self._post = kwargs['post']
            self._user = kwargs['user']
        
        elif len(kwargs) == 3:
            self.id = kwargs['id']
            self._post = kwargs['post']
            self._user = kwargs['user']
            self.created = kwargs['created']

        else:
            raise ValueError(f'Esperava 5 ou 3 argumentos *args ou **kwargs')


    @property
    def post(self) -> Post:
        if not isinstance(self._post, Post):
            self._post = Post.get(id = self._post)
        return self._post
    
    @property
    def user(self) -> User:
        if not isinstance(self._user, User):
            self._user = User.get(id = self._user)
        return self._user

    def save(self) -> Self:

        db = get_db()
        db.execute(
            'INSERT INTO like (post_id, user_id) VALUES (?,?)',
            (self.post.id, self.user.id)
        )
        db.commit()
        return Like.get(post_id = self.post.id, user_id = self.user.id)

    def __repr__(self) -> str:
        return f'Like(post={self.post}, user={self.user})'
    

class Reply(Model):

    @overload
    def __init__(
        self,
        post: Post,
        user: User,
        body: str,
    ) -> None: ...

    @overload
    def __init__(
        self,
        id: int,
        post_id: int,
        user_id: int,
        body: str,
        created: str
    ) -> None: ...
        
    def __init__(self, *args, **kwargs) -> None:

        if len(args) == 5:
            self.id = args[0]
            self._post = args[1]
            self._user = args[2]
            self.body = args[3]
            self.created = args[4]
        
        elif len(args) == 3:
            self._post = args[0]
            self._user = args[1]
            self.body = args[2]

        elif len(kwargs) == 5:
            self.id = kwargs['id']
            self._post = kwargs['post']
            self._user = kwargs['user']
            self.body = kwargs['body']
            self.created = kwargs['created']
        
        elif len(kwargs) == 3:
            self._post = kwargs['post']
            self._user = kwargs['user']
            self.body = kwargs['body']

        else:
            raise ValueError(f'Esperava 5 ou 3 argumentos *args ou **kwargs')
        
    @property
    def post(self) -> Post:
        if not isinstance(self._post, Post):
            self._post = Post.get(id = self._post)
        return self._post
    
    @property
    def user(self) -> User:
        if not isinstance(self._user, User):
            self._user = User.get(id = self._user)
        return self._user

        
    def save(self) -> Self:

        db = get_db()
        db.execute(
            'INSERT INTO reply (post_id, user_id, body) values (?,?,?)',
            (self.post.id, self.user.id, self.body)
        )
        db.commit()
        return Reply.get(post_id = self.post.id, user_id = self.user.id, body = self.body)

    def __repr__(self) -> str:
        return f'Reply(post={self.post}, user={self.user}, body={self.body})'


ModelType = Union[User, Post, Like, Reply]