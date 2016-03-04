#!/usr/bin/env python
#coding:utf-8
from flask import Flask,request
from . import jsonrpc
from . import app
import logging,util
from auth import auth_login
import json,traceback

@jsonrpc.method('cabinet.create')     
@auth_login
def create(auth_info,**kwargs):
    if auth_info['code'] == 1:   #主要用于判断认证是否过期，过期会会在web提示
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        app.config['cursor'].execute_insert_sql('Cabinet', data)
        util.write_log(username, "create Cabinet %s sucess" % data['name'])
        return json.dumps({'code': 0, 'result': '创建机柜%s成功' % data['name']})
    except:
        logging.getLogger().error("Create Cabinet error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '创建机柜失败'})


@jsonrpc.method('cabinet.get')     
@auth_login
def get(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output = ['id','name','idc_id','u_num','power']
        fields = kwargs.get('output', output)
        where = kwargs.get('where', {})
        result = app.config['cursor'].get_one_result('Cabinet', fields, where)
        if result:
            util.write_log(username, 'select Cabinet sucess') 
            return json.dumps({'code':0,'result':result})
        else:
            return json.dumps({'code':1,'errmsg':'需要指定一个机柜'})
    except:
        logging.getLogger().error("select Cabinet error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '获取机柜信息失败'})

@jsonrpc.method('cabinet.getlist')     
@auth_login
def getlist(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output = ['id','name','idc_id','u_num','power']
        fields = kwargs.get('output', output)
        result = app.config['cursor'].get_results('Cabinet', fields)
        util.write_log(username, 'select Cabinet list sucess') 
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error("select  Cabinet list error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '获取机柜列表失败'})

@jsonrpc.method('cabinet.update')
@auth_login
def update(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = kwargs.get('data',None)
        where = kwargs.get('where',None)
        result = app.config['cursor'].execute_update_sql('Cabinet', data, where, ['name', 'idc_id', 'u_num', 'power'])
        if result == '':
            return json.dumps({'code':1,'errmsg':'需要指定一个机柜'})
        util.write_log(username,'update cabinet %s sucess' % data['name'])
        return json.dumps({'code':0,'result':'更新机柜%s成功' % data['name']})
    except:
        logging.getLogger().error('update cabinet error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'更新机柜失败'})

@jsonrpc.method('cabinet.delete')     
@auth_login
def delete(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        result = app.config['cursor'].execute_delete_sql('Cabinet', data)
        if result == '':
            return json.dumps({'code':1,'errmsg':'需要指定一个机柜'})
        util.write_log(username,'delete cabinet sucess')
        return json.dumps({'code':0,'result':'删除机柜成功'})
    except:
        logging.getLogger().error('delete cabinet error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'删除机柜失败'})

