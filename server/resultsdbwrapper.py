import psycopg2
from psycopg2 import sql
import json
import os
from . import participantdbwrapper as partdb
from . import eventdbwrapper as evdb
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

def getWinners(event):
    cur,conn = open()
    win = sql.Identifier(event+"Winners")
    cur.execute(sql.SQL("""SELECT * FROM {wins} ORDER BY rank LIMIT 3""").format(wins=win))
    res = cur.fetchall()
    close((cur,conn))
    return res

def init():
    cur,conn = open()
    cur.execute("""DROP TABLE IF EXISTS Results""")
    conn.commit()
    cur.execute("""SELECT sid, sname INTO Results FROM Schools""")
    conn.commit()
    cur.execute("""ALTER TABLE Results 
    ADD COLUMN points INT DEFAULT 0,
    ADD COLUMN firsts INT DEFAULT 0,
    ADD COLUMN "seconds" INT DEFAULT 0,
    ADD COLUMN thirds INT DEFAULT 0;""")
    events = creds["Events"]
    for event in events:
        rows = getMacRes(event)
        for row in rows:
            sid = row[0]
            points = row[1]
            cur.execute("""UPDATE Results SET points = points + %s WHERE sid = %s""", (points, sid))
        rows = getWinners(event=event)
        for row in rows:
            rank = int(row[0])
            sid = row[1].rstrip()
            if rank == 1:
                cur.execute("""UPDATE Results SET firsts = firsts + 1 WHERE sid = %s""", (sid,))
                conn.commit()
            if rank == 2:
                cur.execute("""UPDATE Results SET "seconds" = "seconds" + 1 WHERE sid = %s""", (sid,))
                conn.commit()
            if rank == 3:
                cur.execute("""UPDATE Results SET thirds = thirds + 1 WHERE sid = %s""", (sid,))
                conn.commit()
            
    conn.commit()
    close((cur,conn))

def getEventRes(event, round="finals"):
    cur,conn = open()
    if round == "finals":
        res=sql.Identifier(event+"ResultsFin")
        cur.execute(sql.SQL("""SELECT * FROM {res} ORDER BY points DESC, pref DESC""").format(res=res))
    else:
        res=sql.Identifier(event+"ResultsPri")
        cur.execute(sql.SQL("""SELECT * FROM {res} ORDER BY points DESC""").format(res=res))
    head = [desc[0] for desc in cur.description]
    data = [head] + list(cur.fetchall())
    close((cur,conn))
    return data
    close((cur,conn))
    return res

def getOverallRes():
    cur,conn = open()
    cur.execute("""SELECT * FROM Results ORDER BY points DESC, firsts DESC, "seconds" DESC, thirds DESC""")
    head = [desc[0] for desc in cur.description]
    data = [head] + list(cur.fetchall())
    close((cur,conn))
    return data
    close((cur,conn))
    return res

def getOverallWinners():
    cur,conn = open()
    cur.execute(sql.SQL("""SELECT sid, sname FROM Results ORDER BY points DESC, firsts DESC, "seconds" DESC, thirds DESC LIMIT 3"""))
    head = [desc[0] for desc in cur.description]
    data = [head] + list(cur.fetchall())
    close((cur,conn))
    return data
    close((cur,conn))
    return res