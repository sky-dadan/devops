#!/usr/bin/env python
#coding: utf-8
from flask import Flask, request
from . import app, jsonrpc
import logging, util, time
import json, traceback
from auth import auth_login
from jsondate import MyEncoder

#创建工单申请任务
@jsonrpc.method('opsjob.create')
@auth_login
def opsjob_create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        data = request.get_json()['params']
        data['apply_date'] = time.strftime('%Y-%m-%d %H:%M')
        data['status'] , data['apply_persion'] = 0, username
        app.config['cursor'].execute_insert_sql('ops_jobs',data)
        util.write_log(username, "create opsjonb  create")
        print data
        return json.dumps({'code':0,'result':'创建工单成功!'})
    except:
        logging.getLogger().error('opsjob create error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'工单申请失败!'})

#获取一个工单详细信息
@jsonrpc.method('opsjob.get')
@auth_login
def opsjob_get(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dump(auth_info)
    try:
        username = auth_info['username']
        where = kwargs.get('where',None)
        output = ['id','apply_date','apply_type','apply_desc','deal_persion','status','deal_desc','deal_time','apply_persion']
        fields = kwargs.get('output',output)
        result = app.config['cursor'].get_one_result('ops_jobs',fields,where)
        util.write_log(username, 'get one opejobs detail success!')
        return json.dumps({'code':0,'result':result},cls=MyEncoder)
    except:
        logging.getLogger().error('get one ops_jobs detail error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':"获取工单详情失败!"})

#获取申请，处理中的工单列表
@jsonrpc.method('opsjob.getad')
@auth_login
def opsjob_getadmin(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    try:
        username = auth_info['username']
        where = {'status':['2','3']}
        fields = ['id','apply_date','apply_type','apply_desc','deal_persion','status','deal_desc','deal_time','apply_persion']
        result = app.config['cursor'].get_results('ops_jobs',fields,where)
        print result
        util.write_log(username, 'get opsjob status in (2,3) success!') 
        return json.dumps({'code':0,'result':result,'count':len(result)},cls=MyEncoder)
    except:
        logging.getLogger().error("select opsjob status in (2,3) error : %s"  % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'select opsjob status in (2,3) error!'})


#获取所有工单列表
@jsonrpc.method('opsjob.getlist')
@auth_login
def opsjob_list(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    try:
        username = auth_info['username']
        output = ['id','apply_date','apply_type','apply_desc','deal_persion','status','deal_desc','deal_time','apply_persion']
        fields = kwargs.get('output',output)
        result = app.config['cursor'].get_results('ops_jobs',fields)
        util.write_log(username,' get all opsjob list success')
        return json.dumps({'code':0,'result':result,'count':len(result)},cls=MyEncoder)
    except:
        logging.getLogger().error("select ops_jobs list error: %s" % traceback.format_exc())
        return json.dumps({'code':1, 'errmsg':'获取工单列表失败!'})


#工单处理
@jsonrpc.method('opsjob.deal')
@auth_login
def opsjob_deal(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    if auth_info['role'] != '0':
        return json.dumps({'code':1,'errmsg':'只有管理员才有此权限'})
    try:
        username = auth_info['username']
        data = request.get_json()['params']   # data = {'where':{'id':3},'status':0,'deal_desc':'deal desc comment'}
        data['deal_persion'] = username
        where = data['where']
        data.pop('where')
        if data['status'] == 0:       #工单改为处理状态
            data['status'] = 1
            app.config['cursor'].execute_update_sql('ops_jobs',data,where)
            util.write_log(username, ' opsjobs 正在处理中......')
            print  data,where
            return json.dumps({'code':0,'result':'工单正在处理中......'})
        else:                          #工单处理结束
            data['deal_time'] = time.strftime("%Y-%m-%d %H:%M")
            app.config['cursor'].execute_update_sql('ops_jobs',data,where)
            util.write_log(username, 'finish the ope job')
            return json.dumps({'code':0,'result':'ope job处理完成!'})
    except:
        logging.getLogger().error('opsjob finish error : %s'  % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'工单处理失败!'})

