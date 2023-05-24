import psycopg2


def create_db(cursor):
    cursor.execute("drop table phones;"
                   "drop table clients;"
                   "commit;")

    # создание таблиц
    cursor.execute("""
                create table phones(
                    id serial4 NOT NULL,
                    client_id int4 NOT NULL,
                    phone varchar NOT NULL,
                    CONSTRAINT phones_pk PRIMARY KEY (id)
                );
                create table clients(
                    id serial4 NOT NULL,
                    name varchar(50) NOT NULL,
                    surname varchar(100) NOT NULL,
                    email varchar(100) NOT NULL,
                    CONSTRAINT clients_pkey PRIMARY KEY (id) 
                );
                ALTER TABLE phones ADD CONSTRAINT phones_fk FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE ON UPDATE CASCADE;
                commit;
                """)


def add_client(cursor, name, surname, email, phones=None):
    cursor.execute("""
                insert into clients(name, surname, email)
                values (%s, %s, %s);
                commit;
                select id from clients where name = %s and surname = %s and email = %s;
            """, (name, surname, email, name, surname, email))
    if phones is not None:
        client_id = cursor.fetchone()[0]
        for p in phones:
            add_phone(cursor, client_id, p)


def add_phone(cursor, client_id, phone):
    cursor.execute("""
                insert into phones (client_id, phone)
                values (%s, %s);
                commit;
            """, (client_id, phone))


def del_phone(cursor, client_id, phone=None):
    if phone is None:
        cursor.execute("""
                    delete from phones WHERE client_id=%s;
                    commit;
                """, (client_id,))
    else:
        cursor.execute("""
                    delete from phones WHERE client_id=%s and phone=%s;
                    commit;
                """, (client_id, phone))


def change_client(cursor, client_id, name=None, surname=None, email=None, phones=None):
    if name is not None:
        cursor.execute("""
                    update clients set name=%s where id=%s;
                    commit;
                """, (name, client_id))
    if surname is not None:
        cursor.execute("""
                    update clients set surname=%s where id=%s;
                    commit;
                """, (surname, client_id))
    if email is not None:
        cursor.execute("""
                    update clients set  email=%s where id=%s;
                    commit;
                """, (email, client_id))
    if phones is not None:
        del_phone(cursor, client_id)
        for p in phones:
            add_phone(cursor, client_id, p)


def del_client(cursor, client_id):
    cursor.execute("""
                delete from clients where id=%s;
                commit;
            """, (client_id,))


def add_find_option(paramText, findText):
    use_like = findText.__contains__("%")
    if use_like:
        return f"{paramText} like '{findText}'"
    return f"{paramText} = '{findText}'"


def find_client(cursor, name=None, surname=None, email=None, phone=None):
    find_options = []
    if name is not None:
        find_options.append(add_find_option("c.name", name))
    if surname is not None:
        find_options.append(add_find_option("c.surname", surname))
    if email is not None:
        find_options.append(add_find_option("c.email", email))
    if phone is not None:
        find_options.append(add_find_option("p.phone", phone))
    f_options = " and ".join(find_options)
    cursor.execute("select c.id, c.name, c.surname, c.email, p.phone from clients c, phones p where c.id = "
                   "p.client_id and "+f_options)
    return cursor.fetchall()


if __name__ == '__main__':
    with psycopg2.connect(database="postgres", user="postgres", password="postgres") as conn:
        with conn.cursor() as cur:
            create_db(cur)
            add_client(cur, 'Иван', 'Иванов', 'IvanovII@yandex.ru', ["+7-111-111-11-11","+7-222-222-22-22"])
            add_client(cur, 'Сидр', 'Сидоров', 'SidorovSS@yandex.ru', ["+7-333-333-33-33"])
            add_phone(cur, 1, '+7-987-654-32-10')
            add_phone(cur, 2, '+7-987-654-32-11')
            change_client(cur, 2, 'Петр', 'Петров', 'PetrovPP@yandex.ru',["+7-444-444-44-44","+7-555-555-55-55"])
            del_phone(cur, 1, '+7-111-111-11-11')
            del_client(cur, 2)
            for s in find_client(cur, surname="%ов", email="%yandex.ru", phone="+7%"):
                print(s)
    conn.close()
