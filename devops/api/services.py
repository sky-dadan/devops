#!/usr/bin/env python
#coding: utf-8
from flask  import Flask, request
from flask_jsonrpc import JSONRPC
from .import app , jsonrpc
import logging, util
from auth import auth_login
import json, traceback

@jsonrpc.method('services.create')
@auth_login
def create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        app.config['cursor'].execute_insert_sql('service', data)
        util.write_log(username, "create Services %s success"  % data['name'])
        return json.dumps({'code':0,'result':'创建服务%s成功'  % data['name']})
    except:
        logging.getLogger().error("create services error: %s"  % traceback.format_exc())
        return json.dumps({'code':1, 'errmsg':'创建服务失败'})

@jsonrpc.method('services.get')
@auth_login
def get(auth_info, **kwargs):
    if auth_info['code']== 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output = ['id','name','dev_interface','sa_interface','remark']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('service', fields, where)
        if result:
            util.write_log(username,'select services success')
            return json.dumps({'code':0,'result':result})
        else:
            return json.dumps({'code':'1','errmsg':'需要指定一个服务'})
    except:
        logging.getLogger().error('select services error: %s'  % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'获取服务信息失败'})

@jsonrpc.method('services.getlist')
@auth_login
def getlist(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output = ['id','name','dev_interface','sa_interface','remark']
        fields = kwargs.get('output', output)
        result = app.config['cursor'].get_results('service', fields)
        util.write_log(username, 'select services list success')
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error("select services error: %s " % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'获取服务列表失败'})

@jsonrpc.method('services.update')
@auth_login
def update(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = kwargs.get('data',None)
        where = kwargs.get('where', None)
        result = app.config['cursor'].execute_update_sql('service', data, where,
                ['name', 'dev_interface', 'sa_interface', 'remark'])
        if result == '':
            return json.dumps({'code':1,'errmsg':'需要指定一个服务'})
        util.write_log(username, 'update services %s success'  % data['name'])
        return json.dumps({'code':0,'result':'更新服务%s成功'  %  data['name']})
    except:
        logging.getLogger().error('update services error: %s'  % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'更新服务失败'})

@jsonrpc.method('services.delete')
@auth_login
def delete(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        result = app.config['cursor'].execute_delete_sql('service', data)
        if result == '':
            return json.dumps({'code':1,'errmsg':'需要指定一个服务'})
        util.write_log(username , 'delete services success' )
        return json.dumps({'code':0,'result':'删除服务成功'} )
    except:
        logging.getLogger().error('delete services error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'删除服务失败'})

