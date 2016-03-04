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
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        if not util.check_name(data['name']):
            return json.dumps({'code': 1, 'errmsg': '权限名必须为字母和数字'})
        app.config['cursor'].execute_insert_sql('power', data)
        util.write_log(username, "create power %s success"  %  data['name'])
        return json.dumps({'code':0,'result':'创建权限%s成功' %  data['name']})
    except:
        logging.getLogger().error('create power error:%s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg': '创建权限失败'})

@jsonrpc.method('power.delete')
@auth_login
def delete(auth_info,**kwargs):
    if auth_info['code']==1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        if not data.has_key('id'):
            return json.dumps({'code':1,'errmsg':'需要指定一个权限'})
        record = app.config['cursor'].get_one_result('power', ['name', 'url'], data)
        app.config['cursor'].execute_delete_sql('power', data)
        util.write_log(username, "delete permission %s success"  % record['name'])
        return json.dumps({'code':0,'result':'删除权限%s成功' % record['name']})
    except:
        logging.getLogger().error("delete permission error:%s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg': '删除权限失败'})

@jsonrpc.method('power.getlist')
@auth_login
def getlist(auth_info,**kwargs):
    if auth_info['code']==1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output = ['id','name','name_cn','url','info']
        fields = kwargs.get('output', output)
        result = app.config['cursor'].get_results('power', fields)
        util.write_log(username, 'select power list success')
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error("get list permission error: %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'获取权限列表失败'})

@jsonrpc.method('power.get')
@auth_login
def getbyid(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output = ['id','name','name_cn','url','info']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        if where.has_key('id'):
            result = app.config['cursor'].get_one_result('power', fields, where)
            util.write_log(username,'select power by id successed!')
            return json.dumps({'code':0, 'result':result})
        else:
            return json.dumps({'code':1, 'errmsg':'需要指定一个权限'})
    except:
        logging.getLogger().error("select power by id error: %s" %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'获取权限信息失败'})


@jsonrpc.method('power.update')
@auth_login
def update(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        where = data.get('where',None)
        data = data.get('data',None)
        if not util.check_name(data['name']):
            return json.dumps({'code': 1, 'errmsg': '权限名必须为字母和数字'})
        result=app.config['cursor'].execute_update_sql('power', data, where, ['name', 'name_cn', 'url', 'info'])
        if result == '': 
            return json.dumps({'code':1, 'errmsg':'需要指定一个权限'})
        util.write_log(username,"update %s successed" % data['name'])
        return json.dumps({'code':0,'result':'更新权限信息%s成功' % data['name']})
    except:
        logging.getLogger().error("update error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'更新权限失败'})
