import psycopg2



def create_db(conn):
    cur = conn.cursor()
    cur.execute("drop table clients")

    # создание таблиц
    cur.execute("""
                create table if not exists clients(
                    id serial primary key,
                    name text not null,
                    surname text not null,
                    email text not null,
                    phone text
                );
                """)
    conn.commit()


def create_clients(conn, name, surname, email, phone):
    cur = conn.cursor()
    # наполнение таблиц
    cur.execute("""
                insert into clients(name, surname, email, phone)
                values (%s, %s, %s, %s);
            """, (name, surname, email, phone))
    conn.commit()


def add_client(conn, name, surname, email, phone=None):
    cur = conn.cursor()
    cur.execute("""
                insert into clients(name, surname, email, phone)
                values (%s, %s, %s, %s);
            """, (name, surname, email, phone))
    conn.commit()


def add_phone(conn, id, phone_add: str = None):
    cur = conn.cursor()
    cur.execute("""
                select phone from clients WHERE id=%s;
            """, (id,))
    exist_phone = cur.fetchone()
    if len(exist_phone) > 0 and exist_phone[0] is not None:
        phone_add = exist_phone[0] + "\n" + phone_add
    cur.execute("""
                update clients set phone=%s WHERE id=%s
            """, (phone_add, id))
    conn.commit()


def change_client(conn, id, name, surname, email, phone):
    cur = conn.cursor()
    cur.execute("""
                update clients set name=%s, surname=%s, email=%s, phone=%s  where id=%s;
            """, (id, name, surname, email, phone))
    conn.commit()


def del_phone(conn, id, phone):
    cur = conn.cursor()
    cur.execute("""
                select phone from clients WHERE id=%s;
            """, (id,))
    exist_phones = cur.fetchone()
    if len(exist_phones) > 0 and exist_phones[0] is not None:
        exist_phone: str = exist_phones[0]
        phones = exist_phone.split("\n")
        if phones.__contains__(phone):
            phones.remove(phone)
            phone = "\n".join(phones)

    cur.execute("""
                update clients set phone=%s WHERE id=%s
            """, (phone, id))
    conn.commit()


def del_client(conn, id):
    cur = conn.cursor()
    cur.execute("""
                delete from clients where id=%s;
            """, (id,))
    conn.commit()


def add_find_option(paramText, findText):
    use_like = findText.__contains__("%")
    if use_like:
        return f"{paramText} like '{findText}'"
    return f"{paramText} = '{findText}'"


def find_client(conn, name=None, surname=None, email=None, phone=None):
    cur = conn.cursor()
    find_options = []
    if name is not None:
        find_options.append(add_find_option("name", name))
    if surname is not None:
        find_options.append(add_find_option("surname", surname))
    if email is not None:
        find_options.append(add_find_option("email", email))
    if phone is not None:
        find_options.append(add_find_option("phone", phone))
    f_options = " and ".join(find_options)
    cur.execute(f"select * from clients WHERE {f_options};")
    return cur.fetchall()


with psycopg2.connect(database="test_db", user="postgres", password="postgres") as conn:
    create_db(conn)
    create_clients(conn, 'Иван', 'Иванов', 'IvanovII@yandex.ru', '+7-222-234-56-78')
    add_client(conn, 'Сидр', 'Сидоров', 'SidorovSS@yandex.ru')
    add_phone(conn, 1, '+7-987-654-32-10')
    add_phone(conn, 1, '+7-987-654-32-11')
    change_client(conn, 'Петр', 'Петров', 'PetrovPP@yandex.ru', '+7-123-456-78-90', 2)
    del_phone(conn, 1, '+7-222-234-56-78')
    del_client(conn, 1)
    for s in find_client(conn, surname="%ов", email="%yandex.ru", phone="+7%"):
        print(s)

conn.close()
