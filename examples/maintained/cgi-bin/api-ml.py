#!/usr/bin/env python2
import os
import sys
import json
import urlparse
import subprocess
import mysql.connector
from datetime import datetime

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
elif action == 'predict':
    today = datetime.now().strftime('%Y-%m-%d %H:%M')
    subprocess.check_call([
        "dffml", "dataflow", "run", "repos", "set",
        "-keys", query['URL'],
        "-repo-def", "URL",
        "-dataflow", os.path.join(os.path.dirname(__file__), "dataflow.yaml"),
        "-sources", "db=demoapp",
        ])
    result = subprocess.check_output([
        'dffml', 'predict', 'repo',
        '-keys', query['URL'],
        '-model', 'tfdnnc',
        '-model-predict', 'maintained',
        '-model-classifications', '0', '1',
        '-sources', 'db=demoapp',
        '-model-features',
        'authors:int:10',
        'commits:int:10',
        'work:int:10',
        '-log', 'critical',
        '-update'])
    result = json.loads(result)
    cursor.execute("REPLACE INTO status (key, maintained) VALUES(%s, %s)",
                   (query['URL'], result[0]['prediction']['value'],))
    cnx.commit()
    print json.dumps(dict(success=True))
else:
    print json.dumps(dict(error='Unknown action'))

sys.stdout.flush()
cursor.close()
cnx.close()
