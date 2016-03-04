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
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        app.config['cursor'].execute_insert_sql('Idc', data)
        util.write_log(username, "create idc %s success"  %  data['name'])
        return json.dumps({'code':0, 'result': '创建IDC"%s"成功' % data['name']})
    except:
        logging.getLogger().error("create Idc error: %s"   %  traceback.format_exc())
        return json.dumps({'code':1, 'errmsg':'创建IDC失败'})

@jsonrpc.method('idc.get')
@auth_login
def idc_get(auth_info,**kwargs):
    if auth_info['code']==1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output = ['id','idc_name','name','address','email','interface_user','user_phone','pact_cabinet_num','rel_cabinet_num','remark']
        fields = kwargs.get('output', output)
        where = kwargs.get('where', None)
        result = app.config['cursor'].get_one_result('Idc', fields, where)
        if result:
            util.write_log(username, 'select idc information success')
            return json.dumps({'code':0,'result':result})
        else:
            return json.dumps({'code':1,'errmsg':'需要指定一个IDC'})
    except:
        logging.getLogger().error("select idc error: %s"  % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'获取IDC信息失败'})

@jsonrpc.method('idc.getlist')
@auth_login
def idc_getlist(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output = ['id','idc_name','name','address','email','interface_user','user_phone','pact_cabinet_num','rel_cabinet_num','remark']
        fields = kwargs.get('output', output)
        result = app.config['cursor'].get_results('Idc', fields)
        util.write_log(username,'select idc list success')
        return json.dumps({'code':0, 'result':result, 'count':len(result)})
    except:
        logging.getLogger().error("select idc list error: %s"   %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'获取IDC列表失败'})

@jsonrpc.method('idc.update')
@auth_login
def idc_update(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = kwargs.get('data',None)
        where = kwargs.get('where', None)
        result = app.config['cursor'].execute_update_sql('Idc', data, where,
            ['idc_name', 'name', 'address', 'email', 'interface_user', 'user_phone',
             'pact_cabinet_num', 'rel_cabinet_num', 'remark'])
        if result == '':
            return json.dumps({'code':1,'errmsg':'需要指定一个IDC'})
        util.write_log(username,'update idc %s success'  % data['name'])
        return json.dumps({'code':0,'result':'更新IDC"%s"成功' % data['name']})
    except:
        logging.getLogger().error("update idc error:  %s"  % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'更新IDC失败'})

@jsonrpc.method('idc.delete')
@auth_login
def idc_delete(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        result = app.config['cursor'].execute_delete_sql('Idc', data)
        if result == '':
            return json.dumps({'code':1,'errmsg':'需要指定一个IDC'})
        util.write_log(username, 'delete idc success')
        return json.dumps({'code':0,'result':'删除IDC成功'})
    except:
        logging.getLogger().error('delete idc error : %s'  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'删除IDC失败'})

