#!/usr/bin/env python
#coding: utf-8
from flask import Flask ,request
from flask_jsonrpc import JSONRPC
from . import app , jsonrpc
import logging, util
from auth import auth_login
import json,traceback

@jsonrpc.method('idc.create')
@auth_login
def create(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	role = int(auth_info['role'])
	if role != 0:
		return json.dumps({'code':1, 'errmsg':'you are not admin'})
	try:
		data = request.get_json()['params']
		fields, values = [], []
		for k, v in data.items():
			fields.append(k)
			values.append("'%s'"  % v)
		sql = "insert into Idc (%s)  values (%s)"   % (','.join(fields), ','.join(values))
		app.config['cursor'].execute(sql)
		util.write_log(username, "create idc %s success"  %  data['name'])
		return json.dumps({'code':0, 'result': 'create %s success' % data['name']})
	except:
		logging.getLogger().error("create Idc error: %s"   %  traceback.format_exc())
		return json.dumps({'code':1, 'errmsg':'Idc create error'})


@jsonrpc.method('idc.get')
@auth_login
def idc_get(auth_info,**kwargs):
	if auth_info['code']==1:
		return json.dumps(auth_info)
	username = auth_info['username']
	try:
		output = kwargs.get('output', [])
		where = kwargs.get('where', None)
		if len(output) == 0:
			fields = ['id','idc_name','name','address','email','interface_user','user_phone','pact_cabinet_num','rel_cabinet_num','remark']
		else:
			fields = output
		if where.has_key('id'):
			sql = "select %s from Idc where id = %s" % (','.join(fields), where['id'])
			app.config['cursor'].execute(sql)
			row = app.config['cursor'].fetchone()
			result = {}
			for i,k in enumerate(fields):
				result[k] = row[i]
			util.write_log(username, 'select idc information success')
			return json.dumps({'code':0,'result':result})
		else:
			return json.dumps({'code':1,'errmsg':'must input Idc id'})
	except:
		logging.getLogger().error("select idc error: %s"  % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'select idc error~'})
			

@jsonrpc.method('idc.getlist')
@auth_login
def idc_getlist(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	try:
		output = kwargs.get('output', [])
		if len(output) == 0:
			fields = ['id','idc_name','name','address','email','interface_user','user_phone','pact_cabinet_num','rel_cabinet_num','remark']
		else:
			fields = output
		sql = "select %s from Idc"  %  ','.join(fields)
		app.config['cursor'].execute(sql)
		result = []
		count = 0
		for row in app.config['cursor'].fetchall():
			count += 1
			res = {}
			for i,k in enumerate(fields):
				res[k] = row[i]
			result.append(res)
		util.write_log(username,'select idc list success')
		return json.dumps({'code':0, 'result':result, 'count':count})
	except:
		logging.getLogger().error("select idc list error: %s"   %  traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'select idc list error'})



@jsonrpc.method('idc.update')
@auth_login
def idc_update(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	role = int(auth_info['role'])
	if role != 0:
		return json.dumps({'code':1 ,'errmsg':'you are not admin!'})
	try:
		data = kwargs.get('data',None)
		where = kwargs.get('where', None)
		if not where.has_key('id'):
			return json.dumps({'code':1,'errmsg':'you must give an id!'})
		sql = 'update Idc set idc_name="%(idc_name)s", name="%(name)s", address="%(address)s",email="%(email)s",interface_user="%(interface_user)s",user_phone="%(user_phone)s",pact_cabinet_num="%(pact_cabinet_num)s",rel_cabinet_num="%(rel_cabinet_num)s",remark="%(remark)s" where id = "%%d"' % data  % where['id']
		app.config['cursor'].execute(sql)
		util.write_log(username,'update idc %s success'  % data['name'])
		return json.dumps({'code':0,'result':'update %s success' % data['name']})
	except:
		logging.getLogger().error("update idc error:  %s"  % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'update idc error'})


@jsonrpc.method('idc.delete')
@auth_login
def idc_delete(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	role = int(auth_info['role'])
	if role != 0:
		return json.dumps({'code':1, 'errmsg':'you are not admin!'})
	try:
		data = request.get_json()['params']
		if not data.has_key('id'):
			return json.dumps({'code':1,'errmsg':'you need give an id!'})
		sql = 'delete from Idc where id = %d' % data['id']
		app.config['cursor'].execute(sql)
		util.write_log(username, 'delete idc  success')
		return json.dumps({'code':0,'result':'delete success'})
	except:
		logging.getLogger().error('delete idc error : %s'  %  traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'delete idc error'})
			
@jsonrpc.method('idc.test')
@auth_login
def test(auth_info):
	print auth_info
	print "hello,test"
	return "hello, sky-du"
