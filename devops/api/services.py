#!/usr/bin/env python
#coding: utf-8
from flask  import Flask, request
from flask_jsonrpc import JSONRPC
from .import app
import logging, util
from auth import auth_login
import json, traceback
from cabinet import jsonrpc

@jsonrpc.method('services.create')
@auth_login
def create(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	role = int(auth_info['role'])
	if role != 0:
		return json.dumps({'code':1,'errmsg':'you are not admin!'})
	try:
		data = request.get_json()['params']
		fields, values = [] ,[]
		for k,v in data.items():
			fields.append(k)
			values.append("'%s'" % v)
		sql = "insert into Services (%s) values (%s)" % (','.join(fields),','.join(values))
		app.config['cursor'].execute(sql)
		util.write_log(username, "create Services %s success"  % data['name'])
		return json.dumps({'code':0,'result':'create Services %s success'  % data['name']})
	except:
		logging.getLogger().error("create services error: %s"  % traceback.format_exc())
		return json.dumps({'code':1, 'errmsg':'create services error %s' % traceback.format_exc()})


@jsonrpc.method('services.get')
@auth_login
def get(auth_info, **kwargs):
	if auth_info['code']== 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	fields = ['id','name','dev_interface','sa_interface','remark']
	try:
		data = request.get_json()['params']
		if data.has_key('id'):
			sql = "select %s from Services where id = %s" % (','.join(fields), data['id'])
			app.config['cursor'].execute(sql)
			row = app.config['cursor'].fetchone()
			result = {}
			for i,k in enumerate(fields):
				result[k] = row[i]
			util.write_log(username,'select services success')
			return json.dumps({'code':0,'result':result})
		else:
			return json.dumps({'code':'1','errmsg':'must give services id'})
	except:
		logging.getLogger().error('select services error: %s'  % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'select services error'})




@jsonrpc.method('services.getlist')
@auth_login
def getlist(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	try:
		fields = ['id','name','dev_interface','sa_interface','remark']
		data = request.get_json()['params']
		sql = "select * from Services"
		app.config['cursor'].execute(sql)
		result = []
		count = 0
		for row in app.config['cursor'].fetchall():
			count += 1
			res = {}
			for i , k in enumerate(fields):
				res[k] = row[i]
			result.append(res)
		util.write_log(username, 'select services list success')
		return json.dumps({'code':0,'errmsg':result,'count':count})
	except:
		logging.getLogger().error("select services error: %s " % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'select services error'})




@jsonrpc.method('services.update')
@auth_login
def update(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	role = auth_info['role']
	if role != '0':
		return json.dumps({'code':1,'errmsg':'you are not admin!'})
	try:
		data = request.get_json()['params']
		if not data.has_key('id'):
			return json.dumps({'code':1,'errmsg':'must give an id!'})
		sql = 'update Services set name="%(name)s",dev_interface="%(dev_interface)s,sa_interface=%(sa_interface)s , remark=%(remark)s" where id=%(id)d'  % data
		app.config['cursor'].execute(sql)
		util.write_log(username, 'update services %s success'  % data['name'])
		return json.dumps({'code':0,'result':'update services %s successed'  %  data['name']})
	except:
		logging.getLogger().error('update services error: %s'  % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'update services error'})



@jsonrpc.method('services.delete')
@auth_login
def delete(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	role = int(auth_info['role'])
	if role != 0:
		return json.dumps({'code':1,'errmsg':'you are not admin!'})
	try:
		data = request.get_json()['params']
		if not data.has_key('id'):
			return	json.dumps({'code':1,'errmsg':'need give an id!'})
		sql = 'delete from Services where id= %d' % data['id']
		app.config['cursor'].execute(sql)
		util.write_log(username , 'delete services %s success' % data['name'])
		return json.dumps({'code':0,'result':'delete %s success' % data['name']})
	except:
		logging.getLogger().error('delete services error: %s' % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'delete services error'})


@jsonrpc.method('services.test')
@auth_login
def test(auth_info, **kwargs):
	print 'hello, test'
	return  'hello,sky-du'
