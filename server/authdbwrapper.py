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
    cursor,connection=open()
    #init(cursor)
    #insertUser(100120, "1e17a2a4c4420f63e04e21323377470ab94edf5e4c43ecb4b3d6db74eabaadb4", cursor)
    #modUser(100121, '5714cbcb9ef3f779420776dfff5eb07f42f372b280ac24faade67e994dadc919', cursor)
    cursor.execute("""SELECT * FROM OAuth""")
    print(cursor.fetchall())
    confirm(connection)
    close((cursor,connection))
    #cursor.execute("""SHOW TABLES;""")
    #print(cursor.fetchall())
