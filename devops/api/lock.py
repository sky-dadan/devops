#coding:utf-8
import json
import logging
import traceback

import util

from flask import Flask, request
from . import app             #等价 from api import app
@app.route("/api/islocked/<username>",methods=['GET', 'PUT'])
def is_locked(username):
    sql='select is_lock from user where username = "%s"' % username
    app.config['cursor'].execute(sql)
    row = app.config['cursor'].fetchone()
    return json.dumps({'code':0, 'is_lock':row[0]})

@app.route("/api/lock_user",methods=['GET'])
def lock_user():
    users = ['zhangxunan','lisi']
#    for user in users:
#        sql = 'update user set is_lock = 1 where username = "%s"' % user
#        app.config['cursor'].execute(sql)
#        util.write_log('zhangxunan','lock user %s' % user)
#    return json.dumps("lock user")

    sql='update user set is_lock = 1 where username in (%s)'
    inargs = ', '.join(map(lambda x: '%s',users))
    sql = sql % inargs
    app.config['cursor'].execute_arg(sql,users)
    util.write_log('zhangxunan','lock user %s' % ','.join(users))
    return json.dumps('lock users')
