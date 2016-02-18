#!/usr/bin/env python
#coding:utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app , jsonrpc
import logging, util
from auth import auth_login
import json, traceback

# 关于权限这一块的增删改查

@jsonrpc.method('power.create')
@auth_login
def create(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        print "you are not admin"
        return json.dumps({'code':1,'errmsg':'you are not admin'})
    try:
        data = request.get_json()['params']
        print data
        app.config['cursor'].execute_insert_sql('power', data)
        util.write_log(username, "create power %s success"  %  data['name'])
        return json.dumps({'code':0,'result':'create %s scucess' %  data['name']})
    except:
        logging.getLogger().error('create power error:%s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg': traceback.format_exc()})

@jsonrpc.method('power.delete')
@auth_login
def delete(auth_info,**kwargs):
    if auth_info['code']==1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        print "you are not admin"
        return json.dumps({'code':1,'errmsg':'you are not admin'})
    try:
        data = request.get_json()['params']
        if not data.has_key('id'):
            return json.dumps({'code':1,'errmsg':'you have give an id'})
        record = app.config['cursor'].get_one_result('power', ['name', 'url'], data)
        app.config['cursor'].execute_delete_sql('power', data)
        util.write_log(username, "delete permission %s success"  % record['name'])
        return json.dumps({'code':0,'result':'delete permisson %s scucess' % record['name']})
    except:
        logging.getLogger().error("delete permission error:%s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg': traceback.format_exc()})

@jsonrpc.method('power.getlist')
@auth_login
def getlist(auth_info,**kwargs):
    if auth_info['code']==1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        print "you are not admin"
        return json.dumps({'code':1,'errmsg':'you are not admin'})
    try:
        output = ['id','name','name_cn','url','info']
        fields = kwargs.get('output', output)
        result = app.config['cursor'].get_results('power', fields)
        util.write_log(username, 'select power list success')
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error("get list permission error: %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'getlist error : %s'  % traceback.format_exc()})

@jsonrpc.method('power.get')
@auth_login
def getbyid(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','name','name_cn','url','info']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        if where.has_key('id'):
            result = app.config['cursor'].get_one_result('power', fields, where)
            util.write_log(username,'select power by id successed!')
            return json.dumps({'code':0, 'result':result})
        else:
            return json.dumps({'code':1, 'errmsg':'you need give an id!'})
    except:
        logging.getLogger().error("select power by id error: %s" %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'select error : %s' % traceback.format_exc()})


@jsonrpc.method('power.update')
@auth_login
def update(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code':1,'errmsg':'you are not admin'})
    try:
        data = request.get_json()['params']
        where = data.get('where',None)
        data = data.get('data',None)
        result=app.config['cursor'].execute_update_sql('power', data, where, ['name', 'name_cn', 'url', 'info'])
        if result == '': 
            return json.dumps({'code':1, 'errmsg':'you need give an id!'})
        util.write_log(username,"update %s successed" % data['name'])
        return json.dumps({'code':0,'result':'update %s successed' % data['name']})
    except:
        logging.getLogger().error("update error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'error: %s' %  traceback.format_exc()})
