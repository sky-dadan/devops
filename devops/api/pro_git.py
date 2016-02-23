#!/usr/bin/env python
#coding: utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app, jsonrpc
import logging, util
import json, traceback
from auth import auth_login
import time


@jsonrpc.method('git.create')
@auth_login
def create(auth_info, **kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	role = int(auth_info['role'])
	if role != 0:
		return json.dumps({'code':1,'errmsg':'you are not admin'})
	p_data, p_perm_data = {},{}     # p_data是project表的相关数据，p_perm_data是project_perm表的相关数据
	pro_field = ['name','path','principal','create_date','is_lock','comment']
	try:
		data = request.get_json()['params']
		data['create_date'] = time.strftime('%Y-%m-%d %H:%M:%S')    #添加项目创建时间
		for key in data:
			if key in pro_field:
				p_data[key] = data[key]
			else:
				p_perm_data[key] = data[key]
		app.config['cursor'].execute_insert_sql('project',p_data)
		p_id = app.config['cursor'].get_one_result('project',['id'],{'name':p_data['name']})   #获取当前创建项目的id
		p_perm_data['id'] = p_id['id']					#创建project_perm准备的数据
		app.config['cursor'].execute_insert_sql('project_perm',p_perm_data)
		util.write_log(username,{'code':0,'result':'create  %s success'  %  data['name']})
	except:
		logging.getLogger().error('create project error: %s' % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'git project create error'})


@jsonrpc.method('git.update')
@auth_login
def update(auth_info,**kwargs):
	if auth_info['code'] == 1:
		return json.dumps(auth_info)
	username = auth_info['username']
	role = int(auth_info['role'])
	if role != 0:
		return json.dumps({'code':1,'errmsg':'you are not admin'})
	p_data, p_perm_data = {},{}
	pro_field = ['name','path','principal','create_date','is_lock','comment']
	try:
		data = kwargs.get('data',None)
		where = kwargs.get('where',None)
		for key in data:
			if key in pro_field:
				p_data[key] = data[key]
			else:
				p_perm_data[key] = data[key]
		result = app.config['cursor'].execute_update_sql('project',p_data,where)
		result2 = app.config['cursor'].execute_update_sql('project_perm',p_perm_data,where)
		if result == '' or result2 == '':
			return json.dumps({'code':1,'errmsg':'you must give an id!'})
		util.write_log(username,'update project %s success' % data['name'])
	except:
		logging.getLogger().error("update project error : %s" % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'update project error'})

