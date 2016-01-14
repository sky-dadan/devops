#!/usr/bin/env python
#coding:utf-8

from flask import Flask,request
from flask_jsonrpc import JSONRPC
from . import app , jsonrpc
import logging, util
import json, traceback
from auth import auth_login

@jsonrpc.method('manufact.create')
@auth_login
def create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = auth_info['role']
    if role != '0':
        return json.dumps({'code':1 ,'errmsg': "You are not admin"})
    try:
        data = request.get_json()['params']
        app.config['cursor'].execute_insert_sql('Manufacturers', data)
        util.write_log(username, 'create manufactures %s success'  % data['name'])
        return json.dumps({'code':0,'result':'create manufactures %s success'  %  data['name']})
    except:
        logging.getLogger().error('create manufactures error: %s'  % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'create manufacturers error'})
        
@jsonrpc.method('manufact.get')
@auth_login
def manufact_get(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','name','supplier_name','interface_user','email','user_phone']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('Manufacturers', fields, where)
        if result:
            util.write_log(username, 'select manufacturers success')
            return json.dumps({'code':0,'result':result})
        else:
            return json.dumps({'code':1,'errmsg':'must give an id!'})
    except:
        logging.getLogger().error("select manufacturers error: %s"  % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'select manufacturers error'})

@jsonrpc.method('manufact.getlist')
@auth_login
def manufact_getlist(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','name','supplier_name','interface_user','email','user_phone']
        fields = kwargs.get('output', output)
        result = app.config['cursor'].get_results('Manufacturers', fields)
        util.write_log(username, 'select manufact list success!')
        return json.dumps({'code':0, 'result':result,'count':len(result)})
    except:
        logging.getLogger().error("select factmanu list error: %s"  % traceback.format_exc())
        return json.dumps({'code':1, 'errmsg':'select factmanu error~!'})

@jsonrpc.method('manufact.update')
@auth_login
def manufact_update(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = auth_info['role']
    if role != '0':
        return json.dumps({'code':1,'errmsg':'you are not admin!'})
    try:
        data = kwargs.get('data',None)
        where = kwargs.get('where',None)
        fields = ['name','supplier_name','interface_user','email','user_phone']
        result = app.config['cursor'].execute_update_sql('Manufacturers', data, where, fields)
        if result == '':
            return json.dumps({'code':1,'errmsg':'must give an id~!'})
        util.write_log(username ,"update manufact %s success!"  %  data['name'])
        return json.dumps({'code':0, 'result':'update %s success'  % data['name']})
    except:
        logging.getLogger().error('update manufact error: %s'  % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'update manufact error'})

@jsonrpc.method('manufact.delete')
@auth_login
def manufact_delete(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = auth_info['role']
    if role != '0':
        return json.dumps({'code':1,'errmsg':'you are not admin!'})
    try:
        data = request.get_json()['params']
        result = app.config['cursor'].execute_delete_sql('Manufacturers', data)
        if result == '':
            return json.dumps({'code':1,'errmsg':'must give an id!'})
        util.write_log(username, 'delete manufacturers success')
        return json.dumps({'code':0,'result':'delete manufact success'})
    except:
        logging.getLogger().error('delete manufact error: %s'  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'delete manufact error~!'})

