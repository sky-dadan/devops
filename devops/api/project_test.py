#!/usr/bin/env python
#coding: utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app, jsonrpc
import logging, util
import json, traceback,os,sys
from auth import auth_login
import time,requests
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
    field = ['project_id','host','commit','pusher','push_date','comment']
    try:

        data = request.get_json()['params']
        #执行上线脚本
        result = app.config['cursor'].get_one_result('git', ['name'], {'id': data['project_id']})
        if not result:
            return json.dumps({'code': 1, 'errmsg': '发布的项目不存在'})
        work_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        ret, msg = util.run_script_with_timeout("%s/online_test_dev.sh %s %s" % (app.config['script_path'], result['name'], data['host']))
        if not ret:
            return json.dumps({'code':1,'errmsg':msg})

        #从脚本获取的两部分内容，一部分是代码Git信息，另一部分是同步的结果
        i = msg.find('|ERR:')
        info, err = (msg[:i], msg[i+1:]) if i > 0 else (msg, '')

        #获取上线人，上线时间，commit号，上线说明,然后插入到数据库里
        data['pusher'] = username
        data['push_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        data['commit'] = info[:7]
        data['comment'] = info[8:]

        if err:
            return json.dumps({'code': 1, 'errmsg': '\n'.join(err.split('|'))})

        app.config['cursor'].execute_insert_sql('project_test', data)
        util.write_log(username,{'code':0,'result':'add project_test success'})
        return json.dumps({'code':0,'result':'测试发布完成'})    
    except:
        logging.getLogger().error('add project_test error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'测试发布失败'})


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
        projects = util.user_projects(username, app.config['cursor'])
        for res in result:
            res['project_id'] = projects[str(res['project_id'])]
            res['push_date'] = str(res['push_date'])
        util.write_log(username, '查询项目成功') 
        return json.dumps({'code':0,'result':result})
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
            res['push_date'] = str(res['push_date'])
            result.append(res)
        app.config['cursor'].close_db()
        util.write_log(username, '查询项目成功') 
        return json.dumps({'code':0,'result':result})
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
        projects = util.user_projects(username, app.config['cursor'])
        result = []
        for k in projects:
            result.append({'id': k, 'name': projects[k], 'host': ','.join(list(conf.get(projects[k])))})
        return json.dumps({'code':0,'result':result})
    except:
        logging.getLogger().error("获取测试主机失败: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '获取测试主机失败'})
