import sqlite3 as sq


def sql_start():
    global base, cur
    base = sq.connect('data_base/base_users.db')
    cur = base.cursor()
    if base:
        print('Data base connect OK!')
    base.execute('CREATE TABLE IF NOT EXISTS data(id INT PRIMARY KEY, username TEXT, '
                 'requests_left INT,  days_left INT, '
                 'human TEXT, ia TEXT)')
    base.commit()
    # cur.execute('PRAGMA max_page_count = 21474836460')


async def sql_add_command(id, username):
    cur.execute('INSERT INTO data VALUES (?, ?, ?, ?, ?, ?)', (id, username, 5, 0, ' ', ' '))
    base.commit()


async def sql_read_id(id):
    return cur.execute('SELECT * FROM data WHERE id == ?', (id,)).fetchall()


async def sql_read_left():
    return cur.execute('SELECT id, days_left, requests_left FROM data').fetchall()


async def sql_update_text(human, ia, id):
    cur.execute('UPDATE  data SET human = ?, ia = ? WHERE id == ?', (human, ia, id))
    base.commit()


async def sql_update_left(left_num, id, name):
    if name in ('requests_left', 'days_left'):
        cur.execute('UPDATE  data SET {} = ? WHERE id == ?'.format(name), (left_num, id))
    else:
        print('No update...\n')
        return
    base.commit()

