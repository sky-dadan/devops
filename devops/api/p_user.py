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

@jsonrpc.method('p_user.select')
@auth_login
def getlist(auth_info,**kwargs):
	if auth_info['code']==1:
		return json.dumps(auth_info)
	username = auth_info['username']
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


@jsonrpc.method('p_user.update')
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


@jsonrpc.method('p_role.select')
@auth_login
def role_select(auth_info,**kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	try:
		data = request.get_json()['params']
		output = data.get('output',[])
		if len(output) == 0:
			fields = ['id','name','p_id','info']
		else:
			fields = output
		sql = "select %s from groups " % ','.join(fields)
		app.config['cursor'].execute(sql)
		result = []
		count = 0
		for row in app.config['cursor'].fetchall():
			count += 1
			res = {}
			for i,k in enumerate(fields):
				res[k] = row[i]
			result.append(res)
		util.write_log(username, 'select p_role list success')
		return json.dumps({'code':0,'result':result})
	except:
		logging.getLogger.error("select p_role list error: %s"  %  traceback.format_exec())
		return json.dumps({'code':1,'errmsg':'error : %s' %  traceback.format_exec()})

@jsonrpc.method('p_role.create')
@auth_login
def role_create(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	if auth_info['role'] != '0':
		return json.dumps({'code':1,'errmsg':'you are not admin!'})
	try:
		data = request.get_json()['params']
		print data
		fields, values = [], []
		for k,v in data.items():
			fields.append(k)
			values.append("'%s'" % v)
		sql = "insert into groups (%s) values (%s)"  % (','.join(fields),','.join(values))
		print sql
		app.config['cursor'].execute(sql)
		util.write_log(username, "create groups %s scucess" %  data['name'])
		return json.dumps({'code':0,'result':'create groups %s successed' % data['name']})
	except:
		logging.getLogger().error(username,"create groups    error: %s" % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'error:%s' % traceback.format_exc()})

@jsonrpc.method('p_role.delete')
@auth_login
def role_delete(auth_info,**kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	if auth_info['role'] != '0':
		return json.dumps({'code':1,'errmsg':'you are not admin'})
	try:
		data = request.get_json()['params']
		print data,  data['id']
		if not data.has_key('id'):
			return json.dumps({'code':1,'errmsg':'you need give an id!'})
		sql = "delete from groups where id='%s'"  % data['id']
		app.config['cursor'].execute(sql)
		util.write_log(username, 'delete groups successed')
		return json.dumps({'code':0,'result':'delete groups successed'})
	except:
		logging.getLogger().error('delete groups error: %s' %  traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'error: %s'  % traceback.format_exc()})


@jsonrpc.method('p_role.update')
@auth_login
def role_update(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	if auth_info['role'] != '0':
		return json.dumps({'code':1,'errmsg':'you are not admin!'})
	try:
		data = request.get_json()['params']
		where = data.get('where',None)
		print data
		data = data.get('data',None)
		print data
		print where
		if not where.has_key('id'):
			return json.dumps({'code':1, 'errmsg':'you need give an id!'})
		sql = "update groups set name='%(name)s', p_id='%(p_id)s', info='%(info)s' where id='%%d'" % data % where['id']	
		print sql
		app.config['cursor'].execute(sql)
		util.write_log(username, 'update groups %s success!' % data['name'])
		return json.dumps({'code':0,'result':'update groups %s successed' % data['name']})
	except:
		logging.getLogger().error("update error: %s"  % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':"error : %s" % traceback.format_exc()})

