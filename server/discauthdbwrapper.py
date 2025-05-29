import psycopg2
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

def open():
    conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cur = conn.cursor()
    return cur,conn

def init(cur,conn):
    cur.execute("""CREATE TABLE DiscAuth (
        pid INT PRIMARY KEY,
        username VARCHAR(32)
    )""")
    conn.commit()

def insert(cur, pid, username):
    cur.execute("""INSERT INTO DiscAuth (pid, username) VALUES (%s, %s);""", (pid, username))

def confirm(conn):
    conn.commit()

def close(curconn):
    cur, conn = curconn
    cur.close()
    conn.close()

def checkUser(curconn, username):
    cur,conn=curconn
    cur.execute("""SELECT p.name, p.class, p.event 
                   FROM discauth d 
                   JOIN participants p ON d.pid = p.pid 
                   WHERE d.username = %s""", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None:
        return False
    name, clss, event = row
    return {"name": name, "class": clss, "event": event}

if __name__ == "__main__":
    conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cur = conn.cursor()
    #init(cur,conn)
    cur.execute("""DELETE FROM DiscAuth;""")
    confirm(conn=conn)
    close((cur,conn))