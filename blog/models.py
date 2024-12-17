from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_db
from typing import Self, Union, overload




class Model:

    @classmethod
    def get(cls, **kwargs) -> Self | None:

        values = []
        for k in kwargs:
            values.append(f'{k} = ?')

        command = f'SELECT * FROM {cls.__name__.lower()} WHERE ' + ' AND '.join(values)

        db = get_db()
        obj = db.execute(
            command, tuple(kwargs.values())
        ).fetchone()

        return cls(*obj) if obj else None
    
    @classmethod
    def get_all(cls) -> list[Self]:
        
        all = get_db().execute(
            f'SELECT * FROM {cls.__name__.lower()}'
        ).fetchall()
        return [cls(**kwargs) for kwargs in all]

    
    @classmethod
    def save(cls, **kwargs) -> None:

        keys = ','.join(kwargs.keys())
        values = tuple(kwargs.values())

        db = get_db()
        db.execute(
            f'INSERT INTO {cls.__name__.lower()} ({keys}) VALUES ({','.join('?'*len(kwargs))})',
            values
        )
        db.commit()
    

class User(Model):

    @overload
    def __init__(self, id: int, username: str, password_hash: str) -> None: ...
    @overload
    def __init__(self, username: str, password: str) -> None: ...

    def __init__(self, *args, **kwargs) -> None:

        if len(args) == 2:
            self.username = args[0]
            self.password_hash = generate_password_hash(args[1])

        elif len(args) == 3:
            self.id = args[0]
            self.username = args[1]
            self.password_hash = args[2]

        elif len(kwargs) == 2:
            self.username = kwargs['username']
            self.password_hash = kwargs['password']

        elif len(kwargs) == 3:
            self.id = kwargs['id']
            self.username = kwargs['username']
            self.password_hash = kwargs['password_hash']

        else:
            raise ValueError(f'init de User espera dois ou três argumentos, mas recebeu {len(args)}\nargs')
        

    

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
    


class Like(Model):

    def __init__(self, id: int | None, post: Post | int, author: User | int, created: str | None) -> None:
        self.id = id
        self._post = post
        self._author = author
        self.created = created

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
    


ModelType = Union[User, Post, Like]