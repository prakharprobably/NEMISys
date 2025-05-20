import psycopg2

def open():
    connection = psycopg2.connect(host = "", dbname="technolympics", user="", password="", port = 0000)
    cursor = connection.cursor()
    return (cursor,connection)  

def init(cur):
    cur.execute("""CREATE TABLE OAuth(
    uuid INT PRIMARY KEY,
    passkey CHAR(64));""")

def checkLogin(cur, uuid, passkey):
    cur.execute("""SELECT passkey FROM OAuth WHERE uuid = %s;""",(uuid,))
    try:
        return cur.fetchone()[0]==passkey
    except:
        return False

def insertUser(cur, uuid, passkey):
    cur.execute("""INSERT INTO OAuth VALUES(%s, %s);""",(uuid, passkey))

def deleteUser(cur, uuid):
    cur.execute("""DELETE FROM OAuth WHERE uuid = %s;""",(uuid,))

def modUser(cur, uuid,passkey):
    cur.execute("""UPDATE OAuth SET passkey=%s WHERE uuid = %s""",(passkey,uuid))
    cur.execute("""SELECT * FROM OAuth""")
    print(cur.fetchall())

def confirm(conn):
    conn.commit()

def close(conncur):
    conncur[0].close()
    conncur[1].close()

if __name__=='__main__':
    cur,conn=open()
    init(cur=cur)
    confirm(conn)
    close((conn,cur))
