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

def open():
    con = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cur = con.cursor()
    return cur,con

def markAtt(cur, event, pid, attendance):
    att=sql.Identifier(event+"Attendance")
    cur.execute(sql.SQL("""UPDATE {att} SET attendance=%s WHERE pid = %s""").format(att=att), (attendance, pid))
    print(f"marked {pid} as {attendance}")

def markRes(cur, event, sid, points, finals):
    if not finals:
        res=sql.Identifier(event+"ResultsPri")
    else:
        res=sql.Identifier(event+"ResultsFin")
    cur.execute(sql.SQL("""UPDATE {att} SET attendance=%s WHERE pid = %s""").format(res=res), (attendance, pid))
    print(f"marked {points} for {sid}")

def getAttTable(event):
    cur, conn = open()
    att=sql.Identifier(event+"Attendance")
    cur.execute(sql.SQL("""SELECT * FROM {att}""").format(att=att))
    head = [desc[0] for desc in cur.description]
    data = [head]+list(cur.fetchall())
    close((cur,conn))
    return data

def getResTable(event, finals):
    cur, conn = open()
    if finals:
        res=sql.Identifier(event+"ResultsFin")
    else:
        res=sql.Identifier(event+"ResultsPri")
    cur.execute(sql.SQL("""SELECT * FROM {att}""").format(att=att))
    head = [desc[0] for desc in cur.description]
    data = [head]+list(cur.fetchall())
    close((cur,conn))
    return data

def close(curconn):
    cur,conn=curconn
    cur.close()
    conn.close()

if __name__ == "__main__":
    cur,conn = open()
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE';
    """)
    for table in cur.fetchall():
        print(table[0])
    close((cur,conn))