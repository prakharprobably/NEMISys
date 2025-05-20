import psycopg2

def open():
    connection = psycopg2.connect(host = "", dbname="technolympics", user="", password="", port = 0000)
    cursor = connection.cursor()
    return (cursor,connection)

def init(cur):
    cur.execute("""CREATE TABLE Tokens(
        token CHAR(64) PRIMARY KEY,
        uuid INT,
        luse DATE,
        event VARCHAR(20),
        perms text[]
    );""")

def create(cur, token, uuid, event, perms):
    cur.execute("""INSERT INTO Tokens VALUES(%s, %s, CURRENT_DATE,  %s, %s)""", (token, uuid, event, perms))

def clean(cur, token=None, uuid=None):
    if uuid:
        cur.execute("""DELETE FROM Tokens WHERE uuid = %s""", (uuid,))
    elif token:
        cur.execute("""DELETE FROM Tokens WHERE token = %s""", (token,))
    else:
        cur.execute("""DELETE FROM Tokens WHERE luse < CURRENT_DATE - INTERVAL '7 days'""")

def checkToken(cur, token):
    cur.execute("""SELECT 1 FROM Tokens WHERE token = %s LIMIT 1""", (token,))
    return cur.fetchone() is not None

def getTokenPerms(cur, token):
    cur.execute("""SELECT perms FROM Tokens WHERE token=%s""",(token,))
    return cur.fetchone()[0]

def getTokenEvent(cur, token):
    cur.execute("""SELECT event FROM Tokens WHERE token=%s""",(token,))
    return cur.fetchone()[0]

def getTokenUUID(cur, token):
    cur.execute("""SELECT uuid FROM Tokens WHERE token=%s""",(token,))
    return cur.fetchone()[0]

def modTokenPerms(cur, uuid, perms=None, event=None):
    sets, params = [], []
    if perms is not None:
        sets.append("perms = %s")
        params.append(perms)
    if event is not None:
        sets.append("event = %s")
        params.append(event)
    params.append(uuid)
    cur.execute(f"UPDATE Tokens SET {', '.join(sets)} WHERE uuid = %s", params)


def update(cur, token):
    cur.execute("""UPDATE Tokens SET luse = CURRENT_DATE WHERE token = %s""", (token,))

def confirm(conn):
    conn.commit()

def close(conncur):
    conncur[0].close()
    conncur[1].close()


if __name__ == '__main__':
    cur,conn=open()
    init(cur=cur)
    confirm(conn)
    close((conn,cur))
