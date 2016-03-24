#!/usr/bin/env python
#coding: utf-8
from jsondate import MyEncoder
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app, jsonrpc
import logging, util,time
import json, traceback,datetime
from auth import auth_login
from jsondate import MyEncoder
from user_perm import getid_list

#创建申请任务列表
@jsonrpc.method('apply.create') 
@auth_login
def apply_create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    field = ['project_id','info','applicant','commit','apply_date','status','detail']
    try:
        data = request.get_json()['params']  #project_id,project_name,applicant,info,detail
        data['commit']='11111'               #脚本获取
        data['apply_date'] = time.strftime('%Y-%m-%d %H:%M')
        data['status'] = 1
        where = {"project_id":int(data['project_id'])}
        data.pop('project_username')  
        res = app.config['cursor'].get_one_result('project_apply',field,where)
        if not res: 
            app.config['cursor'].execute_insert_sql('project_apply', data)
        else:
            app.config['cursor'].execute_update_sql('project_apply',data,where)
        app.config['cursor'].execute_insert_sql('project_deploy',data)  
        util.write_log(username,{'code':0,'result':'project apply success'})
        return json.dumps({'code':0,'result':'project apply  success'})    
    except:
        logging.getLogger().error('project apply error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'project apply error'})


#申请列表，任务列表
@jsonrpc.method('apply.getlist')
@auth_login
def apply_list(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','project_id','info','applicant','version','commit','apply_date','status','detail']
        fields = kwargs.get('output', output)
        loginname = app.config['cursor'].get_one_result('user',['name'],{'username':username})
        print loginname  #{'name': u'\u5218\u5b50\u5e73'} 
        loginer = app.config['cursor'].get_results('project_apply',fields,{'applicant':loginname['name']})

        where = {'status':['1','2']}
        result = app.config['cursor'].get_results('project_apply',fields,where)
        #id转换成名字
        id2name_project=util.getinfo('project',['id','name'])
        for res in result:
            res['project_name'] = id2name_project[str(res['project_id'])]           

        util.write_log(username, 'get apply list success!')
        return  json.dumps({'code':0,'data':loginer, 'result':result,'count':len(result)},cls = MyEncoder)
    except:
        logging.getLogger().error("select apply list error:%s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'apply.getlist error  : %s'  %  traceback.format_exc()})

#任务列表，详情按钮
@jsonrpc.method('apply.get')
@auth_login
def apply_one(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','project_id','info','applicant','version','commit','apply_date','status','detail']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('project_apply',fields,where)
        #id转换成名字
        id2name_project=util.getinfo('project',['id','name'])
        result['project_name'] = id2name_project[str(result['project_id'])] 

        util.write_log(username, 'get one apply detail success')
        return json.dumps({'code':0,'result':result},cls=MyEncoder)
    except:
        logging.getLogger().error("get apply detail faild : %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'err msg':'get apply detail error:%s' % traceback.format_exc()})


#仿真发布 脚本打上version版本号,触发仿真测试代码脚本, 返回执行结果 更新project_apply为2  灰度发布中,插入一条记录到project_deploy,状态为2
@jsonrpc.method('apply.emulation')
@auth_login
def apply_emulation(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        version = kwargs.get('version')
        id = kwargs.get('id')                   #web端 传递过来测试打上的version，申请项目的ID
        data, where = {'version':version,'status':'2'},{'id':id}
        logging.getLogger().info(data)
        app.config['cursor'].execute_update_sql('project_apply',data,where)
        util.write_log(username," emulation update  project_apply status 2")

        fields = ['project_id','info','applicant','version','commit','detail']  #为project_deplpy 准备数据
        result=app.config['cursor'].get_one_result('project_apply',fields,where)
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result['apply_date'] = time
        result['status'] = '2'                                                #将project_deploy status改为2 并且插入记录
        app.config['cursor'].execute_insert_sql('project_deploy',result)  
        util.write_log(username,"insert into project_deploy  status 2 ")
        return json.dumps({'code':0})
    except:
        logging.getLogger().error("apply.emulation get failed : %s" %  traceback.format_exc())
        return json.dumps({'code':1, 'errmsg':'apply.emulation get failed'})

#仿真失败，取消
@jsonrpc.method('apply.cancel')
@auth_login
def apply_cancel(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        id = kwargs.get('where')
        id = id['id']
        where,data = {'id':id},{'status':'4'}
        app.config['cursor'].execute_update_sql('project_apply',data,where)
        util.write_log(username,"cancel update project_apply status 4")
        
        fields = ['project_id','info','applicant','version','commit','detail']  #为project_deplpy 准备数据
        result=app.config['cursor'].get_one_result('project_apply',fields,where)
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result['apply_date'] = time
        result['status'] = '4'                                               
        app.config['cursor'].execute_insert_sql('project_deploy',result)
        util.write_log(username,"cancel insert project_deploy status  4")
        return json.dumps({'code':0})
    except:
        logging.getLogger().error("apply.cancel get failed : %s" % traceback.format_exc())
        return json.dumps({'code':1})


#仿真测试成功，正式上线
@jsonrpc.method("apply.success")
@auth_login
def annly_success(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        id = kwargs.get('where')
        id = id['id']
        where,data = {'id':id},{'status':'3'}
        app.config['cursor'].execute_update_sql('project_apply',data,where)
        util.write_log(username,"apply success update project_apply status 3")

        fields = ['project_id','info','applicant','version','commit','detail']  #为project_deplpy 准备数据
        result=app.config['cursor'].get_one_result('project_apply',fields,where)
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result['apply_date'] = time
        result['status'] = '3'                                               
        app.config['cursor'].execute_insert_sql('project_deploy',result)
        util.write_log(username,"apply success insert project_deploy status  3")
        return json.dumps({'code':0})
    except:
        logging.getLogger().error("apply success  get failed : %s" % traceback.format_exc())
        return json.dumps({'code':1})
