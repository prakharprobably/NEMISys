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
    con = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cur = con.cursor()
    return cur,con

def close(curconn):
    cur,conn = curconn
    cur.close()
    conn.close()

def getParticipation(cur):
    try:
        cur.execute("""SELECT COUNT(pid) FROM Participants WHERE attendance = TRUE;""")
        data = cur.fetchone()
        return data[0]
    except:
        pass

def getOnsiteCount(cur):
    try:
        cur.execute("""SELECT COUNT(pid) FROM Attendance WHERE attendance = TRUE;""")
        data = cur.fetchone()
        return data[0]
    except:
        pass

def getTotalSchoolCount(cur):
    try:
        cur.execute("""SELECT COUNT(DISTINCT sid) FROM Schools""")
        data = cur.fetchone()
        return data[0]
    except:
        pass

def getParticipatingSchoolCount(cur):
    try:
        cur.execute("""SELECT COUNT(DISTINCT sid) FROM Participants WHERE attendance = TRUE""")
        data = cur.fetchone()
        return data[0]
    except:
        pass

def getOnsiteSchoolCount(cur):
    try:
        cur.execute("""SELECT COUNT(DISTINCT sid) FROM Attendance WHERE attendance = TRUE""")
        data = cur.fetchone()
        return data[0]
    except:
        pass

if __name__ == '__main__':
    cur,conn = open()
    print(getParticipation(cur))
    close((cur,conn))
