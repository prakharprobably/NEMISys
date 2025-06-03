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


def getWinningParts(event):
    cur, conn = open()
    win = sql.Identifier(event + "Winners")
    cur.execute(sql.SQL("SELECT rank, sname, sid FROM {win} ORDER BY rank LIMIT 3").format(win=win))
    winners = cur.fetchall()
    out = {}
    data = {}
    try:
        for winner in winners:
            rank, sname, sid = winner
            cur.execute(sql.SQL("""
                SELECT name, class
                FROM participants p
                JOIN {win} AS w ON p.sid = w.sid
                WHERE p.event = %s AND p.attendance = TRUE AND w.sid = %s
            """).format(win=win), (event, sid))
            participants = cur.fetchall()
            part_list = [{"name": name, "class": clss} for name, clss in participants]
            data[rank] = {"name": sname, "participants": part_list}
            print(event, rank, sname, part_list)
        out[event] = data
        return out
    except:
        return {}
    finally:
        close((cur,conn))

def getQualifyingParts(event):
    cur, conn = open()
    try:
        res_table = sql.Identifier(f"{event}ResultsPri")
        cur.execute(sql.SQL("SELECT sname, sid FROM {} ORDER BY points LIMIT 6").format(res_table))
        qualifiers = cur.fetchall()
        out = {}
        data = []
        for sname, sid in qualifiers:
            cur.execute(sql.SQL("""
                SELECT p.name, p.class FROM participants p
                JOIN (
                    SELECT sid FROM {res} ORDER BY points LIMIT 6
                ) AS res ON p.sid = res.sid
                WHERE p.event = %s AND p.attendance = TRUE AND res.sid = %s
            """).format(res=res_table), (event, sid))
            participants = cur.fetchall()
            part_list = [{"name": name, "class": clss} for name, clss in participants]
            data.append({"name": sname, "participants": part_list})
        out[event] = data
        return out
    except Exception as e:
        print(f"Error in getQualifyingParts: {e}")
        return {}
    finally:
        close((cur, conn))