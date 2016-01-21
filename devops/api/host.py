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
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'you not admin '})
    try:
        data = request.get_json()['params']
        app.config['cursor'].execute_insert_sql('Host', data)
        util.write_log(username, "create Host %s sucess" % data['hostname'])
        return json.dumps({'code': 0, 'result': 'Create %s success' % data['hostname']})
    except:
        logging.getLogger().error("Create Host error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'Create Host  error'})

@jsonrpc.method('host.get')     
@auth_login
def get(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','hostname','sn','host_no','inner_ip','mac_address','wan_ip','remote_ip','os_info','cpu_num','disk_num','mem_num',\
                'host_type','manufacturer_id','supplier_id','store_date','expire','idc_id','cabinet_id','service_id','status','vm_status','remark']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('Host', fields, where)
        if result:
            util.write_log(username, 'select Host sucess') 
            return json.dumps({'code':0,'result':result},cls=MyEncoder)
        else:
            return json.dumps({'code':1,'errmsg':'must input Host id'})
    except:
        logging.getLogger().error("select Host error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'select Host  error'})

@jsonrpc.method('host.getlist')     
@auth_login
def getlist(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps({'code': 1, 'errmsg': '%s' % auth_info['errmsg']})
    username = auth_info['username']
    print "kwargs = ",kwargs
    try:
        output = ['id','hostname','sn','host_no','inner_ip','mac_address','wan_ip','remote_ip','os_info','cpu_num','disk_num','mem_num',\
                'host_type','manufacturer_id','supplier_id','store_date','expire','idc_id','cabinet_id','service_id','status','vm_status','remark']
        fields = kwargs.get('output', output)
        result = app.config['cursor'].get_results('Host', fields)
        util.write_log(username, 'select Host list sucess') 
        return json.dumps({'code':0,'result':result,'count':len(result)},cls=MyEncoder)
    except:
        logging.getLogger().error("select Host list error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'select Host list error'})

@jsonrpc.method('host.update')     
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
        #fields_int = ['host_no','cpu_num','disk_num','mem_num','manufacturer_id','supplier_id','idc_id','cabinet_id','service_id','status','vm_status']
        fields = ['hostname','sn','host_no','inner_ip','mac_address','wan_ip','remote_ip','os_info','cpu_num','disk_num','mem_num',\
                 'host_type','manufacturer_id','supplier_id','store_date','expire','idc_id','cabinet_id','service_id','status','vm_status','remark']
        where = kwargs.get('where',None)
        result = app.config['cursor'].execute_update_sql('Host', data, where, fields)
        if result == '':
            return json.dumps({'code':1,'errmsg':'must need id '})
        util.write_log(username,'update Host %s sucess' % data['hostname'])
        return json.dumps({'code':0,'result':'update %s success' % data['hostname']})
    except:
        logging.getLogger().error('update Host error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'update Host error'})

@jsonrpc.method('host.delete')     
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
        result = app.config['cursor'].execute_delete_sql('Host', data)
        if result == '':
            return json.dumps({'code':1,'errmsg':'must need id '})
        util.write_log(username,'delete Host %s sucess' % data['id'])
        return json.dumps({'code':0,'result':'delete %s success' % data['id']})
    except:
        logging.getLogger().error('delete Host error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'delete Host error'})

