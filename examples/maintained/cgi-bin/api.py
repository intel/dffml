#!/usr/bin/env python2
import os
import sys
import json
import urlparse
import mysql.connector

from conf import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_PORT

print 'Content-Type: application/json'
print ''

query = dict(urlparse.parse_qsl(os.getenv('QUERY_STRING', default='')))

action = query.get('action', None)

if action is None:
    print json.dumps(dict(error='Need method query parameter'))
    sys.exit(1)

cnx = mysql.connector.connect(
    user=MYSQL_USER,
    passwd=MYSQL_PASSWORD,
    database=MYSQL_DATABASE,
    port=MYSQL_PORT
    )
cursor = cnx.cursor()

if action == 'dump':
    cursor.execute("SELECT key, maintained FROM status")
    print json.dumps(dict(cursor))
elif action == 'set':
    cursor.execute("REPLACE INTO status (key, maintained) VALUES(%s, %s)",
                   (query['URL'], query['maintained'],))
    cnx.commit()
    print json.dumps(dict(success=True))
else:
    print json.dumps(dict(error='Unknown action'))

sys.stdout.flush()
cursor.close()
cnx.close()
