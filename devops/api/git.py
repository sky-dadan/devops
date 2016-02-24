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
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('project', pro_fields,where)
        where = {'id':int(result['id'])}
        pro_perm_result = app.config['cursor'].get_one_result('project_perm',pro_perm_fields,where)
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
        result = app.config['cursor'].get_results('project', pro_fields)
        pro_perm_result = app.config['cursor'].get_results('project_perm',pro_perm_fields)
        for project in result:
            for pro_perm in pro_perm_result:
                if project['id'] == pro_perm['id']:
                    project.update(pro_perm)
        print "final_result =",result
        util.write_log(username, 'select project list sucess') 
        return json.dumps({'code':0,'result':result,'count':len(result)},cls=MyEncoder)
    except:
        logging.getLogger().error("select project list error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'select project list error'})

