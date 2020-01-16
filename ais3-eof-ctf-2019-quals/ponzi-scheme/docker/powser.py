#!/usr/bin/env python3
import sqlite3
from time import time
import hashlib
import secrets


class Powser:
    def __init__(
            self,
            db_path,
            difficulty=16,
            clean_expired_rows_per=1000,
            prefix_length=16,
            default_expired_time=None,
            min_refresh_time=None
        ):
        self.db = sqlite3.connect(db_path)
        self.difficulty = difficulty
        self.clean_expired_rows_per = clean_expired_rows_per
        self.prefix_length = prefix_length
        if default_expired_time is None:
            self.default_expired_time = max(600, 2**(difficulty-16))
        else:
            self.default_expired_time = default_expired_time
        if min_refresh_time is None:
            self.min_refresh_time = self.default_expired_time // 2
        else:
            self.min_refresh_time = min_refresh_time

        self._insert_count = 0

        if not self._table_exists():
            self._create_table()

    def get_challenge(self, ip):
        row = self.db.execute('SELECT prefix, valid_until FROM pow WHERE ip=?', (ip, )).fetchone()
        if row is None:
            return self._insert_client(ip)

        prefix, valid_until = row
        time_remain = valid_until - int(time())
        if time_remain <= self.min_refresh_time:
            return self._insert_client(ip)
        return prefix, time_remain

    def verify_client(self, ip, answer, with_msg=False):
        row = self.db.execute('SELECT valid_until, prefix FROM pow WHERE ip=?', (ip, )).fetchone()
        if row is None:
            return (False, 'Please get a new PoW challenge.') if with_msg else False
        valid_until, prefix = row
        if time() > valid_until:
            return (False, 'The PoW challenge is expired.') if with_msg else False
        result = self._verify_hash(prefix, answer)
        if not result:
            return (False, 'The hash is incorrect.') if with_msg else False
        self._insert_client(ip)
        return (True, 'Okay.') if with_msg else True

    def clean_expired(self):
        self.db.execute('DELETE FROM pow WHERE valid_until < strftime("%s", "now")')
        self.db.commit()

    def close(self):
        self.db.close()

    def _verify_hash(self, prefix, answer):
        h = hashlib.sha256()
        h.update((prefix + answer).encode())
        bits = ''.join(bin(i)[2:].zfill(8) for i in h.digest())
        zeros = '0' * self.difficulty
        return bits[:self.difficulty] == zeros

    def _insert_client(self, ip):
        self._insert_count += 1
        if self.clean_expired_rows_per > 0 and self._insert_count % self.clean_expired_rows_per == 0:
            self.clean_expired()
        prefix = secrets.token_urlsafe(self.prefix_length).replace('-', '_')
        valid_until = int(time()) + self.default_expired_time
        data = {
            'ip': ip,
            'valid_until': valid_until,
            'prefix': prefix
        }
        self.db.execute('INSERT OR REPLACE INTO pow VALUES(:ip, :valid_until, :prefix)', data)
        self.db.commit()
        return prefix, valid_until - int(time())

    def _table_exists(self):
        row = self.db.execute('SELECT COUNT(*) FROM sqlite_master WHERE type=? AND name=?', ('table', 'pow')).fetchone()
        return bool(row[0])

    def _create_table(self):
        sql = '''
            CREATE TABLE pow (
                ip TEXT PRIMARY KEY,
                valid_until INTEGER,
                prefix TEXT
            )
        '''
        self.db.execute(sql)
        self.db.commit()
