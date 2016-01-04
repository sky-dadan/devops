#!/usr/bin/env python
#coding:utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app , jsonrpc
import logging, util
from auth import auth_login
import json, traceback

# 关于权限这一块的增删改查

@jsonrpc.method('power.create')
@auth_login
def create(auth_info,**kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	if auth_info['role'] != '0':
		print "you are not admin"
		return json.dumps({'code':1,'errmsg':'you are not admin'})
	try:
		data = request.get_json()['params']
		print data
		fields, values = [],[]
		for k , v in data.items():
			fields.append(k)
			values.append("'%s'"  % v)
		sql = "insert into power (%s) values (%s)"  % (','.join(fields), ','.join(values))
		app.config['cursor'].execute(sql)
		util.write_log(username, "create power %s success"  %  data['name'])
		return json.dumps({'code':0,'result':'create %s scucess' %  data['name']})
	except:
		logging.getLogger().error('create power error:%s' % traceback.format_exc())
		return json.dumps({'code':1,'errmsg': traceback.format_exc()})


@jsonrpc.method('power.delete')
@auth_login
def delete(auth_info,**kwargs):
	if auth_info['code']==1:
		return json.dumps(auth_info)
	username = auth_info['username']
	if auth_info['role'] != '0':
		print "you are not admin"
		return json.dumps({'code':1,'errmsg':'you are not admin'})
	try:
		data = request.get_json()['params']
		if not data.has_key('id'):
			return json.dumps({'code':1,'errmsg':'you have give an id'})
		sql_re = "select name, url from power where id = '%s'"  % data['id']
		print sql_re
		app.config['cursor'].execute(sql_re)
		record = app.config['cursor'].fetchone()
		sql = "delete from power where id = '%s'" % data['id']
		print sql
		app.config['cursor'].execute(sql)
		util.write_log(username, "delete permission  %s  success"  % record[0])
		return json.dumps({'code':0,'result':'delete permisson %s scucess' % record[0]})
	except:
		logging.getLogger().error("delete permission error:%s" % traceback.format_exc())
		return json.dumps({'code':1,'errmsg': traceback.format_exc()})



@jsonrpc.method('power.getlist')
@auth_login
def getlist(auth_info,**kwargs):
	if auth_info['code']==1:
		return json.dumps(auth_info)
	username = auth_info['username']
	if auth_info['role'] != '0':
		print "you are not admin"
		return json.dumps({'code':1,'errmsg':'you are not admin'})
	try:
		output = kwargs.get('output',[])
		if len(output) == 0:
			fields = ['name','name_cn','url','info']
		else:
			fields = output
		sql = "select %s from power" % ','.join(fields)
		app.config['cursor'].execute(sql)
		result = []
		count = 0
		for row in app.config['cursor'].fetchall():
			res = {}
			count += 1
			for i, k in enumerate(fields):
				res[k] = row[i]
			result.append(res)
		util.write_log(username, 'select power list success')
		return json.dumps({'code':0,'result':result,'count':count})
	except:
		logging.getLogger().error("get list permission error: %s"  %  traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'getlist error : %s'  % traceback.format_exc()})

@jsonrpc.method('power.get')
@auth_login
def getbyid(auth_info,**kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	try:
		output = kwargs.get('output',[])
		where = kwargs.get('where',None)
		if len(output) == 0:
			fields = ['id','name','name_cn','url','info']
		else:
			fields = output
		if where.has_key('id'):
			sql = "select %s from power where id=%d" % (','.join(fields), where['id'])
			app.config['cursor'].execute(sql)
			row = app.config['cursor'].fetchone()
			result = {}
			for i, k in enumerate(fields):
				result[k]=row[i]
			util.write_log(username,'select power by id successed!')
			return json.dumps({'code':0, 'result':result})
		else:
			return json.dumps({'code':1, 'errmsg':'you need give an id!'})
	except:
		logging.getLogger().error("select power by id error: %s" %  traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'select error : %s' % traceback.format_exc()})


@jsonrpc.method('power.update')
@auth_login
def update(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	if auth_info['role'] != '0':
		return json.dumps({'code':1,'errmsg':'you are not admin'})
	try:
		data = request.get_json()['params']
		where = data.get('where',None)
		data = data.get('data',None)
		if not where.has_key('id'):
			return json.dumps({'code':1,'errmsg':'you need give an id!'})	
		sql = "update power set name='%(name)s', name_cn='%(name_cn)s', url='%(url)s', info='%(info)s' where id=%%d" % data % where['id']
		print sql
		app.config['cursor'].execute(sql)
		util.write_log(username,"update %s successed" % data['name'])
		return json.dumps({'code':0,'result':'update %s successed' % data['name']})
	except:
		logging.getLogger().error("update error: %s" % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'error: %s' %  traceback.format_exc()})
