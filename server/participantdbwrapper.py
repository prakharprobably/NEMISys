import psycopg2

def open():
    con = psycopg2.connect(host = "", dbname="technolympics", user="", password="", port = 0000)
    cur = con.cursor()
    return cur,con

def init():
    con = psycopg2.connect(host = "", dbname="technolympics", user="", password="", port = 0000)
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
    connection = psycopg2.connect(host = "", dbname="technolympics", user="", password="", port = 0000)
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM Participants""")
    head = [desc[0] for desc in cursor.description]
    data = [head]+list(cursor.fetchall())
    cursor.close()
    connection.close()
    return data

def getBySchool(sid):
    connection = psycopg2.connect(host = "", dbname="technolympics", user="", password="", port = 0000)
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

if __name__ == '__main__':
    init()