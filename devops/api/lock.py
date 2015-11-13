#coding:utf-8
import json
import logging
import traceback
import sys
import util

from flask import Flask, request
from . import app             #等价 from api import app
@app.route("/api/lockuser/<int:user_id>",methods=['GET','PUT'])
def lock_user(user_id):
    try:
        authorization = request.headers['authorization']
        name = util.validate(authorization, app.config['passport_key'])
        if not name:
            logging.getLogger().warning("Request forbiden")
            return json.dumps({'code': 1, 'errmsg': 'User validate error'})
        if util.role(name) is False:
            logging.getLogger().warning("You are not admin,Request forbiden")
            return json.dumps({'code':1,'errmsg':'You are not admin,Request forbiden'})
    except:
        logging.getLogger().warning("Validate error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'User validate error'})

    if request.method == 'GET':
        sql='SELECT is_lock From user WHERE id = %d' % (user_id)
        app.config['cursor'].execute(sql)
        row = app.config['cursor'].fetchone()
        util.write_log(name,'Check whether the user_id = %d is locked' % (row[0]))
        return json.dumps({'code':0, 'is_lock':row[0]})

    if request.method == 'PUT':
        try:
            data = request.get_data()
            data = json.loads(data)
            user_id  = data['user_id']
            sql = 'UPDATE user SET is_lock = 1 WHERE id = %d' % (user_id)
            app.config['cursor'].execute(sql)
            util.write_log(name,'Lock user %d'% user_id)
            return json.dumps({'code':0,'msg':'Lock user user_id = %d' % user_id}) 
        except:
            logging.getLogger().error("Lock user error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Lock user error'})
    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method})

@app.route("/api/lockuser",methods=['GET','PUT'])
def lock_userlist():    
    try:
        authorization = request.headers['authorization']
        name = util.validate(authorization, app.config['passport_key'])
        if not name:
            logging.getLogger().warning("Request forbiden")
            return json.dumps({'code': 1, 'errmsg': 'User validate error'})
        if util.role(name) is False:
            logging.getLogger().warning("You are not admin,Request forbiden")
            return json.dumps({'code':1,'errmsg':'You are not admin,Request forbiden'})
    except:
        logging.getLogger().warning("Validate error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'User validate error'})

    if request.method == 'GET':
        try:
            users = []
            fields = ['username','is_lock']
            sql = 'SELECT %s FROM user' % ','.join(fields)
            app.config['cursor'].execute(sql)
            for row in app.config['cursor'].fetchall():
                user = {}
                for i,k in enumerate(fields):
                    user[k] = row[i]
                users.append(user)
            util.write_log(name,'Check all users are locked')
            return json.dumps({'code':0,'is_lock':users})
        except:
            logging.getLogger().error("Get users is_lock error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Get users is_lock error'})
    if request.method == 'PUT':
        try:
            data = request.get_data()
            data = json.loads(data)
            sql = 'UPDATE user SET is_lock = 1 WHERE username in (%s)' % (','.join(["'%s'" % x for x in data['users']]))
            app.config['cursor'].execute(sql)

            util.write_log(name,'lock user %s' % ','.join(data['users']))
            return json.dumps({'code':0,'result': 'Lock %s Success' % ','.join(data['users'])})
        except:
            logging.getLogger().error("Lock user error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Lock user error'})
@app.route("/api/unlockuser/<int:user_id>",methods=['PUT'])
def unlockuser(user_id):
    try:
        authorization = request.headers['authorization']
        name = util.validate(authorization, app.config['passport_key'])
        if not name:
            logging.getLogger().warning("Request forbiden")
            return json.dumps({'code': 1, 'errmsg': 'User validate error'})
        if util.role(name) is False:
            logging.getLogger().warning("You are not admin,Request forbiden")
            return json.dumps({'code':1,'errmsg':'You are not admin,Request forbiden'})
    except:
        logging.getLogger().warning("Validate error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'User validate error'})

    if request.method == 'PUT':
        try:
            data = request.get_data()
            data = json.loads(data)
            user_id  = data['user_id']
            sql = 'UPDATE user SET is_lock = 0 WHERE id = %d' % (user_id)
            app.config['cursor'].execute(sql)
            util.write_log(name,'Lock user %d'% user_id)
            return json.dumps({'code':0,'msg':'Unlock user user_id = %d' % user_id}) 
        except:
            logging.getLogger().error("Unlock user error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Unlock user error'})

    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method})
