#!/usr/bin/env python
#coding:utf-8
from flask import Flask,request
from . import jsonrpc
from . import app
import logging,util
from auth import auth_login
import json,traceback
from jsondate import MyEncoder

@jsonrpc.method('switch.create')     
@auth_login
def create(auth_info,**kwargs):
    if auth_info['code'] == 1:   #主要用于判断认证是否过期，过期会会在web提示
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        app.config['cursor'].execute_insert_sql('Switch', data)
        util.write_log(username, "create Switch %s sucess" % data['name'])
        return json.dumps({'code': 0, 'result': '创建网络设备%s成功' % data['name']})
    except:
        logging.getLogger().error("Create Switch error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '创建网络设备失败'})

@jsonrpc.method('switch.get')
@auth_login
def get(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output = ['id','name','ip','type','manufacturer_id','supplier_id','idc_id','cabinet_id','port_num','status','remark']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('Switch', fields, where)
        if result:
            util.write_log(username, 'select Switch sucess') 
            return json.dumps({'code':0,'result':result},cls=MyEncoder)
        else:
            return json.dumps({'code':1,'errmsg':'需要指定一个网络设备'})
    except:
        logging.getLogger().error("select Switch error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '获取网络设备信息失败'})

@jsonrpc.method('switch.getlist')     
@auth_login
def getlist(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps({'code': 1, 'errmsg': '%s' % auth_info['errmsg']})
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        fields =['id','name','ip','type','manufacturer_id','supplier_id','idc_id','cabinet_id','port_num','status','remark']
        result = app.config['cursor'].get_results('Switch', fields)
        util.write_log(username, 'select Switch list sucess') 
        return json.dumps({'code':0,'result':result,'count':len(result)},cls=MyEncoder)
    except:
        logging.getLogger().error("select Switch list error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '获取网络设备列表失败'})

@jsonrpc.method('switch.update')     
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
        fields = ['name', 'ip', 'type','manufacturer_id','supplier_id','idc_id', 'cabinet_id', 'port_num', 'status', 'remark']
        result = app.config['cursor'].execute_update_sql('Switch', data, where, fields)
        if result == '':
            return json.dumps({'code':1,'errmsg':'需要指定一个网络设备'})
        util.write_log(username,'update Switch %s sucess' % data['name'])
        return json.dumps({'code':0,'result':'更新网络设备%s成功' % data['name']})
    except:
        logging.getLogger().error('update Switch error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'更新网络设备失败'})

@jsonrpc.method('switch.delete')     
@auth_login
def delete(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        result = app.config['cursor'].execute_delete_sql('Switch', data)
        if result == '':
            return json.dumps({'code':1,'errmsg':'需要指定一个网络设备'})
        util.write_log(username,'delete Switch %s sucess' % data['id'])
        return json.dumps({'code':0,'result':'删除网络设备成功'})
    except:
        logging.getLogger().error('delete Switch error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'删除网络设备失败'})
