#coding:utf-8
import json
import logging
import traceback

import util

from flask import Flask, request
from . import app             #等价 from api import app

@app.route("/api/group",methods=['GET','POST'])
def group():
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
            fields=['group_name','user_name','group_comment']
            groups = []
            sql ='SELECT groups.name AS %s,user.username AS %s,groups.comment AS %s FROM groups,user,user_group WHERE groups.id=user_group.group_id and user.id = user_group.user_id' %(fields[0],fields[1],fields[2])
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

    if request.method == 'POST':
        try:
            data = request.get_data()
            data = json.loads(data)
            fields = ['name','name_cn','comment']
            uids = []
            if len(data['users']) == 0:
                return json.dumps({'code':1,'result':'Users can not be empty'})
            sql = 'INSERT INTO groups (%s) VALUES (%s)' % (','.join(fields), ','.join(["'%s'" % data[x] for x in fields]))
            app.config['cursor'].execute(sql)
            sql = 'SELECT id FROM groups WHERE name = "%s"' % data['name']
            app.config['cursor'].execute(sql)
            row = app.config['cursor'].fetchone()
            gid = row[0]
            sql = "SELECT id FROM user WHERE username IN (%s)" % (','.join(["'%s'" % x for x in data['users']]))
            app.config['cursor'].execute(sql)
            rows = app.config['cursor'].fetchall()
            for row in rows:
                uids.append(row[0])
            values = ', '.join(["(%s, %s)" % (gid, uid) for uid in uids])
            sql = "INSERT INTO user_group VALUES %s" % values
            app.config['cursor'].execute(sql)
            util.write_log(name,'add group %s' % data['name'])
            return json.dumps({'code':0,'result': 'add group %s Success' % data['name']})
        except:
            logging.getLogger().error("Lock user error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Add group error'})

    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method})
