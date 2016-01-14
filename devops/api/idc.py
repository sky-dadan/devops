#!/usr/bin/env python
#coding: utf-8
from flask import Flask ,request
from flask_jsonrpc import JSONRPC
from . import app , jsonrpc
import logging, util
from auth import auth_login
import json,traceback

@jsonrpc.method('idc.create')
@auth_login
def create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1, 'errmsg':'you are not admin'})
    try:
        data = request.get_json()['params']
        app.config['cursor'].execute_insert_sql('Idc', data)
        util.write_log(username, "create idc %s success"  %  data['name'])
        return json.dumps({'code':0, 'result': 'create %s success' % data['name']})
    except:
        logging.getLogger().error("create Idc error: %s"   %  traceback.format_exc())
        return json.dumps({'code':1, 'errmsg':'Idc create error'})

@jsonrpc.method('idc.get')
@auth_login
def idc_get(auth_info,**kwargs):
    if auth_info['code']==1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','idc_name','name','address','email','interface_user','user_phone','pact_cabinet_num','rel_cabinet_num','remark']
        fields = kwargs.get('output', output)
        where = kwargs.get('where', None)
        result = app.config['cursor'].get_one_result('Idc', fields, where)
        if result:
            util.write_log(username, 'select idc information success')
            return json.dumps({'code':0,'result':result})
        else:
            return json.dumps({'code':1,'errmsg':'must input Idc id'})
    except:
        logging.getLogger().error("select idc error: %s"  % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'select idc error~'})

@jsonrpc.method('idc.getlist')
@auth_login
def idc_getlist(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','idc_name','name','address','email','interface_user','user_phone','pact_cabinet_num','rel_cabinet_num','remark']
        fields = kwargs.get('output', output)
        result = app.config['cursor'].get_results('Idc', fields)
        util.write_log(username,'select idc list success')
        return json.dumps({'code':0, 'result':result, 'count':len(result)})
    except:
        logging.getLogger().error("select idc list error: %s"   %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'select idc list error'})

@jsonrpc.method('idc.update')
@auth_login
def idc_update(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1 ,'errmsg':'you are not admin!'})
    try:
        data = kwargs.get('data',None)
        where = kwargs.get('where', None)
        result = app.config['cursor'].execute_update_sql('Idc', data, where,
            ['idc_name', 'name', 'address', 'email', 'interface_user', 'user_phone',
             'pact_cabinet_num', 'rel_cabinet_num', 'remark'])
        if result == '':
            return json.dumps({'code':1,'errmsg':'you must give an id!'})
        util.write_log(username,'update idc %s success'  % data['name'])
        return json.dumps({'code':0,'result':'update %s success' % data['name']})
    except:
        logging.getLogger().error("update idc error:  %s"  % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'update idc error'})

@jsonrpc.method('idc.delete')
@auth_login
def idc_delete(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':0, 'errmsg':'you are not admin!'})
    try:
        data = request.get_json()['params']
        result = app.config['cursor'].execute_delete_sql('Idc', data)
        if result == '':
            return json.dumps({'code':1,'errmsg':'you need give an id!'})
        util.write_log(username, 'delete idc success')
        return json.dumps({'code':0,'result':'delete success'})
    except:
        logging.getLogger().error('delete idc error : %s'  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'delete idc error'})

