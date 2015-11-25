#coding:utf-8
import json
import logging
import traceback

import util

from flask import Flask, request
from . import app             #等价 from api import app
from auth import auth_login

@app.route("/api/group",methods=['GET','POST','DELETE'])
@auth_login
def group(auth_info):
    if request.method == 'GET':
        try:
            if request.args.get('offset')  is not  None and request.args.get('size') is  not None:
                offset = request.args.get('offset')
                size = request.args.get('size')
                if int(size) >= 1000:
                    return json.dumps({'code': 1, 'errmsg': 'you input size too big '})
            else:
                return json.dumps({'code':1,'errmsg':'Invalid args'})

            fields = ['name','name_cn','comment']
            groups = []
            sql = 'SELECT %s from groups limit %d,%d' % (','.join(fields),int(offset),int(size))
            app.config['cursor'].execute(sql)
            for row in app.config['cursor'].fetchall():
                group_list = {}
                for i,k in enumerate(fields):
                    group_list[k] = row[i]
                groups.append(group_list)
            util.write_log(auth_info[0], 'list all groups')
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
            values = ', '.join(["(%s, %s)" % (uid, gid) for uid in uids])
            sql = "INSERT INTO user_group VALUES %s" % values
            app.config['cursor'].execute(sql)
            util.write_log(auth_info[0],'Add group %s' % data['name'])
            return json.dumps({'code':0,'result': 'Add group %s Success' % data['name']})
        except:
            logging.getLogger().error("Add group error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Add group error'})
    if request.method == 'DELETE':
        try:
            data = request.get_data()
            data = json.loads(data)
            fields, values = [],[]
            field = data.keys()[0]
            values = data[field]
            for group in values:
                sql1 = 'SELECT id FROM groups WHERE name="%s"'  % group
                sql2 = 'DELETE FROM groups WHERE name="%s"' % group
                app.config['cursor'].execute(sql1)
                row = app.config['cursor'].fetchone()
                sql3 = 'delete from user_group where group_id="%s"' % row[0]
                app.config['cursor'].execute(sql2)
                app.config['cursor'].execute(sql3)
            util.write_log(auth_info[0],"Delete groups %s" % ','.join("'%s'" % group for group in values))
            return json.dumps({'code':0,'result':'Delete groups %s successful' % ','.join(["'%s'" % group for group in values])})
        except:
            logging.getLogger().error("Delete groups error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Delete groups error'})
    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method})

@app.route("/api/group_detail/<int:gid>",methods=['GET','POST','PUT','DELETE'])
@auth_login
def group_detail(auth_info,gid):
    if request.method == 'GET':
        try:
            if not util.if_groupid_exist(gid):
                return json.dumps({'code':1,'errmsg':'group is not exist'})
            members = []
            sql = 'SELECT name FROM groups WHERE id = %d' %(gid)
            app.config['cursor'].execute(sql)
            group_name = app.config['cursor'].fetchone()[0]
            sql = 'SELECT user.name,comment FROM groups,user,user_group WHERE groups.id=user_group.group_id and user.id = user_group.user_id and groups.id = %d' % (gid)
            app.config['cursor'].execute(sql)
            for row in app.config['cursor'].fetchall():
                members.append(row[0])
                comment = row[1]
            util.write_log(auth_info[0],"List %s's members:%s" % (group_name,','.join(members)))
            return json.dumps({'code':0,'group_name':group_name,'members':members,'comment':comment})
        except:
            logging.getLogger().error(" list members error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'List members error'})

    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method})
