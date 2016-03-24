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

#获取某个项目最近上线的那一条记录
@jsonrpc.method('project_test.get')
@auth_login
def project_test_get(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    try:
        
        fields = ['project_id','host','commit','pusher','push_date']
        result = []
#        data = request.get_json()['params']
#        where = kwargs.get('where',None)
#        result = app.config['cursor'].get_results('project_test',fields,where,'push_date',False,(0,1))
#        print "result = ",result
        sql = 'select project_id, host, commit, pusher, push_date from (select project_id, host, commit, pusher, push_date from project_test order by push_date desc) as sort_project_test group by project_id'
        app.config['cursor'].execute(sql)
        for row in  app.config['cursor'].fetchall():
            res = {}
            for i,k in enumerate(fields):
                res[k] = row[i]
            result.append(res)
        print "result =",result
        util.write_log(username, '查询项目成功') 
        return json.dumps({'code':0,'result':result},cls=MyEncoder)
    except:
        logging.getLogger().error("select project error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '查询项目错误'})

#获取所有项目的上线的所有上线的历史记录或者某个项目的所有上线的历史记录
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

#获取每个项目所对应的测试主机
#@jsonrpc.method('test_host.getlist')
@app.route('/api/testhost',methods=['GET','POST'])
@auth_login
def project_test_getlist(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        fields = ['project_id','host','commit','pusher','push_date','comment']
        conf = util.ProjectConfig('../ip.conf')
        projects = util.userproject(username)
        print "projects",projects
        print "projects.values():",projects.values()
        print "projects.keys()",projects.keys()
        result = conf.gets(projects.values())
        for res in result:
            result[res] = ','.join(list(result[res]))
#        for pro_id in projects.keys():
#            where = {'project_id':int(pro_id)}
#            print where
#            res_latest = app.config['cursor'].get_results('project_test',fields,where,'push_date',False,(0,1))
#            print "res_latest",res_latest
        return json.dumps({'code':0,'result':result})
    except:
        logging.getLogger().error("/api/testhost: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '调用/api/testhost错误'})
