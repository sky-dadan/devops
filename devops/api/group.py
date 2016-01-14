#!/usr/bin/env python
#coding:utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app , jsonrpc
import logging, util
from auth import auth_login
import json, traceback

#这里是关于用户权限的查看，修改  组的增删改查

@jsonrpc.method('groups.getlist')
@auth_login
def role_select(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        data = request.get_json()['params']
        output = data.get('output',[])
        if len(output) == 0:
            fields = ['id','name','name_cn','p_id','info']
        else:
            fields = output
        perm_name = {}    #{1:'git',2:'web'}
        sql = 'SELECT id,name FROM power'
        app.config['cursor'].execute(sql)
        for row in app.config['cursor'].fetchall():
            perm_name[row[0]] = row[1]
        sql = "select %s from groups " % ','.join(fields)
        app.config['cursor'].execute(sql)
	result = []
        for row in app.config['cursor'].fetchall():
	    res = {}
	    for i,k in enumerate(fields):
		res[k] = row[i]
            p_name=[]
            p_namestr=','
            p_id = res['p_id'].split(',')
            for pid in p_id:
                p_name.append(perm_name[int(pid)])
                res['p_id']=p_namestr.join(p_name)
	    result.append(res)
	util.write_log(username, 'select groups list success')
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error("select groups list error: %s"  %  traceback.format_exc())
	return json.dumps({'code':1,'errmsg':'error : %s' %  traceback.format_exc()})
@jsonrpc.method('groups.get')
@auth_login
def groups_get(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = kwargs.get('output',[])
        where = kwargs.get('where',None)
        if len(output) == 0:
            fields = ['id','name','name_cn','p_id','info']
        else:
            fields = output
        if where.has_key('id'):
            sql = "select %s from groups where id = %s"  %  (','.join(fields), where['id'])
	    app.config['cursor'].execute(sql)
	    row = app.config['cursor'].fetchone()
	    result = {}
            for i, k in enumerate(fields):
                result[k] = row[i]
	    util.write_log(username, "select groups by id success")
	    return json.dumps({'code':0,'result':result})
        else:
            return json.dumps({'code':1, 'errmsg':'must need give an id'})
    except:
        logging.getLogger().error('select groups by id error: %s'  % traceback.format_exc())
        return  json.dumps({'code':1,'errmsg':'select groups error'})

@jsonrpc.method('groups.create')
@auth_login
def role_create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code':1,'errmsg':'you are not admin!'})
    try:
	data = request.get_json()['params']
	print data
	fields, values = [], []
        for k,v in data.items():
            fields.append(k)
	    values.append("'%s'" % v)
	sql = "insert into groups (%s) values (%s)"  % (','.join(fields),','.join(values))
	print sql
	app.config['cursor'].execute(sql)
	util.write_log(username, "create groups %s scucess" %  data['name'])
	return json.dumps({'code':0,'result':'create groups %s successed' % data['name']})
    except:
        logging.getLogger().error(username,"create groups    error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'error:%s' % traceback.format_exc()})

@jsonrpc.method('groups.delete')
@auth_login
def role_delete(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code':1,'errmsg':'you are not admin'})
    try:
        data = request.get_json()['params']
        if not data.has_key('id'):
            return json.dumps({'code':1,'errmsg':'you need give an id!'})
	sql = "delete from groups where id='%s'"  % data['id']
	app.config['cursor'].execute(sql)
	util.write_log(username, 'delete groups successed')
	return json.dumps({'code':0,'result':'delete groups successed'})
    except:
        logging.getLogger().error('delete groups error: %s' %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'error: %s'  % traceback.format_exc()})

@jsonrpc.method('groups.update')
@auth_login
def role_update(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code':1,'errmsg':'you are not admin!'})
    try:
        data = request.get_json()['params']
	where = data.get('where',None)
	data = data.get('data',None)
        if not where.has_key('id'):
            return json.dumps({'code':1, 'errmsg':'you need give an id!'})
        sql = "update groups set name='%(name)s', name_cn='%(name_cn)s',p_id='%(p_id)s', info='%(info)s' where id='%%d'" % data % where['id']	
	app.config['cursor'].execute(sql)
	util.write_log(username, 'update groups %s success!' % data['name'])
	return json.dumps({'code':0,'result':'update groups %s successed' % data['name']})
    except:
        logging.getLogger().error("update error: %s"  % traceback.format_exc())
	return json.dumps({'code':1,'errmsg':"error : %s" % traceback.format_exc()})

