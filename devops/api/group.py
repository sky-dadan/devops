#!/usr/bin/env python
#coding:utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app , jsonrpc
import logging, util
from auth import auth_login
import json, traceback

#这里是关于用户权限的查看，修改  组的增删改查

@jsonrpc.method('groups.getlist')
@auth_login
def role_select(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','name','name_cn','p_id','info']
        data = request.get_json()['params']
        fields = data.get('output', output)

        result = app.config['cursor'].get_results('power', ['id', 'name'])
        perm_name = dict([(x['id'], x['name']) for x in result])

        result = []
        res = app.config['cursor'].get_results('groups', fields)
        for x in res:
            p_name = [perm_name[int(p_id)] for p_id in x['p_id'].split(',')]
            x['p_id'] = ','.join(p_name)
            result.append(x)

	util.write_log(username, 'select groups list success')
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error("select groups list error: %s"  %  traceback.format_exc())
	return json.dumps({'code':1,'errmsg':'error : %s' %  traceback.format_exc()})

@jsonrpc.method('groups.get')
@auth_login
def groups_get(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','name','name_cn','p_id','info']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('groups', fields, where)
        if result is None:
            return json.dumps({'code':1, 'errmsg':'must need give an id'})
        else:
	    util.write_log(username, "select groups by id success")
	    return json.dumps({'code':0,'result':result})
    except:
        logging.getLogger().error('select groups by id error: %s'  % traceback.format_exc())
        return  json.dumps({'code':1,'errmsg':'select groups error'})

@jsonrpc.method('groups.create')
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
        app.config['cursor'].execute_insert_sql('groups', data)
	util.write_log(username, "create groups %s scucess" %  data['name'])
	return json.dumps({'code':0,'result':'create groups %s successed' % data['name']})
    except:
        logging.getLogger().error(username,"create groups    error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'error:%s' % traceback.format_exc()})

@jsonrpc.method('groups.delete')
@auth_login
def role_delete(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code':1,'errmsg':'you are not admin'})
    try:
        data = request.get_json()['params']
        result = app.config['cursor'].execute_delete_sql('groups', data)
        if result == '':
            return json.dumps({'code':1,'errmsg':'you need give an id!'})
	util.write_log(username, 'delete groups successed')
	return json.dumps({'code':0,'result':'delete groups successed'})
    except:
        logging.getLogger().error('delete groups error: %s' %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'error: %s'  % traceback.format_exc()})

@jsonrpc.method('groups.update')
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
	data = data.get('data',None)
        result = app.config['cursor'].execute_update_sql('groups', data, where, ['name', 'name_cn', 'p_id', 'info'])
        if result == '':
            return json.dumps({'code':1, 'errmsg':'you need give an id!'})
	util.write_log(username, 'update groups %s success!' % data['name'])
	return json.dumps({'code':0,'result':'update groups %s successed' % data['name']})
    except:
        logging.getLogger().error("update error: %s"  % traceback.format_exc())
	return json.dumps({'code':1,'errmsg':"error : %s" % traceback.format_exc()})

