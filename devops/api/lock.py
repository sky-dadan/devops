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

@app.route("/api/lock_user",methods=['GET','PUT'])
def lock_user():
    try:
        authorization = request.headers['authorization']
        name = util.validate(authorization, app.config['passport_key'])
        if not name:
            logging.getLogger().warning("Request forbiden")
            return json.dumps({'code': 1, 'errmsg': 'User validate error'})
    except:
        logging.getLogger().warning("Validate error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'User validate error'})

    try:
        data = request.get_data()
        data = json.loads(data)
        users = []
        for k, v in data.items():
            users.append(v)

        sql = 'update user set is_lock = 1 where username in (%s)'
        inargs = ', '.join(map(lambda x: '%s',users))
        sql = sql % inargs
        app.config['cursor'].execute_arg(sql,users)

        util.write_log(name,'lock user %s' % ','.join(users))
        return json.dumps({'code':0,'result': 'Lock %s Success' % ','.join(users)})
    except:
        logging.getLogger().error("Lock user error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'Lock user error'})

    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method})
