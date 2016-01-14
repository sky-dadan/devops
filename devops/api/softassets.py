#!/usr/bin/env python
#coding:utf-8
from flask import Flask,request
from . import jsonrpc
from . import app
import logging,util
from auth import auth_login
import json,traceback
from jsondate import MyEncoder

@jsonrpc.method('softassets.create')     
@auth_login
def create(auth_info,**kwargs):
    if auth_info['code'] == 1:   #主要用于判断认证是否过期，过期会会在web提示
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'you not admin '})
    try:
        data = request.get_json()['params']
        app.config['cursor'].execute_insert_sql('Soft_Assets', data)
        util.write_log(username, "create Soft_Assets %s sucess" % data['type'])
        return json.dumps({'code': 0, 'result': 'Create Soft_Assets %s success' % data['type']})
    except:
        logging.getLogger().error("Create Soft_Assets error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'Create Soft_Assets error'})

@jsonrpc.method('softassets.get')     
@auth_login
def get(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output =['id','type','manufacturer','store_date','expire','remark']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('Soft_Assets', fields, where)
        if result:
            util.write_log(username, 'select Soft_Assets sucess') 
            return json.dumps({'code':0,'result':result},cls=MyEncoder)
        else:
            return json.dumps({'code':1,'errmsg':'must input Soft_Assets id'})
    except:
        logging.getLogger().error("select Soft_Assets error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'select Soft_Assets error'})

@jsonrpc.method('softassets.getlist')     
@auth_login
def getlist(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps({'code': 1, 'errmsg': '%s' % auth_info['errmsg']})
    username = auth_info['username']
    try:
        fields = ['id','type','manufacturer','store_date','expire','remark']
        data = request.get_json()
        data = data['params']
        result = app.config['cursor'].get_results('Soft_Assets', fields)
        util.write_log(username, 'select Soft_Assets list sucess') 
        return json.dumps({'code':0,'result':result,'count':len(result)},cls=MyEncoder)
    except:
        logging.getLogger().error("select Soft_Assets list error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'select Soft_Assets list error'})

@jsonrpc.method('softassets.update')
@auth_login
def update(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'you not admin '})
    try:
        data = kwargs.get('data',None)
        where = kwargs.get('where',None)
        result = app.config['cursor'].execute_update_sql('Soft_Assets', data, where,
                    ['type','manufacturer','store_date','expire','remark'])
        if result == '':
            return json.dumps({'code':1,'errmsg':'must need id1'})
        util.write_log(username,'update Soft_Assets %s sucess' % data['type'])
        return json.dumps({'code':0,'result':'update Soft_Assets %s success' % data['type']})
    except:
        logging.getLogger().error('update Soft_Assets error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'update Soft_Assets error'})

@jsonrpc.method('softassets.delete')     
@auth_login
def delete(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'you not admin '})
    try:
        data = request.get_json()['params']
        result = app.config['cursor'].execute_delete_sql('Soft_Assets', data)
        if result == '':
            return json.dumps({'code':1,'errmsg':'must need id '})
        util.write_log(username,'delete Soft_Assets %s sucess' % data['id'])
        return json.dumps({'code':0,'result':'delete %s success' % data['id']})
    except:
        logging.getLogger().error('delete Soft_Assets error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'delete Soft_Assets error'})

