#!/usr/bin/env python3
from secrets import token_urlsafe
from sqlite3 import IntegrityError
from dataclasses import dataclass

import databases
import config

@dataclass
class User:
    uid: str
    balance: int
    csrf: str
    bankrupt: bool

class Database:
    def __init__(self, url):
        self.db = databases.Database(url)

    async def connect(self):
        return await self.db.connect()

    async def init_user_table(self):
        await self.db.execute('''
CREATE TABLE IF NOT EXISTS users (
    uid TEXT PRIMARY KEY UNIQUE NOT NULL,
    balance INTEGER NOT NULL,
    csrf TEXt NOT NULL,
    bankrupt INTEGER DEFAULT 0,
    CHECK (balance >= 0)
)''')
    async def init_stat_table(self):
        await self.db.execute('''
CREATE TABLE IF NOT EXISTS stats (
    id INTEGER PRIMARY KEY,
    user_bankruptcy INTEGER DEFAULT 0,
    ponzi_max_balance INTEGER DEFAULT 0
)''')

    async def create_stat(self):
        await self.db.execute('INSERT OR IGNORE INTO stats VALUES (0, 0, :b)', dict(b=config.ponzi_init_balance))

    async def get_stats(self):
        t = tuple(await self.db.fetch_one('SELECT user_bankruptcy, ponzi_max_balance FROM stats'))
        t += tuple(await self.db.fetch_one('SELECT count(*) FROM users'))
        t += ((await self.get_user(config.ponzi_uid)).balance, )
        return t

    async def disconnect(self):
        return await self.db.disconnect()

    async def create_user(self, uid, balance):
        csrf = token_urlsafe(16)
        await self.db.execute('INSERT OR IGNORE INTO users VALUES (:u, :b, :c, 0)', dict(u=uid, b=balance, c=csrf))
        return User(uid, balance, csrf, 0)

    async def get_user(self, uid):
        row = await self.db.fetch_one('SELECT uid, balance, csrf, bankrupt FROM users WHERE uid == :uid', dict(uid=uid))
        return None if row is None else User(*row)

    async def update_user_csrf(self, uid):
        return await self.db.execute('UPDATE users SET csrf = :c WHERE uid = :u', dict(c=token_urlsafe(16), u=uid))

    async def transfer(self, src_uid, dst_uid, balance):
        try:
            async with self.db.transaction():
                await self.db.execute('UPDATE users SET balance = balance - :b WHERE uid = :src', dict(b=balance, src=src_uid))
                await self.db.execute('UPDATE users SET balance = balance + :b WHERE uid = :dst', dict(b=balance, dst=dst_uid))
            if dst_uid == config.ponzi_uid:
                ponzi = await self.get_user(config.ponzi_uid)
                await self.db.execute('UPDATE stats SET ponzi_max_balance = max(ponzi_max_balance, :b)', dict(b=ponzi.balance))
            return True
        except IntegrityError:
            if src_uid == config.ponzi_uid:
                await self.db.execute('UPDATE stats SET user_bankruptcy = user_bankruptcy + 1')
                await self.db.execute('UPDATE users SET bankrupt = 1 WHERE uid = :uid', dict(uid=dst_uid))
        return False
