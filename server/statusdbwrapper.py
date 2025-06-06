import psycopg2
from psycopg2 import sql
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDS_PATH = os.path.join(BASE_DIR, 'creds.json')

with open(CREDS_PATH, 'r') as f:
    creds = json.load(f)

host=creds["host"]
dbname=creds["dbname"]
user=creds["user"]
password=creds["password"]
port=creds["port"]

statuses = {
    0 : "Waiting for registrations",
    1 : "On standby for preliminaries",
    2 : "Preliminaries in progress",
    3 : "On standby for finals",
    4 : "Finals in progress",
    5 : "Concluded"
}

def open():
    con = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cur = con.cursor()
    return cur,con

def close(curconn):
    cur,conn=curconn
    cur.close()
    conn.close()

def init():
    cur,conn = open()
    try:
        cur.execute("""CREATE TABLE IF NOT EXISTS Status(
        event VARCHAR(20),
        status INT DEFAULT 0)""")
        events = creds["Events"]
        conn.commit()
        for event in events:
            cur.execute("""INSERT INTO Status VALUES (%s, 0)""", (event,))
        conn.commit()
    finally:
        close((cur,conn))

def setStatus(curconn, event, status):
    cur,conn = curconn
    cur.execute("""UPDATE Status SET status = %s WHERE event = %s""", (status, event))

def getStatusTable():
    cur,conn = open()
    try:
        cur.execute("""SELECT * FROM Status""")
        return cur.fetchall()
    except:
        return []
    finally:
        close((cur,conn))

def setStatusIfLower(curconn, status):
    cur,conn=curconn
    cur.execute("""UPDATE Status SET status = %s WHERE status < %s""", (status, status))
    conn.commit()

def reset():
    cur,conn = open()
    cur.execute("""UPDATE Status SET status = 0""")
    conn.commit()
    close((cur,conn))

if __name__ == '__main__':
    init()