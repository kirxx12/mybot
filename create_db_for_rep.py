import sqlite3 as sl
from random import shuffle
import os

class IntWithDb():
    def __init__(self) -> None:
        if not os.path.isfile('tg-rep.db'):
            self.create_db()


    def create_db(self) -> None:
        """Создание базы данных"""
        db = sl.connect("tg-rep.db")
        cur = db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quests(
                task_id INT PRIMARY KEY,
                task_desc TEXT,
                task_answer TEXT,
                done INT
            );
        """)
        db.commit()


    def add_task(self, tasks: dict) -> None:
        db = sl.connect("tg-rep.db")
        cur = db.cursor()
        for task in tasks:
            cur.execute('''
                INSERT INTO quests VALUES(?, ?, ?, ?);
            ''', task)
            db.commit()

    
    def get_task_id(self, id: int) -> str:
        db = sl.connect("tg-rep.db")
        cur = db.cursor()
        cur.execute(f"""
            SELECT task_desc FROM quests
            WHERE task_id = {id}
        """)
        answer = cur.fetchone()
        return answer[0]


    def get_count_availaible_tasks(self) -> int:
        db = sl.connect('tg-rep.db')
        cur = db.cursor()
        cur.execute("""
            SELECT count(*) FROM quests
        """)
        counts = cur.fetchone()[0]
        return counts


    def create_dict_for_add(self, path: str) -> list:
        file = open(path)
        s = file.readlines()
        task = [tuple([str(s[j]) for j in range(i * 4, i * 4 + 4)]) for i in range(len(s) // 4)]
        return task


    def check_answer(self, id: int, answer: str) -> bool:
        db = sl.connect('tg-rep.db')
        cur = db.cursor()
        cur.execute(f"""
            SELECT task_answer FROM quests
            WHERE task_id = {id}
        """)
        answer = answer.strip()
        right_answer = str(cur.fetchone()[0]).strip()
        if answer == right_answer:
            return True
        return False


    def get_random_not_done_task(self):
        db = sl.connect('tg-rep.db')
        cur = db.cursor()
        cur.execute("""
            SELECT * FROM quests
            WHERE done = 0
        """)
        tasks = cur.fetchall()
        shuffle(tasks)
        random_task = tasks[0]
        return random_task



# db = IntWithDb()
# db.add_task(db.create_dict_for_add('tasks\demo_tasks.txt'))
# print(db.get_random_not_done_task())
