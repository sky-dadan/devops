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
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'you are not admin!'})
    try:
        data = request.get_json()['params']
        app.config['cursor'].execute_insert_sql('Services', data)
        util.write_log(username, "create Services %s success"  % data['name'])
        return json.dumps({'code':0,'result':'create Services %s success'  % data['name']})
    except:
        logging.getLogger().error("create services error: %s"  % traceback.format_exc())
        return json.dumps({'code':1, 'errmsg':'create services error %s' % traceback.format_exc()})

@jsonrpc.method('services.get')
@auth_login
def get(auth_info, **kwargs):
    if auth_info['code']== 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','name','dev_interface','sa_interface','remark']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('Services', fields, where)
        if result:
            util.write_log(username,'select services success')
            return json.dumps({'code':0,'result':result})
        else:
            return json.dumps({'code':'1','errmsg':'must give services id'})
    except:
        logging.getLogger().error('select services error: %s'  % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'select services error'})

@jsonrpc.method('services.getlist')
@auth_login
def getlist(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','name','dev_interface','sa_interface','remark']
        fields = kwargs.get('output', output)
        result = app.config['cursor'].get_results('Services', fields)
        util.write_log(username, 'select services list success')
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error("select services error: %s " % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'select services error'})

@jsonrpc.method('services.update')
@auth_login
def update(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = auth_info['role']
    if role != '0':
        return json.dumps({'code':1,'errmsg':'you are not admin!'})
    try:
        data = kwargs.get('data',None)
        where = kwargs.get('where', None)
        result = app.config['cursor'].execute_update_sql('Services', data, where,
                ['name', 'dev_interface', 'sa_interface', 'remark'])
        if result == '':
            return json.dumps({'code':1,'errmsg':'must give an id!'})
        util.write_log(username, 'update services %s success'  % data['name'])
        return json.dumps({'code':0,'result':'update services %s successed'  %  data['name']})
    except:
        logging.getLogger().error('update services error: %s'  % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'update services error'})

@jsonrpc.method('services.delete')
@auth_login
def delete(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'you are not admin!'})
    try:
        data = request.get_json()['params']
        result = app.config['cursor'].execute_delete_sql('Services', data)
        if result == '':
            return json.dumps({'code':1,'errmsg':'need give an id!'})
        util.write_log(username , 'delete services success' )
        return json.dumps({'code':0,'result':'delete success'} )
    except:
        logging.getLogger().error('delete services error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'delete services error'})

