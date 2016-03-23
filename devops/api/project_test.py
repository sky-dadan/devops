#!/usr/bin/env python
#coding: utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app, jsonrpc
import logging, util
import json, traceback,os
from auth import auth_login
import time,requests
from jsondate import MyEncoder
from user_perm import getid_list


#headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }
headers = {"Content-Type": "application/json"}

@jsonrpc.method('project_test.create')
@auth_login
def project_test_create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    field = ['project_id','host','commit','pusher','push_date','comment']
    try:
        data = request.get_json()['params']
        #项目上线时间
        data['push_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        print data        
        app.config['cursor'].execute_insert_sql('project_test', data)
        util.write_log(username,{'code':0,'result':'add project_test success'})
        return json.dumps({'code':0,'result':'add project_test success'})    
    except:
        logging.getLogger().error('add project_test error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'add project_test error'})

@jsonrpc.method('project_test.get')
@auth_login
def project_test_get(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    try:
        
        fields = ['project_id','host','commit','pusher','push_date','comment']
        data = request.get_json()['params']
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_results('project_test',fields,where)
        util.write_log(username, '查询项目成功') 
        return json.dumps({'code':0,'result':result},cls=MyEncoder)
    except:
        logging.getLogger().error("select project error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '查询项目错误'})

@jsonrpc.method('project_test.getlist')
@auth_login
def project_test_getlist(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    try:
        
        fields = ['project_id','host','commit','pusher','push_date','comment']
        data = request.get_json()['params']
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_results('project_test',fields,where)
        util.write_log(username, '查询项目成功') 
        return json.dumps({'code':0,'result':result},cls=MyEncoder)
    except:
        logging.getLogger().error("select project error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '查询项目错误'})

@app.route('/api/testhost',methods=['GET','POST'])
@auth_login
def project_test_getlist(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        conf = util.ProjectConfig('../ip.conf')
        projectlist = util.userproject(username)
        result = conf.gets(projectlist)
        for res in result:
            result[res] = ','.join(list(result[res]))
        return json.dumps({'code':0,'result':result})
    except:
        logging.getLogger().error("/api/testhost: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '调用/api/testhost错误'})
