#!/usr/bin/env python
#coding: utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app, jsonrpc
import logging, util
import json, traceback
from auth import auth_login
import time
from jsondate import MyEncoder


#获取用户信息或组信息，返回例如用户信息：{'1':'tom','2','jerry'};组信息{'1':'sa','2':'ask'}
def getinfo(table_name,fields):
    result = app.config['cursor'].get_results(table_name,fields)
    result = dict([(str(x[fields[0]]), x[fields[1]]) for x in result])
    return result

#将用户id替换为username,组id替换为name
def id2name(pro_perm_result,fields,users,groups):
    for res in pro_perm_result:
        for key in fields:
            if not key.find('user'):
                res[key] = ','.join([users[x] for x in res[key].split(',') if x in users]) if res[key] else ''
            elif not key.find('group'):
                res[key] = ','.join([groups[x] for x in res[key].split(',') if x in groups]) if res[key] else ''
            else:
                continue

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
		return json.dumps({'code':0,'result':'create  %s success'  %  data['name']})	
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
		return json.dumps({'code':0,'result':'update project %s success' % data['name']})
	except:
		logging.getLogger().error("update project error : %s" % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'update project error'})
@jsonrpc.method('git.get')
@auth_login
def create(auth_info, **kwargs):
    if auth_info['code'] == 1:
	return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
	return json.dumps({'code':1,'errmsg':'you are not admin'})
    try:
        pro_fields = ['id','name','path','principal','create_date','is_lock','comment']
        pro_perm_fields = ['user_all_perm','group_all_perm','user_rw_perm','group_rw_perm']
        data = request.get_json()
        data = data['params']
        users = getinfo('user',['id','username'])
        groups = getinfo('groups',['id','name'])
        # 条件,项目ID 例如：{'id':1}
        where = kwargs.get('where',None)
        #得到项目id为where条件的结果
        result = app.config['cursor'].get_one_result('project', pro_fields,where) 
        #更新result['principal']的值，将id替换成负责人的用户名
        result['principal'] = users[str(result['principal'])]
        #将项目的id做为条件
        where = {'id':int(result['id'])} 
        #查出项目id对应的权限
        pro_perm_result = app.config['cursor'].get_one_result('project_perm',pro_perm_fields,where) 
        #将用户id替换为用户名,组id替换为组名
        id2name([pro_perm_result],pro_perm_fields,users,groups)
        #将更新后的结果追加到result字典里
        result.update(pro_perm_result) 

        util.write_log(username, 'select project sucess') 
        return json.dumps({'code':0,'result':result},cls=MyEncoder)
    except:
        logging.getLogger().error("select project error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'select project error'})

@jsonrpc.method('git.getlist')
@auth_login
def create(auth_info, **kwargs):
    if auth_info['code'] == 1:
	return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
	return json.dumps({'code':1,'errmsg':'you are not admin'})
    try:
        pro_fields = ['id','name','path','principal','create_date','is_lock','comment']
        pro_perm_fields = ['id','user_all_perm','group_all_perm','user_rw_perm','group_rw_perm']
        data = request.get_json()
        data = data['params']
        #user表里查出id,username,将查出来的数据改成例如{'1':'tom','2':'jerry'}重新赋值
        users = getinfo('user',['id','username'])
        #groups表里查出id,name,将查出来的数据改成例如{'1':'sa','2':'ask'}
        groups = getinfo('groups',['id','name']) 
        #查出项目列表
        result = app.config['cursor'].get_results('project', pro_fields)
        #将负责人id替换成name
        for res in result:
            res['principal'] = users[str(res['principal'])]
        #查出项目权限列表
        pro_perm_result = app.config['cursor'].get_results('project_perm',pro_perm_fields)
        # 将权限表里的用户id,组id，替换成用户名，组名
        id2name(pro_perm_result,pro_perm_fields,users,groups)
        #将权限信息追加到result字典里
        for project in result:
            for pro_perm in pro_perm_result:
                if project['id'] == pro_perm['id']:
                    project.update(pro_perm)
        util.write_log(username, 'select project list sucess') 
        return json.dumps({'code':0,'result':result,'count':len(result)},cls=MyEncoder)
    except:
        logging.getLogger().error("select project list error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'select project list error'})
