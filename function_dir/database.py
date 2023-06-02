import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()

db = psycopg2.connect(user="postgres",
                      password=os.getenv("PASSWORD_DB"),
                      host="127.0.0.1",
                      port="5432",
                      database="SenderPhoto")
cursor = db.cursor()

async def add_user(user_id):
    cursor.execute("SELECT * FROM users WHERE tg_id = %s", [str(user_id)])
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (tg_id) "
                       "VALUES ({id})".format(id=str(user_id)))
        db.commit()

async def get_users():
    cursor.execute("SELECT tg_id FROM users")
    users = cursor.fetchall()
    user_list = []
    for user in users:
        user_list.append(user[0])
    return user_list

