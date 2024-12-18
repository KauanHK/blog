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
        return cls._get(**kwargs)
    
    @classmethod
    def filter(cls, **kwargs) -> list[Self]:

        return get_db().execute(
            f'SELECT * FROM {cls.table} WHERE ' + _get_conditions_sql(kwargs),
            tuple(kwargs.values())
        ).fetchall()
    
    @classmethod
    def get_all(cls) -> list[Self]:
        
        all = get_db().execute(
            f'SELECT * FROM {cls.__name__.lower()}'
        ).fetchall()
        return [cls(**kwargs) for kwargs in all]

    
    @classmethod
    def _create_and_save(cls, **kwargs) -> Self:

        for k,v in kwargs.items():
            if isinstance(v, ModelType):
                kwargs.pop(k)
                kwargs[f'{k}_id'] = v.id

        keys = ','.join(kwargs.keys())
        values = tuple(kwargs.values())

        db = get_db()
        db.execute(
            f'INSERT INTO {cls.__name__.lower()} ({keys}) VALUES ({','.join('?'*len(kwargs))})',
            values
        )
        db.commit()

    @classmethod
    def create_and_save(cls, **kwargs) -> Self:
        return cls._create_and_save(kwargs)

    @abstractmethod
    def save(self) -> None: ...
    

class User(Model):

    @overload
    def __init__(self, id: int, username: str, password_hash: str) -> None: ...
    @overload
    def __init__(self, username: str, password: str) -> None: ...

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
        
    def save(self) -> None:
        
        db = get_db()
        db.execute(
            'INSERT INTO user (username, password) VALUES (?,?)',
            (self.username, self.password_hash)
        )
        db.commit()

    @classmethod
    def create_and_save(cls, username: str, password: str, raise_integrity: bool = True) -> Self:
        try:
            return cls._create_and_save(
                username = username,
                password = generate_password_hash(password)
            )
        except sqlite3.IntegrityError:
            if raise_integrity:
                raise


    def is_registered(self) -> None:
        return self.id is None
        

class Post(Model):

    @overload
    def __init__(
        self,
        author: User,
        title: str,
        body: str,
    ) -> None: ...

    @overload
    def __init__(
        self,
        id: int,
        author_id: int,
        title: str,
        body: str,
        like_count: int,
        created: str
    ) -> None: ...

    def __init__(self, *args, **kwargs) -> None:
        
        if len(args) == 3:
            self._author = args[0]
            self.title = args[1]
            self.body = args[2]

        elif len(args) == 6:
            self.id = args[0]
            self._author = args[1]
            self.title = args[2]
            self.body = args[3]
            self.like_count = args[4]
            self.created = args[5]

        elif len(kwargs) == 3:
            self._author = kwargs['author']
            self.title = kwargs['title']
            self.body = kwargs['body']

        elif len(kwargs) == 6:
            self.id = kwargs['id']
            self._author = kwargs['author_id']
            self.title = kwargs['title']
            self.body = kwargs['body']
            self.like_count = kwargs['like_count']
            self.created = kwargs['created']

        else:
            raise ValueError(f'Esperava 3 ou 5 argumentos, recebeu {len(args)}\n{args}')


    @property
    def author(self) -> User:

        if not isinstance(self._author, User):
            self._author = User.get(id = self._author)
        return self._author
    
    @property
    def likes(self) -> list["Like"]:
        return Like.filter(post_id = self.id)
    
    @classmethod
    def get(cls, check_author: bool = True, **kwargs) -> Self | None:

        post = cls._get(kwargs)
        if post is None:
            abort(404, POST_NAO_EXISTE)
        if check_author and post.id != g.user.id:
            abort(403, FORBIDDEN)
        return post
        
    
    def save(self) -> None:

        db = get_db()
        db.execute(
            'INSERT INTO post (author_id, title, body) VALUES (?,?,?)',
            (self.author.id, self.title, self.body)
        )
        db.commit()


class Like(Model):

    @overload
    def __init__(
        self,
        post: Post,
        author: User,
    ) -> None: ...
        
    @overload
    def __init__(
        self,
        id: int,
        post_id: int,
        author_id: int,
        created: str
    ) -> None: ...

    def __init__(self, *args, **kwargs) -> None:

        if len(args) == 2:
            self._post = args[0]
            self._author = args[1]
        
        elif len(args) == 4:
            self.id = args[0]
            self._post = args[1]
            self._author = args[2]
            self.created = args[3]

        elif len(kwargs) == 2:
            self._post = kwargs['post']
            self._author = kwargs['author']
        
        elif len(kwargs) == 3:
            self.id = kwargs['id']
            self._post = kwargs['post']
            self._author = kwargs['author']
            self.created = kwargs['created']

        else:
            raise ValueError(f'Esperava 5 ou 3 argumentos *args ou **kwargs')


    @property
    def post(self) -> Post:
        if not isinstance(self._post, Post):
            self._post = Post.get(id = self._post)
        return self._post
    
    @property
    def author(self) -> User:
        if not isinstance(self._author, User):
            self._author = User.get(id = self._author)
        return self._author

    def save(self) -> None:

        db = get_db()
        db.execute(
            'INSERT INTO like (post_id, author_id) VALUES (?,?)',
            (self.post.id, self.author.id)
        )
        db.commit()
    

class Reply:

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
            self.post = args[1]
            self.user = args[2]
            self.body = args[3]
            self.created = args[4]
        
        elif len(args) == 3:
            self.post = args[0]
            self.user = args[1]
            self.body = args[2]

        elif len(kwargs) == 5:
            self.id = kwargs['id']
            self.post = kwargs['post']
            self.user = kwargs['user']
            self.body = kwargs['body']
            self.created = kwargs['created']
        
        elif len(kwargs) == 3:
            self.post = kwargs['post']
            self.user = kwargs['user']
            self.body = kwargs['body']

        else:
            raise ValueError(f'Esperava 5 ou 3 argumentos *args ou **kwargs')
        
    def save(self) -> None:

        db = get_db()
        db.execute(
            'INSERT INTO reply (post_id, user_id, body) values (?,?,?)',
            (self.post.id, self.user.id, self.body)
        )
        db.commit()


ModelType = Union[User, Post, Like, Reply]