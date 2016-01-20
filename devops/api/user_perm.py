#!/usr/bin/env python
#coding:utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app , jsonrpc
import logging, util
from auth import auth_login
import json, traceback

#这里是关于用户权限的查看，修改  组的增删改查

def getid_list(id):   #传递过来的参数  (u'1,2',) or  [(u'1,2',), (u'1,3,4',)]
	p = set()
	if type(id) is list:
		for i in id:    #取出来的值是元组  lv = (u'1,2',)
			p.update(set(i[0].split(',')))
	p = list(p)
	p.sort()
	id_list = []
	for k in p:
		id_list.append(k.encode('utf-8'))
	print id_list
	return  id_list

@jsonrpc.method('user_perm.getlist')
@auth_login
def getlist(auth_info,**kwargs):
	if auth_info['code']==1:
		return json.dumps(auth_info)
	username = auth_info['username']
	id = auth_info['uid']
	try:
		output = kwargs.get('output',[])
		if len(output) == 0:
			fields = ['name','name_cn','url','info']
		else:
			fields = output
		r_id = []
		sql = "select r_id from user where username = '%s'" % username
		app.config['cursor'].execute(sql)
		tmp = app.config['cursor'].fetchone()
		r_id.append(tmp)
		print r_id
		r_id = getid_list(r_id)
		sql_pid = "select p_id from groups where id in (%s)" % (','.join(r_id))
		print sql_pid
		app.config['cursor'].execute(sql_pid)
		perm, perm_result = [],[]
		for row in app.config['cursor'].fetchall():
			perm.append(row)
		print perm
		perm_result = getid_list(perm)
		print perm_result
		sql_perm = "select %s from power where id in %s" %  (','.join(fields),tuple(perm_result))
		print sql_perm
		app.config['cursor'].execute(sql_perm)
		result =  []
		count = 0
		for v in app.config['cursor'].fetchall():
			res = {}
			count += 1
			for i, k in enumerate(fields):
				res[k]=v[i]
			result.append(res)
		util.write_log(username, "get permission success")
		return json.dumps({'result':0,'result':result,'count':count})
	except:
		logging.getLogger().error("get list permission error: %s"  %  traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'getlist error : %s'  % traceback.format_exc()})


@jsonrpc.method('user_perm.get')
@auth_login
def getlist_byid(auth_info,**kwargs):
	if auth_info['code']==1:
		return json.dumps(auth_info)
	username = auth_info['username']
	try:
		output = kwargs.get('output',[])
		if len(output) == 0:
			fields = ['name','name_cn','url','info']
		else:
			fields = output
		where = kwargs.get('where')
		if where.has_key('id'):
				id = where['id']
		r_id = []
		sql = "select r_id from user where id = '%s'" % id
		print sql
		app.config['cursor'].execute(sql)
		tmp = app.config['cursor'].fetchone()
		r_id.append(tmp)
		print r_id
		r_id = getid_list(r_id)
		sql_pid = "select p_id from groups where id in (%s)" % (','.join(r_id))
		print sql_pid
		app.config['cursor'].execute(sql_pid)
		perm, perm_result = [],[]
		for row in app.config['cursor'].fetchall():
			perm.append(row)
		print perm
		perm_result = getid_list(perm)
		print perm_result
		sql_perm = "select %s from power where id in %s" %  (','.join(fields),tuple(perm_result))
		print sql_perm
		app.config['cursor'].execute(sql_perm)
		result =  []
		count = 0
		for v in app.config['cursor'].fetchall():
			res = {}
			count += 1
			for i, k in enumerate(fields):
				res[k]=v[i]
			result.append(res)
		util.write_log(username, "get permission success")
		return json.dumps({'result':0,'result':result,'count':count})
	except:
		logging.getLogger().error("get list permission error: %s"  %  traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'getlist error : %s'  % traceback.format_exc()})


@jsonrpc.method('user_perm.update')
@auth_login
def update(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	if auth_info['role'] != '0':
		return json.dumps({'code':1,'errmsg':'you are not admin'})
	try:
		data = request.get_json()['params']
		sql = "update user set r_id = '%s' where id='%s'"  % (data['r_id'], data['where']['id'])
		print sql
		app.config['cursor'].execute(sql)
		util.write_log(username, 'update  permission success')
		return json.dumps({'code':0,'result':'update permission success!'})
	except:
		logging.getLogger().error(username,'update user permission error: %s' %  traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'error: %s' %  traceback.format_exc()})


