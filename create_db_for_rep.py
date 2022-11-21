import sqlite3 as sl
from random import shuffle
import os
import re

class IntWithDb():
    def __init__(self, path: str = 'tasks\mat_demo_tasks.txt') -> None:
        if not os.path.isfile('db/tg-rep.db'):
            self.create_db('m_tasks')
            self.create_db('i_tasks')
            self.add_task(self.create_dict_for_add(path))


    def create_db(self, base: str) -> None:
        """Создание базы данных"""
        db = sl.connect("db/tg-rep.db")
        cur = db.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {base}(
                task_id INT PRIMARY KEY,
                task_desc TEXT,
                task_answer TEXT,
                path_to_image INT
            );
        """)
        db.commit()


    def add_task(self, tasks: dict, base: str) -> None:
        db = sl.connect("db/tg-rep.db")
        cur = db.cursor()
        for task in tasks:
            cur.execute(f'''
                INSERT INTO {base} VALUES(?, ?, ?, ?);
            ''', task)
            db.commit()

    
    def get_task_id(self, id: int, base: str) -> str:
        db = sl.connect("db/tg-rep.db")
        cur = db.cursor()
        cur.execute(f"""
            SELECT task_desc FROM {base}
            WHERE task_id = {id}
        """)
        answer = cur.fetchone()
        return answer[0]


    def get_count_availaible_tasks(self, base: str) -> int:
        db = sl.connect('db/tg-rep.db')
        cur = db.cursor()
        cur.execute(f"""
            SELECT count(*) FROM {base}
        """)
        counts = cur.fetchone()[0]
        return counts


    def create_dict_for_add(self, path: str) -> list:
        file = open(path)
        s = file.readlines()
        reg = re.compile('\n')
        task = [tuple([reg.sub('', s[j]) for j in range(i * 4, i * 4 + 4)]) for i in range(len(s) // 4)]
        print(task)
        return task


    def check_answer(self, id: int, answer: str, chat_id: str, base: str) -> bool:
        db = sl.connect('db/tg-rep.db')
        cur = db.cursor()
        cur.execute(f"""
            SELECT task_answer FROM {base}
            WHERE task_id = {id}
        """)
        answer = answer.strip()
        right_answer = str(cur.fetchone()[0]).strip()
        if answer == right_answer:
            cur.execute(f"""
                UPDATE {chat_id}
                SET done = 1
                WHERE task_id = {id}
            """)
            db.commit()
            return True
        return False


    def get_random_not_done_task(self, chat_id: str, base: str):
        db = sl.connect('db/tg-rep.db')
        cur = db.cursor()
        cur.execute(f"""
            SELECT * FROM {chat_id}
            WHERE done = 0
        """)
        tasks = cur.fetchall()
        if len(tasks) < 2:
            return ('0', 'Задания кончились')
        shuffle(tasks)
        random_task_id = tasks[0][0]
        cur.execute(f"""
            SELECT * FROM {base}
            WHERE task_id = {random_task_id}
        """)
        random_task = cur.fetchone()
        print(random_task)
        return random_task


    def create_db_for_user(self, chat_id: str, base: str) -> None:
        """Создает БД для пользователя с отметками о выполненных заданиях"""
        db = sl.connect('db/tg-rep.db')
        cur = db.cursor()
        chat_id = str(chat_id)
        print(chat_id)
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {chat_id}(
                task_id INT,
                done INT,
                FOREIGN KEY (task_id) REFERENCES {base}(task_id)
            );
        """)
        db.commit()
        cur.execute(f"""
            SELECT count(*) FROM {chat_id}
        """)
        count = cur.fetchone()[0]
        print(count)
        if count == 0:
            cur.execute(f"""
                SELECT * FROM {base}
            """)
            tasks_id = cur.fetchall()
            print(tasks_id)
            for task_id in tasks_id:
                val = (task_id[0], 0)
                cur.execute(f"""
                    INSERT INTO {chat_id} VALUES(?, ?);
                """, val)
                db.commit()


    def check_db(self, name: str) -> set:
        db = sl.connect('db/tg-rep.db')
        cur = db.cursor()
        cur.execute(f"""
            SELECT * FROM {name}
        """)
        data = cur.fetchall()
        return data

    
    def delete_db(self, chat_id: str):
        """Удаление таблицы ученика"""
        db = sl.connect('db/tg-rep.db')
        cur = db.cursor()
        cur.execute(f"""
            DROP TABLE IF EXISTS {chat_id}
        """)
        db.commit()


# db = IntWithDb()
# db.add_task(db.create_dict_for_add('tasks\info_demo_task.txt'), 'i_tasks')
# print(db.create_db_for_user('i1', 'i_tasks'))
# task = db.get_random_not_done_task('i4', 'i_tasks')
# print(task[1])
# if db.check_answer(task[0], input(), 'i1', 'i_tasks'):
#     print('Отлично')
# else:
#     print('Не очень(')
