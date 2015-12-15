#!/usr/bin/env python
#coding:utf-8
from flask import Flask,request
from . import jsonrpc
from . import app
import logging,util
from auth import auth_login
import json,traceback
from jsondate import MyEncoder
@jsonrpc.method('softassets.create')     
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
	sql = "INSERT INTO Soft_Assets (%s) VALUES (%s)" % \
		(','.join(fields),','.join(values))
	app.config['cursor'].execute(sql)
	util.write_log(username, "create Soft_Assets %s sucess" % data['type'])
	return json.dumps({'code': 0, 'result': 'Create Soft_Assets %s success' % data['type']})
    except:
	logging.getLogger().error("Create Soft_Assets error: %s" % traceback.format_exc())
	return json.dumps({'code': 1, 'errmsg': 'Create Soft_Assets error'})

@jsonrpc.method('softassets.get')     
@auth_login
def get(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = kwargs.get('output',[])
        if len(output) == 0:
            fields =['id','type','manufacturer','store_date','expire','remark']
        else:
            fields=output
        where = kwargs.get('where',None)
        if where.has_key('id'):
            sql = "SELECT %s FROM Soft_Assets WHERE id = %d" % (','.join(fields),where['id'])
	    app.config['cursor'].execute(sql)
	    row = app.config['cursor'].fetchone()
            result = {}
	    for i,k in enumerate(fields):
		result[k]=row[i]
	    util.write_log(username, 'select Soft_Assets sucess') 
            return json.dumps({'code':0,'result':result},cls=MyEncoder)
	else:
	    return json.dumps({'code':1,'errmsg':'must input Soft_Assets id'})
    except:
	logging.getLogger().error("select Soft_Assets error: %s" % traceback.format_exc())
	return json.dumps({'code': 1, 'errmsg': 'select Soft_Assets error'})

@jsonrpc.method('softassets.getlist')     
@auth_login
def getlist(auth_info,**kwargs):
    if auth_info['code'] == 1:   
	return json.dumps({'code': 1, 'errmsg': '%s' % auth_info['errmsg']})
    username = auth_info['username']
    try:
        fields = ['id','type','manufacturer','store_date','expire','remark']
	data = request.get_json()	
	data = data['params']
	sql = "select * from Soft_Assets" 
	app.config['cursor'].execute(sql)
	result = []
        count = 0
        for row in app.config['cursor'].fetchall():
            count += 1
	    res = {}
	    for i,k in enumerate(fields):
               res[k] = row[i]
	    result.append(res)
	util.write_log(username, 'select Soft_Assets list sucess') 
        return json.dumps({'code':0,'result':result,'count':count},cls=MyEncoder)
    except:
	logging.getLogger().error("select Soft_Assets list error: %s" % traceback.format_exc())
	return json.dumps({'code': 1, 'errmsg': 'select Soft_Assets list error'})



@jsonrpc.method('softassets.update')     
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
	sql = 'UPDATE Soft_Assets SET type="%(type)s",manufacturer="%(manufacturer)s",store_date="%(store_date)s",\
                expire="%(expire)s",remark="%(remark)s" WHERE id=%(id)d'  % data
        print sql
	app.config['cursor'].execute(sql)
	util.write_log(username,'update Soft_Assets %s sucess' % data['type'])
	return json.dumps({'code':0,'result':'update Soft_Assets %s success' % data['type']})
    except:
	logging.getLogger().error('update Soft_Assets error : %s' % traceback.format_exc())
	return json.dumps({'code':1,'errmsg':'update Soft_Assets error'})

@jsonrpc.method('softassets.delete')     
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
	sql = 'DELETE FROM Soft_Assets WHERE id = %d' % data['id']
	app.config['cursor'].execute(sql)
	util.write_log(username,'delete Soft_Assets %s sucess' % data['type'])
        return json.dumps({'code':0,'result':'delete %s success' % data['type']})
    except:
	logging.getLogger().error('delete Soft_Assets error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'delete Soft_Assets error'})

