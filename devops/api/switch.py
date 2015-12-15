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
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'you not admin '})
    try:
	data = request.get_json()['params']
	fields, values = [], [] 
	for k,v in data.items():
	    fields.append(k)
	    values.append("'%s'" % v)
	sql = "INSERT INTO Switch (%s) VALUES (%s)" % \
		(','.join(fields),','.join(values))
	app.config['cursor'].execute(sql)
	util.write_log(username, "create Switch %s sucess" % data['name'])
	return json.dumps({'code': 0, 'result': 'Create Switch %s success' % data['name']})
    except:
	logging.getLogger().error("Create Switch error: %s" % traceback.format_exc())
	return json.dumps({'code': 1, 'errmsg': 'Create Switch error'})

@jsonrpc.method('switch.get')     
@auth_login
def get(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = kwargs.get('output',[])
        if len(output) == 0:
            fields =['id','name','type','idc_id','cabinet_id','port_num','status','remark']
        else:
            fields=output
        where = kwargs.get('where',None)
        if where.has_key('id'):
            sql = "SELECT %s FROM Switch WHERE id = %d" % (','.join(fields),where['id'])
	    app.config['cursor'].execute(sql)
	    row = app.config['cursor'].fetchone()
            result = {}
	    for i,k in enumerate(fields):
		result[k]=row[i]
	    util.write_log(username, 'select Switch sucess') 
            return json.dumps({'code':0,'result':result},cls=MyEncoder)
	else:
	    return json.dumps({'code':1,'errmsg':'must input Switch id'})
    except:
	logging.getLogger().error("select Switch error: %s" % traceback.format_exc())
	return json.dumps({'code': 1, 'errmsg': 'select Switch error'})

@jsonrpc.method('switch.getlist')     
@auth_login
def getlist(auth_info,**kwargs):
    if auth_info['code'] == 1:   
	return json.dumps({'code': 1, 'errmsg': '%s' % auth_info['errmsg']})
    username = auth_info['username']
    try:
        fields =['id','name','type','idc_id','cabinet_id','port_num','status','remark']
	data = request.get_json()	
	data = data['params']
	sql = "select * from Switch" 
	app.config['cursor'].execute(sql)
	result = []
        count = 0
        for row in app.config['cursor'].fetchall():
            count += 1
	    res = {}
	    for i,k in enumerate(fields):
               res[k] = row[i]
	    result.append(res)
	util.write_log(username, 'select Switch list sucess') 
        return json.dumps({'code':0,'result':result,'count':count},cls=MyEncoder)
    except:
	logging.getLogger().error("select Switch list error: %s" % traceback.format_exc())
	return json.dumps({'code': 1, 'errmsg': 'select Switch list error'})



@jsonrpc.method('switch.update')     
@auth_login
def update(auth_info,**kwargs):
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
	sql = 'UPDATE Switch SET name="%(name)s",type="%(type)s",idc_id="%(idc_id)d",cabinet_id="%(cabinet_id)d",\
                port_num="%(port_num)d",status="%(status)d",remark="%(remark)s" WHERE id=%(id)d'  % data
        print sql
	app.config['cursor'].execute(sql)
	util.write_log(username,'update Switch %s sucess' % data['name'])
	return json.dumps({'code':0,'result':'update Switch %s success' % data['name']})
    except:
	logging.getLogger().error('update Switch error : %s' % traceback.format_exc())
	return json.dumps({'code':1,'errmsg':'update Switch error'})

@jsonrpc.method('switch.delete')     
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
	sql = 'DELETE FROM Switch WHERE id = %d' % data['id']
	app.config['cursor'].execute(sql)
	util.write_log(username,'delete Switch %s sucess' % data['name'])
        return json.dumps({'code':0,'result':'delete %s success' % data['name']})
    except:
	logging.getLogger().error('delete Switch error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'delete Switch error'})
