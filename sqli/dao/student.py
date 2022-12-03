import re
import logging
from typing import Optional, NamedTuple
from aiopg.connection import Connection

log = logging.getLogger(__name__)

class Student(NamedTuple):
    id: int
    name: str

    @classmethod
    def from_raw(cls, raw: tuple):
        return cls(*raw) if raw else None

    @staticmethod
    async def get(conn: Connection, id_: int):
        async with conn.cursor() as cur:
            await cur.execute(
                'SELECT id, name FROM students WHERE id = %s',
                (id_,),
            )
            r = await cur.fetchone()
            return Student.from_raw(r)

    @staticmethod
    async def get_many(conn: Connection, limit: Optional[int] = None,
                       offset: Optional[int] = None):
        q = 'SELECT id, name FROM students'
        params = {}
        if limit is not None:
            q += ' LIMIT + %(limit)s '
            params['limit'] = limit
        if offset is not None:
            q += ' OFFSET + %(offset)s '
            params['offset'] = offset
        async with conn.cursor() as cur:
            await cur.execute(q, params)
            results = await cur.fetchall()
            return [Student.from_raw(r) for r in results]

    @staticmethod
    async def create(conn: Connection, name: str):
        # Prevent sql injection by allowing only aphabetic characters
        # Fix is for this specific instance
        log.info(f'App is creating student {name}')
        name1="".join(c for c in name if c.isalpha())
        log.info(f'App removed i characters. Student name will be {name1}')
        q = ("INSERT INTO students (name) "
             "VALUES ('%(name)s')" % {'name': name1})
        async with conn.cursor() as cur:
            await cur.execute(q)


