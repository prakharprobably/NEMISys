from server.participantdbwrapper import seperatePregrads, markPresent
from server.eventdbwrapper import genAtt, genRes, markAtt
import server.authdbwrapper as authdb
import server.discauthdbwrapper as discauthdb
import server.participantdbwrapper as participantdb
import server.schooldbwrapper as schooldb
import server.staffdbwrapper as staffdb
import server.tokendbwrapper as tokendb
import server.statsdbwrapper as statusdb
import hashlib

import psycopg2
from psycopg2 import sql
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_PATH = os.path.join(BASE_DIR, 'creds.json')

with open(CREDS_PATH, 'r') as f:
    creds = json.load(f)

host=creds["host"]
dbname=creds["dbname"]
user=creds["user"]
password=creds["password"]
port=creds["port"]

if __name__=='__main__':
    try:
        conn=psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
        cur=conn.cursor()

        #cur.execute("""DROP TABLE IF EXISTS discauth, oauth, Participants, Schools, Staff, Status, Tokens""")
        conn.commit()
        try:
            authdb.init(cur)
        except Exception as e:
            print(f"Something went wrong:{e}")
        try:
            discauthdb.init(cur,conn)
        except Exception as e:
            print(f"Something went wrong:{e}")
        try:
            participantdb.init()
        except Exception as e:
            print(f"Something went wrong:{e}")
        try:
            schooldb.init()
        except Exception as e:
            print(f"Something went wrong:{e}")
        try:
            staffdb.init(cur)
        except Exception as e:
            print(f"Something went wrong:{e}")
        try:
            statusdb.init(cur)
        except Exception as e:
            print(f"Something went wrong:{e}")
        try:
            tokendb.init(cur)
        finally:
            conn.commit()
            staffdb.insertUser(cur, 100000, "Admin", 12, "C", "All", ['EI', 'TC', 'SI'])
            authdb.insertUser(cur, 100000, hashlib.sha256(input("Enter Password for Admin: ").encode()).hexdigest())
    except Exception as e:
        print(e)
    finally:
        conn.commit()
        cur.close()
        conn.close()
    pregrads = creds["pregradPrels"]
    prelds = creds["preldEvents"]
    events = creds["Events"]