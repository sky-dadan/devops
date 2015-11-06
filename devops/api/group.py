#coding:utf-8
import json
import logging
import traceback

import util

from flask import Flask, request
from . import app             #等价 from api import app

@app.route("/api/groupadd",methods=['GET','PUT'])
def groupadd():
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
        groupname = data['groupname']
        name_cn = data['name_cn']
        comment = data['comment']
        users = data['users']
        if len(users) == 0:
            return json.dumps({'code':1,'result':'Users can not be empty'})
        sql = "insert into groups(name,name_cn,comment) values('%s','%s','%s')" % (groupname,name_cn,comment)
        app.config['cursor'].execute(sql)
        sql = 'select id from groups where name = "%s"' % groupname
        app.config['cursor'].execute(sql)
        row = app.config['cursor'].fetchone()
        gid = row[0]
        for uname in users:
            sql = 'select id from user where username = "%s"' % uname
            app.config['cursor'].execute(sql)
            row = app.config['cursor'].fetchone()
            uid = row[0]
            sql = 'insert into user_group(user_id,group_id) values(%s,%s)' % (uid,gid)
            app.config['cursor'].execute(sql)

        util.write_log(name,'add group %s' % groupname)
        return json.dumps({'code':0,'result': 'add group %s Success' % groupname})
    except:
        logging.getLogger().error("Lock user error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'Add group error'})

    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method})

@app.route('/api/querygroup',methods=['GET'])
def query_group():
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
        fields=['group_name','user_name','group_comment']
        groups = []
        sql ='select groups.name as %s,user.name as %s,groups.comment as %s from groups,user,user_group where groups.id=user_group.group_id and user.id = user_group.user_id' %(fields[0],fields[1],fields[2])
        app.config['cursor'].execute(sql)
        for row in app.config['cursor'].fetchall():
            group_list = {}
            for i,k in enumerate(fields):
                group_list[k] = row[i]
            groups.append(group_list)
        util.write_log(name, 'list all groups and memebers')
        return json.dumps({'code': 0, 'groups': groups})
    except:
        logging.getLogger().error("Get group list error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'Get group list error'})
