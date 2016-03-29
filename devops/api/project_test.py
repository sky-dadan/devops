#!/usr/bin/env python
#coding: utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app, jsonrpc
import logging, util
import json, traceback,os,sys
from auth import auth_login
import time,requests
from jsondate import MyEncoder
from user_perm import getid_list


#headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }
headers = {"Content-Type": "application/json"}

#插入一条上线记录
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
        #执行上线脚本
        projects = util.userproject(username)
        work_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        script_dir = os.path.join(work_dir,'script/online')
        script_result = util.run_script_with_timeout("sh %s/online_test_dev.sh %s %s" % (script_dir,projects[int(data['project_id'])],data['host']))

        #获取上线上，上线时间，commit号，上线说明,然后插入到数据库里
        data['pusher'] = username
        data['push_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        data['commit'] = script_result[:7]
        data['comment'] = script_result[8:]

        app.config['cursor'].execute_insert_sql('project_test', data)
        util.write_log(username,{'code':0,'result':'add project_test success'})
        return json.dumps({'code':0,'result':'add project_test success'})    
    except:
        logging.getLogger().error('add project_test error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'add project_test error'})


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
        result = app.config['cursor'].get_results('project_test',fields,where,'push_date',False)
        print "result =",result
        projects = util.userproject(username)
        print "projects =",projects
        for res in result:
            res['project_id'] = projects[res['project_id']]
        util.write_log(username, '查询项目成功') 
        return json.dumps({'code':0,'result':result},cls=MyEncoder)
    except:
        logging.getLogger().error("select project error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '查询项目错误'})

#获取所有项目最近上线的那一条记录
@jsonrpc.method('lastest_record.getlist')
@auth_login
def project_test_get(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    try:
        
        fields = ['project_id','commit','pusher','push_date','comment']
        result = []
        sql = 'SELECT %s FROM (SELECT %s FROM project_test ORDER BY push_date DESC) AS sort_project_test GROUP BY project_id' %(','.join(fields),','.join(fields))
        app.config['cursor'].execute(sql)
        for row in  app.config['cursor'].fetchall():
            res = {}
            for i,k in enumerate(fields):
                res[k] = row[i]
            result.append(res)
        util.write_log(username, '查询项目成功') 
        return json.dumps({'code':0,'result':result},cls=MyEncoder)
    except:
        logging.getLogger().error("select project error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '查询项目错误'})

#获取每个项目所对应的测试主机
#@app.route('/api/testhost',methods=['GET','POST'])
@jsonrpc.method('test_host.getlist')
@auth_login
def project_test_getlist(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        work_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        conf_name = os.path.join(work_dir, 'testhost.conf')
#        conf_name = app.config['test_host']
        conf = util.ProjectConfig(conf_name)
        projects = util.userproject(username)
        result = conf.gets(projects.values())
        for res in result:
            result[res] = ','.join(list(result[res]))
        return json.dumps({'code':0,'result':result})
    except:
        logging.getLogger().error("获取测试主机失败: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '获取测试主机失败'})
