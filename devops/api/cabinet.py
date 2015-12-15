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
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'you not admin '})
    try:
	data = request.get_json()['params']
	fields, values = [], [] 
	for k,v in data.items():
	    fields.append(k)
	    values.append("'%s'" % v)
	sql = "insert into Cabinet (%s) values (%s)" % \
		(','.join(fields),','.join(values))
	app.config['cursor'].execute(sql)
	util.write_log(username, "create Cabinet %s sucess" % data['name'])
	return json.dumps({'code': 0, 'result': 'Create %s success' % data['name']})
    except:
	logging.getLogger().error("Create Cabinet error: %s" % traceback.format_exc())
	return json.dumps({'code': 1, 'errmsg': 'Create Cabinet  error'})


@jsonrpc.method('cabinet.get')     
@auth_login
def get(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = kwargs.get('output',[])
        where = kwargs.get('where',None)
        if len(output) == 0:
            fields = ['id','name','idc_id','u_num','power']
        else:
            fields = output
        if where.has_key("id"):
	    sql = "select %s from Cabinet where id = %d" % (','.join(fields),where["id"])
	    app.config['cursor'].execute(sql)
	    row = app.config['cursor'].fetchone()
            result = {}
	    for i,k in enumerate(fields):
		result[k]=row[i]
	    util.write_log(username, 'select Cabinet sucess') 
            return json.dumps({'code':0,'result':result})
	else:
	    return json.dumps({'code':1,'errmsg':'must input Cabinet id'})
    except:
	logging.getLogger().error("select  Cabinet error: %s" % traceback.format_exc())
	return json.dumps({'code': 1, 'errmsg': 'select Cabinet  error'})

@jsonrpc.method('cabinet.getlist')     
@auth_login
def getlist(auth_info,**kwargs):
    if auth_info['code'] == 1:   
	return json.dumps({'code': 1, 'errmsg': '%s' % auth_info['errmsg']})
    username = auth_info['username']
    try:
        output = kwargs.get('output',[])
        if len(output) == 0:
            fields = ['id','name','idc_id','u_num','power']
        else:
            fields = output
	sql = "select %s  from Cabinet" % ','.join(fields)
	app.config['cursor'].execute(sql)
	result = []
        count = 0
        for row in app.config['cursor'].fetchall():
            count += 1
	    res = {}
	    for i,k in enumerate(fields):
               res[k] = row[i]
	    result.append(res)
	util.write_log(username, 'select Cabinet list sucess') 
        return json.dumps({'code':0,'result':result,'count':count})
    except:
	logging.getLogger().error("select  Cabinet list error: %s" % traceback.format_exc())
	return json.dumps({'code': 1, 'errmsg': 'select  Cabinet list error'})



@jsonrpc.method('cabinet.update')     
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
        if not where.has_key("id"):
            return json.dumps({'code':1,'errmsg':'must need id '})
	sql = 'update Cabinet set name="%(name)s",idc_id="%(idc_id)d",u_num="%(u_num)d", \
		power="%(power)s" where id=%%d'  % data % where['id']
        print sql
	app.config['cursor'].execute(sql)
	util.write_log(username,'update cabinet %s sucess' % data['name'])
	return json.dumps({'code':0,'result':'update %s success' % data['name']})
    except:
	logging.getLogger().error('update cabinet error : %s' % traceback.format_exc())
	return json.dumps({'code':1,'errmsg':'update cabinet error'})

@jsonrpc.method('cabinet.delete')     
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
	sql = 'delete from Cabinet where id = %d' % data['id']
        print sql        
	app.config['cursor'].execute(sql)
	util.write_log(username,'delete cabinet %s sucess' % data['name'])
        return json.dumps({'code':0,'result':'delete %s success' % data['name']})
    except:
	logging.getLogger().error('delete cabinet error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'delete cabinet error'})

