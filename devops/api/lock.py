#coding:utf-8
import json
import logging
import traceback
import sys
import util

from flask import Flask, request
from auth import auth_login
from . import app             #等价 from api import app
@app.route("/api/lockuser/<int:user_id>",methods=['GET','PUT'])
@auth_login
def lock_user(auth_info,user_id):
    if request.method == 'GET':
        sql='SELECT is_lock From user WHERE id = %d' % (user_id)
        app.config['cursor'].execute(sql)
        row = app.config['cursor'].fetchone()
        util.write_log(auth_info[0],'Check whether the user_id = %d is locked' % (row[0]))
        return json.dumps({'code':0, 'is_lock':row[0]})
    if request.method == 'PUT':
        try:
            data = request.get_data()
            data = json.loads(data)
            is_lock = data['is_lock']
            sql = 'UPDATE user SET is_lock = %d WHERE id = %d' % (is_lock,user_id)
            app.config['cursor'].execute(sql)
            if is_lock == 1:
                util.write_log(auth_info[0],'Lock user %d'% user_id)
                return json.dumps({'code':0,'msg':'Lock user user_id = %d' % user_id})
            elif is_lock == 0:
                util.write_log(auth_info[0],'Unlock user %d'% user_id)
                return json.dumps({'code':0,'msg':'Unlock user user_id = %d' % user_id})
            else:
                util.write_log(auth_info[0],'Invalid value is_lock = %d' % is_lock)
                return json.dumps({'code':0,'msg':'Invalid value is_lock = %d' % is_lock})
        except:
            logging.getLogger().error("Lock user error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Lock user error'})
    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method})

@app.route("/api/lockuser",methods=['GET','PUT'])
@auth_login
def lock_userlist(auth_info):

    name = auth_info[0]
    uid = int(auth_info[1])
    role = int(auth_info[2])
    
    if request.method == 'GET':
        try:
            users = []
            fields = ['username','is_lock']
            if role == 0 and request.args.get('list') =="true":
                sql = 'SELECT %s FROM user WHERE is_lock = 1' % ','.join(fields)
                app.config['cursor'].execute(sql)
                for row in app.config['cursor'].fetchall():
                    user = {}
                    for i,k in enumerate(fields):
                        user[k] = row[i]
                    users.append(user)
                util.write_log(name,'Check all users are locked')
                return json.dumps({'code':0,'is_lock':users})
            else:
                util.write_log(name,'You are not admin,no permission!')
                return json.dumps({'code':1,'result':'You are not admin,no permission!'})
        except:
            logging.getLogger().error("Get users is_lock error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Get users is_lock error'})
    if request.method == 'PUT':
        try:
            data = request.get_data()
            data = json.loads(data)
            sql = 'UPDATE user SET is_lock = 1 WHERE username in (%s)' % (','.join(["'%s'" % x for x in data['users']]))
            app.config['cursor'].execute(sql)

            util.write_log(auth_info[0],'lock user %s' % ','.join(data['users']))
            return json.dumps({'code':0,'result': 'Lock %s Success' % ','.join(data['users'])})
        except:
            logging.getLogger().error("Lock user error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Lock user error'})
    
    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method})
