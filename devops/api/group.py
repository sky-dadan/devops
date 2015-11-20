#coding:utf-8
import json
import logging
import traceback

import util

from flask import Flask, request
from . import app             #等价 from api import app


@app.route("/api/group",methods=['GET','POST','DELETE'])
def group():
    try:
        authorization = request.headers['authorization']
        name = util.validate(authorization, app.config['passport_key'])
        if not name:
            logging.getLogger().warning("Request forbiden")
            return json.dumps({'code': 1, 'errmsg': 'User validate error'})
        if not util.role(name):
            logging.getLogger().warning("You are not admin,Request forbiden")
            return json.dumps({'code':1,'errmsg':'You are not admin,Request forbiden'})
    except:
        logging.getLogger().warning("Validate error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'User validate error'})

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
            util.write_log(name, 'list all groups')
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
            util.write_log(name,'add group %s' % data['name'])
            return json.dumps({'code':0,'result': 'add group %s Success' % data['name']})
        except:
            logging.getLogger().error("Lock user error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Add group error'})

    if request.method == 'DELETE' and util.role(name):
        try:
            del_groups = request.get_data()
            del_groups = json.loads(del_groups)
            fields, values = [],[]
            field = del_groups.keys()[0]
            values = del_groups[field]
            for d_group in values:
                sql_del_group = 'delete from groups where name="%s"' % d_group
                sql_sel_gid = 'select id from groups where name="%s"'  % d_group
                app.config['cursor'].execute(sql_sel_gid)
                sel_gid = app.config['cursor'].fetchone()
                sql_del_userin_group = 'delete from user_group where group_id="%s"' % sel_gid 
                app.config['cursor'].execute(sql_del_group)
                app.config['cursor'].execute(sql_del_userin_group)
                util.write_log(name,"delete group %s" %  d_group )
            return json.dumps({'code':0,'result':'successful','values':values})
        except:
            logging.getLogger().error("Create user error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Create user error'})
    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method})

@app.route("/api/group_detail/<int:gid>",methods=['GET','POST','PUT','DELETE'])
def group_detail(gid):
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
            util.write_log(name,"List %s's members:%s" % (group_name,','.join(members)))
            return json.dumps({'code':0,'group_name':group_name,'members':members,'comment':comment})
        except:
            logging.getLogger().error(" list members error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'List members error'})

    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method})

@app.route('/api/group/manager',methods=['GET','PUT','DELETE'])
def group_manager():
    try:
        authorization = request.headers['authorization']
        name = util.validate(authorization,app.config['passport_key'])
        if not name :
            logging.getLogger().warining("Request forbiden")
            return json.dumps({'code':1,'errmsg':"User validate error"})
    except:
        logging.getLogger().warning("Validate error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'User Validate error'})

    if request.method == 'PUT':
        try:
            s_data = request.get_data()
            s_data = json.loads(s_data)
            s_username = s_data.values()[0]       
            s_result = []
            sql="select name,name_cn  from groups  where id=(select group_id from user_group where user_id =(select id from user where username='%s'))"   %  s_username
            app.config['cursor'].execute(sql)
            for g_name in app.config['cursor'].fetchone():
                s_result.append(g_name)
            util.write_log(name,"select %s belong to group"  % s_username)
            return json.dumps({'code':0,'result':'select successful','g_name':s_result})
        except:
            logging.getLogger().error("select group error:%s" %  traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'select user_group  error'})
