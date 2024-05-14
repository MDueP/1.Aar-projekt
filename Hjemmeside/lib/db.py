import sqlite3
from time import sleep
conn = sqlite3.connect('database/users.db')
cur = conn.cursor()

def commit_data(username, password):
    query_users = """INSERT INTO BASIC, (USERNAME, PASSWORD) VALUES(?,?)"""
    cur.execute(query_users, )
def get_data(number_of_rows):
    queryuser = """SELECT USERNAME FROM USERS"""
    querypass = """SELECT PASSWORD FROM USERS"""
    try:
        cur.execute(query)
    except sqlite3.Error as sql_e:
        print(f"sqlite error occured: {sql_e}")
        conn.rollback()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
        sleep(1)