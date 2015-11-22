#coding:utf-8
import json
import logging
import traceback

import util

from flask import Flask, request
from . import app             #等价 from api import app
from auth import auth_login

@app.route("/api",methods=['GET', 'PUT'])
@auth_login
def index(auth_info):
    if request.method == 'GET':
        try:
            users = []
            fields = ['id', 'username', 'name', 'email', 'mobile']
            sql = "SELECT %s FROM user" % ','.join(fields)
            app.config['cursor'].execute(sql)
            for row in app.config['cursor'].fetchall():
                user = {}
                for i, k in enumerate(fields):
                    user[k] = row[i]
                users.append(user)
            util.write_log(auth_info[0], 'get_all_users')
            return json.dumps({'code': 0, 'users': users})
        except:
            logging.getLogger().error("Get users list error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Get users error'})

    elif request.method == 'PUT':
        try:
            data = request.get_data()
            data = json.loads(data)
            fields, values = [], []
            for k, v in data.items():
                fields.append(k)
                values.append("'%s'" % v)
            sql = "INSERT INTO user (%s) VALUES (%s)" % (','.join(fields), ','.join(values))
    
            util.write_log(auth_info[0], "create_user %s" % data['username'])
            return json.dumps({'code': 0, 'result': 'Create %s success' % data['username']})
        except:
            logging.getLogger().error("Create user error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Create user error'})

    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method})
