#!/usr/bin/env python
#coding: utf-8
from jsondate import MyEncoder
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app, jsonrpc
import logging, util
import json, traceback
from auth import auth_login
from jsondate import MyEncoder
from user_perm import getid_list


#申请列表，任务列表
@jsonrpc.method('apply.getlist')
@auth_login
def apply_list(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        if auth_info['role'] == '0'  or  1:   #如果为管理人员或者是测试组的人员
            output = ['id','project_id','info','applicant','version','commit','apply_date','apply_status','detail']
            fields = kwargs.get('output', output)
            where = {'apply_status':['1','2']}
            result = app.config['cursor'].get_results('project_apply',fields,where)
            util.write_log(username, 'get apply list success!')
            return  json.dumps({'code':0, 'result':result,'count':len(result)},cls = MyEncoder)
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
        output = ['id','project_id','info','applicant','version','commit','apply_date','apply_status','detail']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        print where
        result = app.config['cursor'].get_one_result('project_apply',fields,where)
        print result
        if result:
            util.write_log(username, 'get one apply detail success')
            return json.dumps({'code':0,'result':result},cls=MyEncoder)
    except:
        logging.getLogger().error("get apply detail faild : %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'get apply detail error:%s' % traceback.format_exc()})


#仿真发布
@jsonrpc.method('apply.emulation')
@auth_login
def apply_emula(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        data = request.get_json()['params']
        where = data.get('where',None)
        data = data.get('data',None)
        print data, where
        #脚本打上tag,触发仿真测试代码脚本, 返回执行结果 更新project_apply为2  灰度发布中,插入一条记录到project_deploy,状态为2
        util.script()

        app.config['cursor'].update_sql('project_apply',{'apply_status':'2'},where)

        app.config['cursor'].execute_insert_sql('project_apply',data)
        
        return json.dumps({'result':data,'where':where})

    except:
        pass
        return json.dumps({'code':1,'errmsg':'apply.emulation error %s......' % traceback.format_exc()})


#仿真取消按钮
#@app.route('/emulation/cancel',methods=['POST'])
@jsonrpc.method('apply.cancel')
@auth_login
def cancel(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0' or 2:    #不是测试组
        return json.dumps({'code':1,'errmsg':'管理员和测试人员才有此权限'})
    try:
        data = request.get_json()['params']       #只需要获取id
        where = data.get('where',None)
        data = data.get('data',None)

        #添加为project_deploy插入的准备数据， 比如project_deploy status
        app.config['cursor'].update_sql('project_apply',{'apply_status':'4'},where)
        app.config['cursor'].execute_insert_sql('project_deploy',data, where)
        util.scirpt()

    except:
        pass
        

#正式发布按钮
@jsonrpc.method('apply.deploy')
@auth_login
def deploy(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['code'] != '0'  or 2:    #不是测试组
        return  json.dumps({'code':1,'errmsg':'管理员和测试人员才有此权限'})
    try:
        data = request.get_json()['params']    #获取需要更改的id, 和为下面更新的数据
        where = data.get('where',None)
        data = data.get('data',None)

        app.config['cursor'].update_sql('project_apply',{'apply_status':'3'},where)
        app.config['cursor'].execute_insert_sql('project_deploy',data, where)
        util.script()

    except:
        pass
        
