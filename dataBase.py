import sqlite3
class DB:
    def __init__(self):
        self.conn = sqlite3.connect('users.db', check_same_thread=False)
        self.c = self.conn.cursor()
        self.c.execute("PRAGMA foreign_keys = ON")
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS users (
                id integer primary key, tg_id integer, username text, first_name text, last_name text
            )''')
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS tempUsers (
                id integer primary key, tg_id integer, username text, first_name text, last_name text
            )''')
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS machs (
                id integer primary key, title text, image text, stopped bool, dateCreate datetime
            )''')
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS usersMaches (
                user INTEGER REFERENCES users (id) ON DELETE CASCADE,
                mach INTEGER REFERENCES machs (id) ON DELETE CASCADE,
                messageId INTEGER,
                suscribe BOOL
            )''')
        self.c.execute(
            """CREATE TABLE IF NOT EXISTS info_matchs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                m_id INTEGER REFERENCES machs (id) ON DELETE CASCADE,
                info TEXT
            );""")
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS sended_info (
            u_id INTEGER REFERENCES users (id) ON DELETE CASCADE,
            i_id INTEGER REFERENCES info_matchs (id) ON DELETE CASCADE
            );''')
        self.conn.commit()

    def insert_data_in_users(self, tg_id, username, first_name, last_name):
        self.c.execute('''INSERT INTO users(tg_id, username, first_name, last_name) VALUES (?, ?, ?, ?)''',
                       (tg_id, username, first_name, last_name))
        self.conn.commit()

    def insert_data_in_tempUsers(self, tg_id, username, first_name, last_name):
        self.c.execute('''INSERT INTO tempUsers(tg_id, username, first_name, last_name) VALUES (?, ?, ?, ?)''',
                       (tg_id, username, first_name, last_name))
        self.conn.commit()

    def insert_data_in_machs(self, title, image, stopped, dateCreate):
        self.c.execute('''INSERT INTO machs(title, image, stopped, dateCreate) VALUES (?, ?, ?, ?)''',
                       (title, image, stopped, dateCreate))
        self.conn.commit()

    def suscribe(self, user_id, m_id):
        self.c.execute('UPDATE usersMaches set suscribe=1 WHERE user = ? AND mach = ?',
                       (user_id, m_id))
        self.conn.commit()

    def insert_data_in_info_match(self, m_id, info):
        self.c.execute('''INSERT INTO info_matchs(m_id, info) VALUES (?, ?)''',
                       (m_id, info))
        self.conn.commit()

    def check_in_table(self, user_id):
        self.c.execute("SELECT tg_id FROM users WHERE tg_id = ?", (user_id,))
        if self.c.fetchone() is None:
            return True
        else:
            return False

    def get_user_id(self, tg_id):
        self.c.execute("SELECT id FROM users WHERE tg_id = ?", (tg_id,))
        return self.c.fetchone()[0]

    def get_all_users_id(self):
        self.c.execute("SELECT tg_id FROM users")
        res = self.c.fetchall()
        for i in range(len(res)):
            res[i] = res[i][0]
        return res

    def insert_user(self, id):
        self.c.execute('''INSERT INTO users (tg_id, username, first_name, last_name)
                          SELECT tg_id, username, first_name, last_name
                          from tempUsers where id=?
                       ''', (id,))
        self.c.execute('''DELETE FROM tempUsers where id = ?''', (id, ))
        self.conn.commit()

    def get_all_temp_users(self):
        self.c.execute("SELECT first_name, username, id FROM tempUsers")
        res = self.c.fetchall()
        return res

    def get_all_users(self):
        self.c.execute("SELECT first_name, username, id FROM users")
        res = self.c.fetchall()
        return res

    def check_in_table_temp(self, user_id):
        self.c.execute("SELECT tg_id FROM tempUsers WHERE tg_id = ?", (user_id,))
        if self.c.fetchone() is None:
            return True
        else:
            return False

    def insert_many_in_usersMatchs(self, data):
        query = '''INSERT INTO usersMaches(user, mach, messageId, suscribe) VALUES (?, ?, ?, ?)'''
        self.c.executemany(query, data)
        self.conn.commit()

    def get_user_by_table_id(self, id):
        self.c.execute('SELECT tg_id FROM users WHERE id = ?', (id,))
        res = self.c.fetchone()[0]
        if res:
            return res
        else:
            return []

    def describe(self, user, mach):
        self.c.execute('UPDATE usersMaches set suscribe=0 WHERE user = ? AND mach = ?', (user, mach,))
        self.conn.commit()

    def sended_info_add(self, u_id, i_id):
        self.c.execute('INSERT INTO sended_info(u_id, i_id) VALUES (?, ?)', (u_id, i_id))
        self.conn.commit()

    def sended_info_many_add(self, records):
        query = 'INSERT INTO sended_info(u_id, i_id) VALUES (?, ?);'
        self.c.executemany(query, records)
        self.conn.commit()

    def delete_user(self, user_id):
        self.c.execute("DELETE from users where tg_id = ?", (user_id,))
        self.conn.commit()

    def delete_user_by_table(self, user_id):
        self.c.execute("DELETE from users where id = ?", (user_id,))
        self.conn.commit()

    def get_maches(self):
        self.c.execute("SELECT id, title from machs WHERE stopped = 0")
        return self.c.fetchall()

    def get_sus_machesUsers_by_machid(self, id):
        self.c.execute('SELECT messageId, user FROM usersMaches WHERE mach = ? AND suscribe=1', (id,))
        return self.c.fetchall()

    def get_machesUsers_by_machid(self, id):
        self.c.execute('SELECT messageId, user FROM usersMaches WHERE mach = ?', (id,))
        return self.c.fetchall()

    def set_stopped_by_id(self, id):
        self.c.execute('UPDATE machs set stopped = 1 WHERE id = ?', (id,))
        self.conn.commit()

    def get_machname_by_id(self, id):
        self.c.execute("SELECT title from machs WHERE id = ?", (id,))
        return self.c.fetchone()[0]

    def get_match_name_by_id(self, id):
        self.c.execute("SELECT title from machs WHERE id = ?", (id,))
        return self.c.fetchone()[0]

    def get_no_send_info(self, u_id, m_id):
        self.c.execute('''
            SELECT info, id FROM info_matchs 
            WHERE NOT EXISTS (SELECT u_id FROM sended_info WHERE u_id == ? AND i_id == info_matchs.id) AND m_id == ?
        ''', (u_id, m_id))
        return self.c.fetchall()