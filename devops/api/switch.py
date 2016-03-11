#!/usr/bin/env python
#coding:utf-8
from flask import Flask,request
from . import jsonrpc
from . import app
import time,logging,util
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
        app.config['cursor'].execute_insert_sql('switch', data)
        util.write_log(username, "create switch %s sucess" % data['name'])
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
        output = ['id','name','ip','type','manufacturer_id','supplier_id','idc_id','cabinet_id','port_num','status','store_date','expire','remark']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('switch', fields, where)
        if result:
            util.write_log(username, 'select switch sucess') 
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
        fields =['id','name','ip','type','manufacturer_id','supplier_id','idc_id','cabinet_id','port_num','status','store_date','expire','remark']
        result = app.config['cursor'].get_results('switch', fields)
        now = int(time.time())
        warning_date = int(app.config.get('asset_warning_day', 0))
        for asset in result:
            if 'expire' in asset and asset['expire']:
                expire = int(time.mktime(asset['expire'].timetuple()))
                remain_date = (expire-now)/(24*60*60)
                asset['warning'] = 2 if remain_date <= 0 else 1 if warning_date > 0 and warning_date > remain_date else 0
        util.write_log(username, 'select switch list sucess') 
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
        fields = ['name', 'ip', 'type','manufacturer_id','supplier_id','idc_id', 'cabinet_id', 'port_num', 'status', 'store_date', 'expire', 'remark']
        result = app.config['cursor'].execute_update_sql('switch', data, where, fields)
        if result == '':
            return json.dumps({'code':1,'errmsg':'需要指定一个网络设备'})
        util.write_log(username,'update switch %s sucess' % data['name'])
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
        result = app.config['cursor'].execute_delete_sql('switch', data)
        if result == '':
            return json.dumps({'code':1,'errmsg':'需要指定一个网络设备'})
        util.write_log(username,'delete switch %s sucess' % data['id'])
        return json.dumps({'code':0,'result':'删除网络设备成功'})
    except:
        logging.getLogger().error('delete Switch error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'删除网络设备失败'})
