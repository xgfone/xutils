# -*- encoding: utf-8 -*-
from __future__ import absolute_import

from six import Iterator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, object_mapper
from sqlalchemy.sql.elements import TextClause


class DB(object):
    """Manager the DB connection."""

    def __init__(self, write_connection, read_connection=None, autocommit=True,
                 expire_on_commit=False, echo=False, encoding=str("utf8"),
                 poolclass=None, pool=None, min_pool_size=2, max_pool_size=5,
                 pool_timeout=30, idle_timeout=3600):

        write_connection = self._fix_charset(write_connection, encoding)
        if read_connection:
            read_connection = self._fix_charset(read_connection, encoding)

        kwargs = {
            "echo": echo,
            "encoding": encoding,
            "poolclass": poolclass,
            "pool": pool,
            "pool_size": min_pool_size,
            "pool_timeout": pool_timeout if pool_timeout else None,
            "pool_recycle": idle_timeout,
            "max_overflow": max_pool_size - min_pool_size,
            "convert_unicode": True,
        }

        self._autocommit = autocommit
        self._expire_on_commit = expire_on_commit

        self._write_engine = self._create_engine(write_connection, kwargs)
        self._write_session_cls = self._get_session_cls(self._write_engine)

        if read_connection:
            self._read_engine = self._create_engine(read_connection, kwargs)
            self._read_session_cls = self._get_session_cls(self._read_engine)
        else:
            self._read_engine = self._write_engine
            self._read_session_cls = self._write_session_cls

    def _fix_charset(self, connection, encoding):
        if "mysql" in connection and "charset=" not in connection:
            if "?" in connection:
                return "%s&charset=%s" % (connection, encoding)
            return "%s?charset=%s" % (connection, encoding)
        return connection

    def _create_engine(self, connection, kwargs):
        if connection.startswith("sqlite:///"):
            kwargs.pop("pool_size", None)
            kwargs.pop("pool_timeout", None)
            kwargs.pop("max_overflow", None)
        return create_engine(connection, **kwargs)

    def _get_session_cls(self, engine):
        return sessionmaker(bind=engine, autocommit=self._autocommit,
                            expire_on_commit=self._expire_on_commit)

    def get_write_session(self):
        return self._write_session_cls()

    def get_read_session(self):
        return self._read_session_cls()

    def get_session(self):
        return self.get_write_session()

    def execute(self, sql, session=None, **kwargs):
        if not isinstance(sql, TextClause):
            sql = text(sql)
        return (session or self.get_session()).execute(sql, kwargs)

    def fetchall(self, sql, **kwargs):
        return self.execute(sql, self.get_read_session(), **kwargs).fetchall()

    def fetchone(self, sql, **kwargs):
        return self.execute(sql, self.get_read_session(), **kwargs).fetchone()

    def first(self, sql, **kwargs):
        return self.execute(sql, self.get_read_session(), **kwargs).first()


# Copy From OpenStack. Apache License 2.0
class ModelBase(Iterator):
    """Base class for models."""
    __tablename__ = ""
    __table_initialized__ = False

    def save(self, session):
        """Save this object."""

        # NOTE(boris-42): This part of code should be look like:
        #                       session.add(self)
        #                       session.flush()
        #                 But there is a bug in sqlalchemy and eventlet that
        #                 raises NoneType exception if there is no running
        #                 transaction and rollback is called. As long as
        #                 sqlalchemy has this bug we have to create transaction
        #                 explicitly.
        with session.begin(subtransactions=True):
            session.add(self)
            session.flush()

    def __repr__(self):
        attrs = ", ".join(("%s=%s" % (k, v) for k, v in self.items()))
        return "%s(%s)" % (self.__tablename__.title(), attrs)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __contains__(self, key):
        # Don't use hasattr() because hasattr() catches any exception, not only
        # AttributeError. We want to passthrough SQLAlchemy exceptions
        # (ex: sqlalchemy.orm.exc.DetachedInstanceError).
        try:
            getattr(self, key)
        except AttributeError:
            return False
        else:
            return True

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __iter__(self):
        columns = list(dict(object_mapper(self).columns).keys())
        return ModelIterator(self, iter(columns))

    def update(self, values):
        """Make the model object behave like a dict."""
        for k, v in values.items():
            setattr(self, k, v)

    def _as_dict(self):
        """Make the model object behave like a dict.
        Includes attributes from joins.
        """
        local = dict((key, value) for key, value in self)
        joined = dict([(k, v) for k, v in self.__dict__.items() if not k[0] == '_'])
        local.update(joined)
        return local

    def items(self):
        """Make the model object behave like a dict."""
        return self._as_dict().items()

    def keys(self):
        """Make the model object behave like a dict."""
        return [key for key, value in self.items()]


# Copy From OpenStack. Apache License 2.0
class ModelIterator(Iterator):
    def __init__(self, model, columns):
        self.model = model
        self.i = columns

    def __iter__(self):
        return self

    # In Python 3, __next__() has replaced next().
    def __next__(self):
        n = next(self.i)
        return n, getattr(self.model, n)
