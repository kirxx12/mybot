import sqlite3 as sl
from random import shuffle
import os
import re

class IntWithDb():
    def __init__(self) -> None:
        if not os.path.isfile('db/tg-rep.db'):
            self.create_db()
            self.add_task(self.create_dict_for_add('tasks\demo_tasks.txt'))


    def create_db(self) -> None:
        """Создание базы данных"""
        db = sl.connect("db/tg-rep.db")
        cur = db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quests(
                task_id INT PRIMARY KEY,
                task_desc TEXT,
                task_answer TEXT,
                path_to_image INT
            );
        """)
        db.commit()


    def add_task(self, tasks: dict) -> None:
        db = sl.connect("db/tg-rep.db")
        cur = db.cursor()
        for task in tasks:
            cur.execute('''
                INSERT INTO quests VALUES(?, ?, ?, ?);
            ''', task)
            db.commit()

    
    def get_task_id(self, id: int) -> str:
        db = sl.connect("db/tg-rep.db")
        cur = db.cursor()
        cur.execute(f"""
            SELECT task_desc FROM quests
            WHERE task_id = {id}
        """)
        answer = cur.fetchone()
        return answer[0]


    def get_count_availaible_tasks(self) -> int:
        db = sl.connect('db/tg-rep.db')
        cur = db.cursor()
        cur.execute("""
            SELECT count(*) FROM quests
        """)
        counts = cur.fetchone()[0]
        return counts


    def create_dict_for_add(self, path: str) -> list:
        file = open(path)
        s = file.readlines()
        reg = re.compile('\n')
        task = [tuple([reg.sub('', s[j]) for j in range(i * 4, i * 4 + 4)]) for i in range(len(s) // 4)]
        return task


    def check_answer(self, id: int, answer: str, chat_id: str) -> bool:
        db = sl.connect('db/tg-rep.db')
        cur = db.cursor()
        cur.execute(f"""
            SELECT task_answer FROM quests
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


    def get_random_not_done_task(self, chat_id):
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
            SELECT * FROM quests
            WHERE task_id = {random_task_id}
        """)
        random_task = cur.fetchone()
        return random_task


    def create_db_for_user(self, chat_id: str) -> None:
        """Создает БД для пользователя с отметками о выполненных заданиях"""
        db = sl.connect('db/tg-rep.db')
        cur = db.cursor()
        chat_id = str(chat_id)
        print(chat_id)
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {chat_id}(
                task_id INT,
                done INT,
                FOREIGN KEY (task_id) REFERENCES quests(task_id)
            );
        """)
        db.commit()
        cur.execute(f"""
            SELECT count(*) FROM {chat_id}
        """)
        count = cur.fetchone()[0]
        print(count)
        if count == 0:
            cur.execute("""
                SELECT * FROM quests
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
        db = sl.connect('tg-rep.db')
        cur = db.cursor()
        cur.execute(f"""
            SELECT * FROM {name}
        """)
        data = cur.fetchall()
        return data


# db = IntWithDb()
# db.add_task(db.create_dict_for_add('tasks\demo_tasks.txt'))
# print(db.create_db_for_user('m1'))
# task = db.get_random_not_done_task('m1')
# print(task[1])
# if db.check_answer(task[0], input(), 'm1'):
#     print('Отлично')
# else:
#     print('Не очень(')
