#!/usr/bin/env python
#coding:utf-8

from flask import Flask,request
from . import jsonrpc
from . import app
import logging,util
from auth import auth_login
import json,traceback
from jsondate import MyEncoder

@jsonrpc.method('host.create')     
@auth_login
def create(auth_info,**kwargs):
    if auth_info['code'] == 1:   #主要用于判断认证是否过期，过期会会在web提示
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        if not util.check_name(data['hostname']):
            return json.dumps({'code': 1, 'errmsg': "用户名必须为字母和数字"})
        app.config['cursor'].execute_insert_sql('host', data)
        util.write_log(username, "create host %s sucess" % data['hostname'])
        return json.dumps({'code': 0, 'result': '创建主机%s成功' % data['hostname']})
    except:
        logging.getLogger().error("Create Host error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '创建主机失败'})

@jsonrpc.method('host.get')
@auth_login
def get(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output = ['id','hostname','sn','host_no','inner_ip','mac_address','wan_ip','remote_ip','os_info','cpu_num','disk_num','mem_num',\
                'host_type','manufacturer_id','supplier_id','store_date','expire','idc_id','cabinet_id','service_id','status','vm_status','remark']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('host', fields, where)
        if result:
            util.write_log(username, 'select host sucess') 
            return json.dumps({'code':0,'result':result},cls=MyEncoder)
        else:
            return json.dumps({'code':1,'errmsg':'需要指定一个主机'})
    except:
        logging.getLogger().error("select Host error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '获取主机信息失败'})

@jsonrpc.method('host.getlist')
@auth_login
def getlist(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output = ['id','hostname','sn','host_no','inner_ip','mac_address','wan_ip','remote_ip','os_info','cpu_num','disk_num','mem_num',\
                'host_type','manufacturer_id','supplier_id','store_date','expire','idc_id','cabinet_id','service_id','status','vm_status','remark']
        fields = kwargs.get('output', output)
        result = app.config['cursor'].get_results('host', fields)
        util.write_log(username, 'select host list sucess') 
        return json.dumps({'code':0,'result':result,'count':len(result)},cls=MyEncoder)
    except:
        logging.getLogger().error("select Host list error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '获取主机列表失败'})

@jsonrpc.method('host.update')     
@auth_login
def update(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = kwargs.get('data',None)
        if not util.check_name(data['hostname']):
            return json.dumps({'code': 1, 'errmsg': "用户名必须为字母和数字"})
        fields = ['hostname','sn','host_no','inner_ip','mac_address','wan_ip','remote_ip','os_info','cpu_num','disk_num','mem_num',\
                 'host_type','manufacturer_id','supplier_id','store_date','expire','idc_id','cabinet_id','service_id','status','vm_status','remark']
        where = kwargs.get('where',None)
        result = app.config['cursor'].execute_update_sql('host', data, where, fields)
        if result == '':
            return json.dumps({'code':1,'errmsg':'需要指定一个主机'})
        util.write_log(username,'update host %s sucess' % data['hostname'])
        return json.dumps({'code':0,'result':'更新主机信息%s成功' % data['hostname']})
    except:
        logging.getLogger().error('update Host error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'更新主机失败'})

@jsonrpc.method('host.delete')
@auth_login
def delete(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        result = app.config['cursor'].execute_delete_sql('host', data)
        if result == '':
            return json.dumps({'code':1,'errmsg':'需要指定一个主机'})
        util.write_log(username,'delete host %s sucess' % data['id'])
        return json.dumps({'code':0,'result':'删除主机成功'})
    except:
        logging.getLogger().error('delete Host error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'删除主机失败'})

