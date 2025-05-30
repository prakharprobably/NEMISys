import psycopg2
from psycopg2 import sql
import json
import os
from . import participantdbwrapper as partdb
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

def close(curconn):
    cur,conn = curconn
    cur.close()
    conn.close()

def getMacRes(event):
    cur,conn = open()
    att=sql.Identifier(event+"ResultsFin")
    cur.execute(sql.SQL("""SELECT sid, points from {att}""").format(att=att))
    res=cur.fetchall()
    close((cur,conn))
    return res

def init():
    cur,conn = open()
    cur.execute("""SELECT sid, sname INTO Results FROM Schools""")
    conn.commit()
    cur.execute("""ALTER TABLE Results ADD COLUMN points INT DEFAULT 0""")
    events = creds["Events"]
    for event in events:
        rows = getMacRes(event)
        for row in rows:
            sid = row[0]
            points = row[1]
            cur.execute("""UPDATE Results SET points = points + %s WHERE sid = %s""", (points, sid))
    conn.commit()
    close((cur,conn))

def getEventRes(event, round="finals"):
    cur,conn = open()
    if round == "finals":
        res=sql.Identifier(event+"ResultsFin")
    else:
        res=sql.Identifier(event+"ResultsPri")
    cur.execute(sql.SQL("""SELECT * FROM {res} ORDER BY points DESC""").format(res=res))
    res=cur.fetchall()
    close((cur,conn))
    return res

def getOverallRes():
    cur,conn = open()
    cur.execute("""SELECT * FROM Results ORDER BY points DESC""")
    res = cur.fetchall()
    close((cur,conn))
    return res


def getWinners(event):
    cur,conn = open()
    res = sql.Identifier(event+"ResultsFin")
    cur.execute(sql.SQL("""SELECT * FROM {res} ORDER BY points DESC LIMIT 3"""))
    res = cur.fetchall()
    close((cur,conn))
    return res

def getOverallWinners():
    cur,conn = open()
    cur.execute(sql.SQL("""SELECT * FROM Results ORDER BY points DESC LIMIT 3"""))
    close((cur,conn))