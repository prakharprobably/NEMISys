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

def init():
    cur,con = open()
    cur.execute("""CREATE TABLE Schools(
        sid CHAR(6) PRIMARY KEY,
        subEmail VARCHAR(320),
        sName VARCHAR(50),
        sAddress VARCHAR(255),
        pName VARCHAR(50),
        pPhone INT,
        sEmail VARCHAR(320),
        tName VARCHAR(50),
        tPhone INT,
        tEmail VARCHAR(320)
    );
    """)
    con.commit()
    cur.close()
    con.close()

def insert(cur, sid, subEmail, sName, sAddress, pName, pPhone, sEmail, tName, tPhone, tEmail):
    cur.execute("""INSERT INTO Schools VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (sid, subEmail, sName, sAddress, pName, pPhone, sEmail, tName, tPhone, tEmail))

def getTable():
    connection = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM Schools""")
    head = [desc[0] for desc in cursor.description]
    data = [head]+list(cursor.fetchall())
    cursor.close()
    connection.close()
    return data

def confirm(conn):
    conn.commit()

def close(curcon):
    curcon[0].close()
    curcon[1].close()

if __name__ == '__main__':
    connection = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cursor = connection.cursor()
    cursor.execute("""DELETE FROM Schools""")
    connection.commit()
    cursor.close()
    connection.close()

