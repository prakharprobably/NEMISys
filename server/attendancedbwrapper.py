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

def init():
    con = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cur = con.cursor()
    cur.execute("""CREATE TABLE Attendance(
        pid INT PRIMARY KEY,
        name VARCHAR(30),
        class INT,
        event VARCHAR(20),
        sid CHAR(7),
        sname VARCHAR(100),
        attendance BOOLEAN
    );""")
    con.commit()
    cur.close()
    con.close()


def open():
    con = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cur = con.cursor()
    return cur,con

def inherit():
    cur,conn = open()
    events = creds["Events"]
    pregrads = creds["pregradPrels"]
    onsites = creds["onsiteEvents"]
    for event in onsites:
        if event in pregrads:
            att_table = sql.Identifier(event + "AttendanceFin")
            cur.execute(sql.SQL("INSERT INTO Attendance SELECT pid, name, class, %s, sid, sname, attendance FROM {}").format(att_table), (event,)) # passes the event name as a value for the missing column)
        else:
            cur.execute("""INSERT INTO Attendance SELECT * FROM Participants WHERE event = %s""",(event,))
    conn.commit()
    cur.close()
    conn.close()

def getTable():
    connection = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM Attendance""")
    head = [desc[0] for desc in cursor.description]
    data = [head]+list(cursor.fetchall())
    cursor.close()
    connection.close()
    return data

def getBySchool(sid):
    connection = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM Attendance WHERE sid = %s""", (sid,))
    head = [desc[0] for desc in cursor.description]
    data = [head]+list(cursor.fetchall())
    cursor.close()
    connection.close()
    return data

def modPart(cur, pid, name=None, clss=None, event=None, sid=None):
    fields = []
    values = []
    if name:
        fields.append("name = %s")
        values.append(name)
    if clss:
        fields.append("class = %s")
        values.append(clss)
    if event:
        fields.append("event = %s")
        values.append(event)
    if sid:
        fields.append("sid = %s")
        values.append(sid)
    values.append(pid)  # for WHERE clause
    query = f"UPDATE Attendance SET {', '.join(fields)} WHERE pid = %s"
    cur.execute(query, tuple(values))

def markPresent(cur, pid, attendance):
    cur.execute("""UPDATE Attendance SET attendance=%s WHERE pid = %s""", (attendance, pid))
    partdb.markPresent(cur,pid,attendance=attendance)

def confirm(conn):
    conn.commit()

def close(curconn):
    cur,conn = curconn
    cur.close()
    conn.close()
