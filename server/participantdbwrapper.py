import psycopg2
from psycopg2 import sql
import json
import os
from  . import eventdbwrapper as evdb
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

def init():
    con = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cur = con.cursor()
    cur.execute("""CREATE TABLE Participants(
        pid INT PRIMARY KEY,
        name VARCHAR(50),
        class INT,
        event VARCHAR(20),
        sid CHAR(6),
        sname VARCHAR(100),
        attendance BOOLEAN
    );""")
    con.commit()
    cur.close()
    con.close()
    
def insertParticipant(cur, pid, name, clss, event, sid, sname, attendance):
    cur.execute("""INSERT INTO Participants VALUES (%s,%s,%s,%s,%s,%s,%s)""",(pid, name, clss, event, sid, sname, attendance))


def getTable():
    connection = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM Participants""")
    head = [desc[0] for desc in cursor.description]
    data = [head]+list(cursor.fetchall())
    cursor.close()
    connection.close()
    return data

def getBySchool(sid):
    connection = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM Participants WHERE sid = %s""", (sid,))
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
    if cls:
        fields.append("class = %s")
        values.append(cls)
    if section:
        fields.append("section = %s")
        values.append(section)
    if event:
        fields.append("event = %s")
        values.append(event)
    if perms:
        fields.append("perms = %s")
        values.append(perms)
    values.append(uuid)  # for WHERE clause
    query = f"UPDATE Participants SET {', '.join(fields)} WHERE uuid = %s"
    cur.execute(query, tuple(values))


def markPresent(cur, pid, attendance):
    cur.execute("""UPDATE Participants SET attendance=%s WHERE pid = %s""", (attendance, pid))

def confirm(conn):
    conn.commit()

def close(curcon):
    curcon[0].close()
    curcon[1].close()

def seperateIntoEvents(curconn):
    cur,conn = curconn
    onsites = creds["onsiteEvents"]
    prelds = creds["preldEvents"]
    for event in onsites:
        if event in prelds:
            evdb.genAtt(curconn, event, "prelims")
        else:
            evdb.genAtt(curconn, event, "finals")
    conn.commit()
    print("SEPERATED")

def seperatePregrads(curconn):
    cur,conn = curconn
    onlPrels = creds["pregradPrels"]
    for event in onlPrels:
        evdb.genAtt((cur,conn), event=event, round="prelims")

def revert(curconn):
    cur,conn = curconn
    events = creds["Events"]
    for event in events:
        priatt=sql.Identifier(event+"AttendancePri")
        finatt=sql.Identifier(event+"AttendanceFin")
        prires=sql.Identifier(event+"ResultsPri")
        finres=sql.Identifier(event+"ResultsFin")
        wins = sql.Identifier(event+"Winners")
        cur.execute(sql.SQL("""DROP TABLE IF EXISTS {priatt}, {finatt},{prires},{finres}, {wins}, Attendance, Results, MeritCerts, AppCerts, PartCerts""").format(priatt=priatt,prires=prires,finatt=finatt, finres=finres, wins = wins))
        conn.commit()

def getGreatestPid(cur):
    cur.execute("""SELECT pid FROM Participants ORDER BY pid DESC LIMIT 1;""")
    pid = cur.fetchone()
    if pid==None:
        return 1000
    return pid[0]

if __name__ == '__main__':
    conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cur = conn.cursor()
    cur.execute("""DROP TABLE Participants""")
    conn.commit()
    init()
    #print(getGreatestPid(cur))
    cur.close()
    conn.close()