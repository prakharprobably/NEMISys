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

def markAtt(cur, event, pid, attendance, round):
    if round=="finals":
        att=sql.Identifier(event+"AttendanceFin")
    else:
        att=sql.Identifier(event+"AttendancePri")
    cur.execute(sql.SQL("""UPDATE {att} SET attendance=%s WHERE pid = %s""").format(att=att), (attendance, pid))
    print(f"marked {pid} as {attendance}")

def markRes(cur, event, sid, points, round):
    if round=="prelims":
        res=sql.Identifier(event+"ResultsPri")
    else:
        res=sql.Identifier(event+"ResultsFin")
    cur.execute(sql.SQL("""UPDATE {res} SET points=%s WHERE sid = %s""").format(res=res), (points, sid))
    print(f"marked {points} for {sid}")

def genAtt(curconn, event, round):
    cur,conn=curconn
    prelds = creds["preldEvents"]
    if round == "prelims":
        if event not in prelds:
            #we want to make a prelims table for a finals only
            pass
        else:
            #prelims table for prelims
            att=sql.Identifier(event+"AttendancePri")
            cur.execute(sql.SQL("""CREATE TABLE {att} AS
                                SELECT pid, name, class, sid, sname FROM Participants 
                                WHERE event = %s AND attendance = TRUE""").format(att=att), (event,))
            cur.execute(sql.SQL("""ALTER TABLE {att} ADD COLUMN attendance BOOLEAN DEFAULT FALSE""").format(att=att))
    else:
        #generate finals table
        fin=sql.Identifier(event+"AttendanceFin")
        if event in prelds: #if event is not finals only
            res=sql.Identifier(event+"ResultsPri")
            pri=sql.Identifier(event+"AttendancePri")
            limit = creds["limit"][event]
            cur.execute(sql.SQL("""SELECT {pri}.* INTO {fin} FROM {pri} WHERE {pri}.sid IN (
                SELECT sid FROM {res} ORDER BY points DESC LIMIT %s)""").format(pri=pri, fin=fin, res=res),(limit,))
        else: #event is finals only
            cur.execute(sql.SQL("""CREATE TABLE {fin} AS
                    SELECT pid, name, class, sid, sname, attendance FROM Participants 
                    WHERE event = %s AND attendance = TRUE""").format(fin=fin), (event,))
        cur.execute(sql.SQL("""UPDATE {fin} SET attendance = FALSE""").format(fin=fin))


def genRes(curconn, event, round):
    cur,conn=curconn
    prelds = creds["preldEvents"]
    if round == "prelims":
        if event not in prelds:
            #we want to make a prelims table for a finals only
            pass
        else:
            res=sql.Identifier(event+"ResultsPri")
            att=sql.Identifier(event+"AttendancePri")
            cur.execute(sql.SQL("""SELECT sid, sname INTO {res} FROM {att}  WHERE attendance = TRUE GROUP BY sid, sname""").format(res=res, att=att))
            cur.execute(sql.SQL("""ALTER TABLE {res} ADD COLUMN points INT DEFAULT 0""").format(res=res))
    else:
        #finals results table
        fin=sql.Identifier(event+"ResultsFin")
        if event in prelds:
            pri=sql.Identifier(event+"ResultsPri")
            limit = creds["limit"][event]
            cur.execute(sql.SQL("""SELECT * INTO {fin} FROM {pri} ORDER BY points LIMIT %s""").format(fin=fin, pri=pri), (limit,))
        else:
            att=sql.Identifier(event+"AttendanceFin")
            cur.execute(sql.SQL("""SELECT sid, sname INTO {fin} FROM {att}  WHERE attendance = TRUE GROUP BY sid, sname""").format(fin=fin, att=att))
            cur.execute(sql.SQL("""ALTER TABLE {fin} ADD COLUMN points INT DEFAULT 0""").format(fin=fin))
        cur.execute(sql.SQL("""UPDATE {fin} SET points=0""").format(fin=fin))

def getAttTable(event, round):
    cur, conn = open()
    if round=="finals":
        att=sql.Identifier(event+"AttendanceFin")
    else:
        att=sql.Identifier(event+"AttendancePri")
    cur.execute(sql.SQL("""SELECT * FROM {att}""").format(att=att))
    head = [desc[0] for desc in cur.description]
    data = [head]+list(cur.fetchall())
    close((cur,conn))
    return data

def getResTable(event, round):
    cur, conn = open()
    if round=="finals":
        res=sql.Identifier(event+"ResultsFin")
    else:
        res=sql.Identifier(event+"ResultsPri")
    cur.execute(sql.SQL("""SELECT * FROM {res}""").format(res=res))
    head = [desc[0] for desc in cur.description]
    data = [head]+list(cur.fetchall())
    close((cur,conn))
    return data

def close(curconn):
    cur,conn=curconn
    cur.close()
    conn.close()

if __name__ == "__main__":
    cur,conn = open()
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE';
    """)
    for table in cur.fetchall():
        print(table[0])
    close((cur,conn))