@jsonrpc.method('user_groups.getlist')
@auth_login
def user_groups(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json,dumps(auth_info)
	username = auth_info['username']
	try:
		output = kwargs.get('output', [])
		if len(output) == 0:
			fields = ['id','name','name_cn','p_id','info']
		else:
			fields = output
		sql = "select r_id from user where username='%s'" % username
		print sql
		app.config['cursor'].execute(sql)
		tmp = app.config['cursor'].fetchone()
		r_id = []
		r_id.append(tmp)
		r_id = getid_list(r_id)
		count = 0
		result = []
		sql_groups = "select %s from groups where id in (%s)" % (','.join(fields),','.join(r_id))
		app.config['cursor'].execute(sql_groups)
		for row in app.config['cursor'].fetchall():
			res = {}
			count+=1
			for i, k in enumerate(fields):
				res[k] = row[i]
			result.append(res)
		util.write_log(username, "get groups success")
		return json.dumps({'code':0,'result':result,'count':count})
	except:
		logging.getLogger().error("get list groups error: %s"  % traceback.format_exc())
		return json.dumps({'code':1, 'errmsg':'get groups error %s'   %  traceback.format_exc()})

@jsonrpc.method('user_groups.get')
@auth_login
def user_group_byid(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	try:
		output = kwargs.get('output',[])
		if len(output)==0:
			fields = ['name','name_cn','id','p_id','info']
		else:
			fields = output
		where = kwargs.get('where',None)
		if where.has_key('id'):
			id = where['id']
		r_id = []
		sql = "select r_id from user where id = '%s'"  % id
		app.config['cursor'].execute(sql)
		tmp = app.config['cursor'].fetchone()
		r_id.append(tmp)
		r_id=getid_list(r_id)
		sql_groups = "select %s  from groups where id in (%s)"  %  (','.join(fields),','.join(r_id))
		print sql_groups
		app.config['cursor'].execute(sql_groups)
		result = []
		count = 0
		for v in app.config['cursor'].fetchall():
			res = {}
			count += 1
			for i, k in enumerate(fields):
				res[k]=v[i]
			result.append(res)
		util.write_log(username, "get user_groups success")
		return json.dumps({'result':0, 'result':result,'count':count})
	except:
		logging.getLogger().error('get list user_groups error: %s' % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':"get list user_groups error  : %s" % traceback.format_exc()})


@jsonrpc.method('groups_sel.get')
@auth_login
def get_color(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        where = kwargs.get('where',None)
        id = where['id']
        sql_rid = "select r_id from  user  where id=%s"  % id
        app.config['cursor'].execute(sql_rid)
        r_id = app.config['cursor'].fetchone()
        rlist=[]
        rlist.append(r_id)
        r_id = getid_list(rlist)
        sql = "select id, name from groups "
        app.config['cursor'].execute(sql)
        result = []
        groups_id = []
        for row in app.config['cursor'].fetchall():
            res = {}
            res['selected'] = ''
            groups_id.append(str(row[0]))
            for i, k in enumerate(['id','name']):
                res[k]=row[i]
            select = set(r_id)  &  set(groups_id)
            if str(res['id'])  in select:
                print res['id'], select
                res['selected'] = "selected = selected"
            result.append(res)
        print groups_id
        util.write_log(username, "groups_sel.get successful!")
        return json.dumps({'code':0,'result':result})
    except:
        logging.getLogger().error('groups_sel.get error!')
        return json.dumps({'code':1,'errmsg':'error: %s'  %  traceback.format_exc()})


@jsonrpc.method('power_sel.get')
@auth_login
def get_color(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        where = kwargs.get('where',None)
        id = where['id']
        sql_rid = "select p_id from  groups  where id=%s"  % id
        app.config['cursor'].execute(sql_rid)
        p_id = app.config['cursor'].fetchone()
        plist=[]
        plist.append(p_id)
        p_id = getid_list(plist)
        sql = "select id, name from power "
        app.config['cursor'].execute(sql)
        result = []
        power_id = []
        for row in app.config['cursor'].fetchall():
            res = {}
            res['selected'] = ''
            power_id.append(str(row[0]))
            for i, k in enumerate(['id','name']):
                res[k]=row[i]
            select = set(p_id)  &  set(power_id)
            if str(res['id'])  in select:
                res['selected'] = "selected = selected"
            result.append(res)
        util.write_log(username,"power_sel.get successful!")
        return json.dumps({'code':0,'result':result})
    except:
        logging.getLogger().error('power_sel.get error! %s'  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'error: %s'  %  traceback.format_exc()})


@jsonrpc.method('user.getlist')
@auth_login
def user_getlist(auth_info,**kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	try:
		output = kwargs.get('output',[])
		if len(output)==0:
			fields = ['id','username','name','email','mobile','is_lock']
		else:
			fields = output
		sql = "SELECT %s from user "  %  ','.join(fields)
		app.config['cursor'].execute(sql)
		result = []
		for row in app.config['cursor'].fetchall():
			res = {}
			for i , k in enumerate(fields):
				res[k] = row[i]
			result.append(res)
		util.write_log(username, 'user.getlist successed!')
		return json.dumps({'code':0,'result':result,'count':len(result)})
	except:
		logging.getLogger().error('user.getlist error : %s')
		return json.dumps({'code':1,'errmsg':'user.getlist error:  %s'  %  traceback.format_exc()})


@jsonrpc.method('user.get')
@auth_login
def user_get(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	try:
		output = kwargs.get('output',[])
		if len(output) == 0:
			fields = ['id','username','name','email','mobile','is_lock']
		else:	
			fields = output
		where = kwargs.get('where')
		if where.has_key('id'):
			id = where['id']
		try:
			sql = "select %s from user where id = %s"  % (','.join(fields), id)
			app.config['cursor'].execute(sql)
		except:
			sql = "select %s from user where username='%s'" % (','.join(fields), id)
			print sql	
			app.config['cursor'].execute(sql)
		result = []
		for row in app.config['cursor'].fetchall():
			res = {}
			for i, k in enumerate(fields):
				res[k]=row[i]
			result.append(res)
		util.write_log(username,'user.get successed!')
		return json.dumps({'code':0,'result':result})
	except:
		logging.getLogger().error('user.get error: %s' %  traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'user.get error: %s' %  traceback.format_exc()})
