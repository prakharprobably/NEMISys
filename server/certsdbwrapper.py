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

def genMerits():
    cur,conn = open()
    events = creds["Events"]
    cur.execute("""DROP TABLE IF EXISTS MeritCerts""")
    conn.commit()
    cur.execute("""CREATE TABLE MeritCerts (pid INT, rank INT, name VARCHAR(50), class INT, event VARCHAR(20), sname VARCHAR(100), sAddress VARCHAR(255))""")
    conn.commit()
    for event in events:
        win = sql.Identifier(event + "Winners")
        cur.execute(sql.SQL("""
            INSERT INTO MeritCerts (pid, rank, name, class, event, sname, sAddress)
            SELECT p.pid, w.rank, p.name, p.class, p.event, p.sName, s.sAddress
            FROM participants p
            JOIN schools s ON p.sid = s.sid
            JOIN {win} AS w ON p.sid = w.sid
            WHERE p.event = %s AND p.attendance = TRUE AND w.rank <= 3""").format(win=win), (event,))
    conn.commit()
    close((cur,conn))

def genParts():
    cur,conn = open()
    events = creds["Events"]
    cur.execute("""DROP TABLE IF EXISTS PartCerts""")
    conn.commit()
    cur.execute("""CREATE TABLE PartCerts (pid INT, name VARCHAR(50), class INT, event VARCHAR(20), sname VARCHAR(100), sAddress VARCHAR(255))""")
    for event in events:
        win = sql.Identifier(event + "Winners")
        cur.execute(sql.SQL("""
            INSERT INTO PartCerts (pid, name, class, event, sname, sAddress)
            SELECT p.pid, p.name, p.class, p.event, p.sName, s.sAddress
            FROM participants p
            JOIN schools s ON p.sid = s.sid
            WHERE p.event = %s AND p.attendance = TRUE AND p.sid NOT IN (
            SELECT sid FROM {win} ORDER BY rank LIMIT 3)""").format(win=win), (event,))
    conn.commit()
    close((cur,conn))

def genAppr():
    cur,conn = open()
    events = creds["Events"]
    cur.execute("""DROP TABLE IF EXISTS AppCerts""")
    conn.commit()
    cur.execute("""CREATE TABLE AppCerts(name VARCHAR(30), class INT, section CHAR(1), event VARCHAR(20), sname VARCHAR(100))""")
    cur.execute("""INSERT INTO AppCerts (name, class, section, event, sname)
    SELECT name, class, section, event, 'Cambridge School, Noida' FROM Staff WHERE NOT ('TC' = ANY(perms))""")
    conn.commit()
    close((cur,conn))


def getMerits(event):
    cur,conn = open()
    cur.execute("""SELECT * FROM MeritCerts WHERE EVENT = %s""", (event,))
    head = [desc[0] for desc in cur.description]
    data = [head]+list(cur.fetchall())
    close((cur,conn))
    return data

def getParts(event):
    cur,conn = open()
    cur.execute("""SELECT * FROM PartCerts WHERE event = %s""", (event,))
    head = [desc[0] for desc in cur.description]
    data = [head] + list(cur.fetchall())
    close((cur,conn))
    return data

def getAppr():
    cur,conn = open()
    cur.execute("""SELECT * FROM AppCerts ORDER BY event""")
    head = [desc[0] for desc in cur.description]
    data = [head] + list(cur.fetchall())
    close((cur,conn))
    return data