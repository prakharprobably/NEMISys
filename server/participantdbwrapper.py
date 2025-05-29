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

def init():
    con = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cur = con.cursor()
    cur.execute("""CREATE TABLE Participants(
        pid INT PRIMARY KEY,
        name VARCHAR(30),
        class INT,
        event VARCHAR(20),
        sid CHAR(7),
        sname VARCHAR(100),
        attendance BOOLEAN,
        CONSTRAINT sid FORIEGN KEY (sid) REFERENCES Schools(sid)
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
    print(f"marked {pid} as {attendance}")

def confirm(conn):
    conn.commit()
    print("confirmed changes to participant db")

def close(curcon):
    curcon[0].close()
    curcon[1].close()

def seperateIntoEvents(curconn):
    cur,conn = curconn
    onsites = creds["onsiteEvents"]
    for event in onsites:
        att=sql.Identifier(event+"Attendance")
        cur.execute(sql.SQL("""CREATE TABLE {att} AS
                               SELECT name, class, sid, sname FROM Participants WHERE event = %s AND attendance = TRUE
                            """).format(att=att), (event,))
        cur.execute(sql.SQL("""ALTER TABLE {att} ADD COLUMN attendance BOOLEAN DEFAULT FALSE""").format(att=att))
    conn.commit()
    print("SEPERATED")


def revert(curconn):
    cur,conn = curconn
    onsites = creds["onsiteEvents"]
    for event in onsites:
        att=sql.Identifier(event+"Attendance")
        pri=sql.Identifier(event+"ResultsPri")
        fin=sql.Identifier(event+"ResultsFin")
        cur.execute(sql.SQL("""DROP TABLE IF EXISTS {att},{pri},{fin}""").format(att=att,pri=pri,fin=fin))
        conn.commit()
    cur.execute(sql.SQL("""DROP TABLE IF EXISTS "Virtual WarriorsAttendance","Virtual WarriorsResultsPri","Virtual WarriorsResultsFin";"""))

def generatePriRes(curconn, event):
    cur,conn = curconn
    res=sql.Identifier(event+"ResultsPri")
    att=sql.Identifier(event+"Attendance")
    cur.execute(sql.SQL("""SELECT sid, sname INTO {res} FROM {att} GROUP BY sid WHERE attendance = TRUE""").format(res=res, att=att))
    cur.execute(sql.SQL("""ALTER TABLE {res} ADD COLUMN points INT DEFAULT 0""").format(res=res))
    conn.commit()

def generateFinRes(curconn, event):
    cur,conn = curconn
    fin=sql.Identifier(event+"ResultsFin")
    pri=sql.Identifier(event+"ResultsPri")
    limit = creds["limit"][event]
    cur.execute(sql.SQL("""SELECT * INTO {fin} FROM {pri} ORDER BY points LIMIT %s""").format(fin=fin, res=res), (limit,))
    cur.execute(sql.SQL("""UPDATE {res} SET points=0""").format(res=res))
    conn.commit()

def genVirtAtt(curconn):
    cur,conn = curconn
    cur.execute("""SELECT name, class, sid, sname INTO "Virtual WarriorsAttendance" FROM Participants WHERE event = 'Virtual Warriors'""")
    conn.commit()

def genVirtPriRes(curconn):
    cur,conn=curconn
    cur.execute("""SELECT sid, sname INTO "Virtual WarriorsResults" FROM Participants WHERE attendance = TRUE""")
    cur.execute("""ALTER TABLE "Virtual WarriorsResultsPri" ADD COLUMN points INT DEFAULT 0""")
    conn.commit()

def genVirtFinRes(curconn):
    cur,conn = curconn
    limit = creds["limit"]["Virtual Warriors"]
    cur.execute("""SELECT * INTO "Virtual Warriors ResultsFin" FROM "Virtual WarriorsResultsPri" ORDER BY points LIMIT %s""", (limit,))
    cur.execute("""UPDATE TABLE "Virtual Warriors ResultsFin" SET points = 0""")
    conn.commit()

if __name__ == '__main__':
    conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cur = con.cursor()
    cur.execute("""DELETE FROM Participants""")
    conn.commit()
    cur.close()
    conn.close()