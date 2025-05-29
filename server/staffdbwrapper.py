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
    connection = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cursor = connection.cursor()
    return (cursor,connection)

def init(cur):
    cur.execute("""CREATE TABLE Staff(
        uuid INT PRIMARY KEY,
        name VARCHAR(30),
        class INT,
        section CHAR(1),
        event VARCHAR(20),
        perms text[]
    );""")

def getData(cur, uuid):
    cur.execute("""SELECT * FROM Staff WHERE uuid = %s""",(uuid,))
    row = cur.fetchone()
    print(row)
    return row if row else None

def getPerms(cur, uuid):
    cur.execute("""SELECT perms FROM Staff WHERE uuid = %s""",(uuid,))
    return cur.fetchone()[0]

def getEvent(cur, uuid):
    cur.execute("""SELECT event FROM Staff WHERE uuid = %s""",(uuid,))
    return cur.fetchone()[0]

def getName(cur, uuid):
    cur.execute("""SELECT name FROM Staff WHERE uuid = %s""",(uuid,))
    return cur.fetchone()[0]

def insertUser(cur, uuid, name, cls, section, event, perms):
    cur.execute("""INSERT INTO Staff VALUES(%s, %s, %s, %s, %s, %s)""",(uuid,name,cls,section,event,perms))

def deleteUser(cur, uuid):
    cur.execute("""DELETE FROM Staff WHERE uuid = %s""",(uuid,))

def modUser(cur, uuid, name=None, cls=None, section=None, event=None, perms=None):
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
    query = f"UPDATE Staff SET {', '.join(fields)} WHERE uuid = %s"
    cur.execute(query, tuple(values))

def getTable(cur):
    cur.execute("""SELECT * FROM Staff""")
    head = [desc[0] for desc in cur.description]
    return [head]+list(cur.fetchall())

def confirm(conn):
    conn.commit()

def close(conncur):
    conncur[0].close()
    conncur[1].close()

if __name__=='__main__':
    curcon = open()
    curcon[0].execute("""SELECT * FROM Staff""")
    print(curcon[0].fetchall())
    #init(curcon[0])
    #deleteUser(100121, curcon[0])
    #insertUser(100120, 'Prakhar Chandra', 12, 'C', 'Pyrathon', '{EI,SI}', curcon[0])
    #confirm(curcon[1])
    close(curcon)
