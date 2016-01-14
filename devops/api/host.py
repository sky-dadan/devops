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
	fields, values = [], [] 
	for k,v in data.items():
	    fields.append(k)
	    values.append("'%s'" % v)
	sql = "INSERT INTO Host (%s) VALUES (%s)" % \
		(','.join(fields),','.join(values))
	app.config['cursor'].execute(sql)
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
        output = kwargs.get('output',[])
        if len(output) == 0:
            fields = ['id','hostname','sn','host_no','inner_ip','mac_address','remote_ip','os_info','cpu_num','disk_num','mem_num','host_type',\
            'manufacturer_id','supplier_id','store_date','expire','idc_id','cabinet_id','service_id','status','vm_status','remark']
        else:
            fields=output
        where = kwargs.get('where',None)
        if where.has_key('id'):
            sql = "SELECT %s FROM Host WHERE id = %s" % (','.join(fields),where['id'])
	    app.config['cursor'].execute(sql)
	    row = app.config['cursor'].fetchone()
            result = {}
	    for i,k in enumerate(fields):
		result[k]=row[i]
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
        output=kwargs.get('output',[])
        if len(output) == 0:
            fields = ['id','hostname','sn','host_no','inner_ip','mac_address','remote_ip','os_info','cpu_num','disk_num','mem_num','host_type',\
        'manufacturer_id','supplier_id','store_date','expire','idc_id','cabinet_id','service_id','status','vm_status','remark']
#            fields=['id','hostname','inner_ip','remote_ip','os_info','idc_id','cabinet_id','service_id','status']
        else:
            fields=output
	sql = "select %s from Host" % ','.join(fields)
	app.config['cursor'].execute(sql)
	result = []
        count = 0
        for row in app.config['cursor'].fetchall():
            count += 1
	    res = {}
	    for i,k in enumerate(fields):
               res[k] = row[i]
	    result.append(res)
	util.write_log(username, 'select Host list sucess') 
        return json.dumps({'code':0,'result':result,'count':count},cls=MyEncoder)
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

        data['host_no']=int(data['host_no'])
        data['cpu_num']=int(data['cpu_num'])
        data['mem_num']=int(data['mem_num'])
        data['manufacturer_id']=int(data['manufacturer_id'])
        data['supplier_id']=int(data['supplier_id'])
        data['idc_id']=int(data['idc_id'])
        data['cabinet_id']=int(data['cabinet_id'])
        data['service_id']=int(data['service_id'])
        data['status']=int(data['status'])
        data['vm_status']=int(data['vm_status'])
        where = kwargs.get('where',None)
        if not where.has_key("id"):
            return json.dumps({'code':1,'errmsg':'must need id '})
	sql = 'update Host set hostname="%(hostname)s",sn="%(sn)s",host_no="%(host_no)d", inner_ip="%(inner_ip)s",mac_address="%(mac_address)s",\
                remote_ip="%(remote_ip)s",os_info="%(os_info)s",cpu_num="%(cpu_num)d",disk_num="%(disk_num)s",mem_num="%(mem_num)d",\
                host_type="%(host_type)s",manufacturer_id="%(manufacturer_id)d",supplier_id="%(supplier_id)d",store_date="%(store_date)s",\
                expire="%(expire)s",idc_id="%(idc_id)d",cabinet_id="%(cabinet_id)d",service_id="%(service_id)d",status="%(status)d",\
                vm_status="%(vm_status)d",remark="%(remark)s" WHERE id=%%d' % data % where['id']
	app.config['cursor'].execute(sql)
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
        if not data.has_key("id"):
            return json.dumps({'code':1,'errmsg':'must need id '})
	sql = 'delete from Host where id = %d' % data['id']
	app.config['cursor'].execute(sql)
	util.write_log(username,'delete Host %s sucess' % data['hostname'])
        return json.dumps({'code':0,'result':'delete %s success' % data['hostname']})
    except:
	logging.getLogger().error('delete Host error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'delete Host error'}) 
