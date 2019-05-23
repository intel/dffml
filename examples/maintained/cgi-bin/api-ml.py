#!/usr/bin/env python2
import os
import cgi
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
    cursor.execute("SELECT src_url, maintained FROM status")
    print json.dumps(dict(cursor))
elif action == 'set':
    cursor.execute("REPLACE INTO status (src_url, maintained) VALUES(%s, %s)",
                   (query['URL'], query['maintained'],))
    cnx.commit()
    print json.dumps(dict(success=True))
elif action == 'predict':
    today = datetime.now().strftime('%Y-%m-%d %H:%M')
    operations = [
        'group_by',
        'quarters_back_to_date',
        'check_if_valid_git_repository_URL',
        'clone_git_repo',
        'git_repo_default_branch',
        'git_repo_checkout',
        'git_repo_commit_from_date',
        'git_repo_author_lines_for_dates',
        'work',
        'git_repo_release',
        'git_commits',
        'count_authors',
        'cleanup_git_repo'
        ]
    subprocess.check_call(([
        'dffml', 'operations', 'repo',
        '-log', 'debug',
        '-sources', 'db=demoapp',
        '-update',
        '-keys', query['URL'],
        '-repo-def', 'URL',
        '-remap',
        'group_by.work=work',
        'group_by.commits=commits',
        'group_by.authors=authors',
        '-dff-memory-operation-network-ops'] + operations + [
        '-dff-memory-opimp-network-opimps'] + operations + [
        '-inputs'] + \
        ['%d=quarter' % (i,) for i in range(0, 10)] + [
        '\'%s\'=quarter_start_date' % (today,),
        'True=no_git_branch_given',
        '-output-specs', '''{
            "authors": {
              "group": "quarter",
              "by": "author_count",
              "fill": 0
            },
            "work": {
              "group": "quarter",
              "by": "work_spread",
              "fill": 0
            },
            "commits": {
              "group": "quarter",
              "by": "commit_count",
              "fill": 0
            }
          }=group_by_spec''']))
    result = subprocess.check_output([
        'dffml', 'predict', 'repo',
        '-keys', query['URL'],
        '-model', 'dnn',
        '-sources', 'db=demoapp',
        '-classifications', '0', '1',
        '-features',
        'def:authors:int:10',
        'def:commits:int:10',
        'def:work:int:10',
        '-log', 'critical',
        '-update'])
    result = json.loads(result)
    cursor.execute("REPLACE INTO status (src_url, maintained) VALUES(%s, %s)",
                   (query['URL'], result[0]['prediction']['classification'],))
    cnx.commit()
    print json.dumps(dict(success=True))
else:
    print json.dumps(dict(error='Unknown action'))

sys.stdout.flush()
cursor.close()
cnx.close()
