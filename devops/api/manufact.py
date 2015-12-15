#!/usr/bin/env python
#coding:utf-8

from flask import Flask,request
from flask_jsonrpc import JSONRPC
from . import app
import logging, util
import json, traceback
from auth import auth_login
from cabinet import jsonrpc


@jsonrpc.method('manufact.create')
@auth_login
def create(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	role = auth_info['role']
	if role != '0':
		return json.dumps({'code':1 ,'errmsg': "You are not admin"})
	try:
		data = request.get_json()['params']
		fields, values = [] ,[]
		for k, v in data.items():
			fields.append(k)
			values.append("'%s'"  %  v)
		sql = "insert into Manufacturers (%s)  values (%s) " % (','.join(fields),','.join(values))
		app.config['cursor'].execute(sql)
		util.write_log(username, 'create manufactures %s success'  % data['name'])
		return json.dumps({'code':0,'result':'create manufactures %s success'  %  data['name']})
	except:
		logging.getLogger().error('create manufactures error: %s'  % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'create manufacturers error'})
		

@jsonrpc.method('manufact.get')
@auth_login
def manufact_get(auth_info,**kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	fields = ['id','name','supplier_name','interface_user','email','user_phone']
	try:
		data = request.get_json()['params']
		if data.has_key('id'):
			sql = "select %s from Manufacturers where id = %d"  % (','.join(fields), data['id'])
			app.config['cursor'].execute(sql) 
			row = app.config['cursor'].fetchone()
			result = {}
			for i, k in enumerate(fields):
				result[k] = row[i]
			util.write_log(username, 'select manufacturers success')
			return json.dumps({'code':0,'result':result})
		else:
			return json.dumps({'code':1,'errmsg':'must give an id!'})
	except:
		logging.getLogger().error("select manufacturers error: %s"  % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'select manufacturers error'})


@jsonrpc.method('manufact.getlist')
@auth_login
def manufact_getlist(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	try:
		fields = ['id','name','supplier_name','interface_user','email','user_phone']
		data = request.get_json()['params']
		sql = "select * from Manufacturers"
		app.config['cursor'].execute(sql)
		result =  []
		count = 0
		for row in app.config['cursor'].fetchall():
			count += 1
			res = {}
			for i, k in enumerate(fields):
				res[k] = row[i]
			result.append(res)
		util.write_log(username, 'select manufact list success!')
		return json.dumps({'code':0, 'result':result,'count':count})
	except:
		logging.getLogger().error("select factmanu list error: %s"  % traceback.format_exc())
		return json.dumps({'code':1, 'errmsg':'select factmanu error~!'})


@jsonrpc.method('manufact.update')
@auth_login
def manufact_update(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	role = auth_info['role']
	if role != '0':
		return json.dumps({'code':1,'errmsg':'you are not admin!'})
	try:
		data = request.get_json()['params']
		print data
		if not data.has_key('id'):
			return json.dumps({'code':1,'errmsg':'must give an id~!'})
		print "hello"
		sql = "update Manufacturers set name='%(name)s', supplier_name='%(supplier_name)s' , interface_user='%(interface_user)s', email='%(email)s', user_phone='%(user_phone)s'  where id=%(id)d"  % data
		print sql
		app.config['cursor'].execute(sql)
		print "hello"
		util.write_log(username ,"update manufact %s success!"  %  data['name'])
		return json.dumps({'code':0, 'result':'update %s  success'  % data['name']})
	except:
		logging.getLogger('update manufact error: %s'  % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'update manufact error'})



@jsonrpc.method('manufact.delete')
@auth_login
def manufact_delete(auth_info,**kwargs):
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
		sql = "delete from Manufacturers where id = %d"  % data['id']
		app.config['cursor'].execute(sql)
		util.write_log(username, 'delete manufacturers %s success' % data['name'])
		return json.dumps({'code':0,'result':'delete manufact %s success'  % data['name']})
	except:
		logging.getLogger().error('delete manufact error: %s'  %  traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'delete manufact error~!'})


@jsonrpc.method('manufact.test')
@auth_login
def manufact_test(auth_info, **kwargs):
	data = request.get_json()
	print data
	return "Hello, sky-du!"
