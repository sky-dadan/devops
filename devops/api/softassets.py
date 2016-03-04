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
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        app.config['cursor'].execute_insert_sql('Soft_Assets', data)
        util.write_log(username, "create Soft_Assets %s sucess" % data['type'])
        return json.dumps({'code': 0, 'result': '创建软资产%s成功' % data['type']})
    except:
        logging.getLogger().error("Create Soft_Assets error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '创建软资产失败'})

@jsonrpc.method('softassets.get')     
@auth_login
def get(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output =['id','type','manufacturer','store_date','expire','remark']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('Soft_Assets', fields, where)
        if result:
            util.write_log(username, 'select Soft_Assets sucess') 
            return json.dumps({'code':0,'result':result},cls=MyEncoder)
        else:
            return json.dumps({'code':1,'errmsg':'需要指定一个软资产'})
    except:
        logging.getLogger().error("select Soft_Assets error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '获取软资产信息失败'})

@jsonrpc.method('softassets.getlist')     
@auth_login
def getlist(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps({'code': 1, 'errmsg': '%s' % auth_info['errmsg']})
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        fields = ['id','type','manufacturer','store_date','expire','remark']
        data = request.get_json()
        data = data['params']
        result = app.config['cursor'].get_results('Soft_Assets', fields)
        util.write_log(username, 'select Soft_Assets list sucess') 
        return json.dumps({'code':0,'result':result,'count':len(result)},cls=MyEncoder)
    except:
        logging.getLogger().error("select Soft_Assets list error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '获取软资产列表失败'})

@jsonrpc.method('softassets.update')
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
        result = app.config['cursor'].execute_update_sql('Soft_Assets', data, where,
                    ['type','manufacturer','store_date','expire','remark'])
        if result == '':
            return json.dumps({'code':1,'errmsg':'需要指定一个软资产'})
        util.write_log(username,'update Soft_Assets %s sucess' % data['type'])
        return json.dumps({'code':0,'result':'更新软资产%s成功' % data['type']})
    except:
        logging.getLogger().error('update Soft_Assets error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'更新软资产失败'})

@jsonrpc.method('softassets.delete')     
@auth_login
def delete(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        result = app.config['cursor'].execute_delete_sql('Soft_Assets', data)
        if result == '':
            return json.dumps({'code':1,'errmsg':'需要指定一个软资产'})
        util.write_log(username,'delete Soft_Assets %s sucess' % data['id'])
        return json.dumps({'code':0,'result':'删除软资产成功'})
    except:
        logging.getLogger().error('delete Soft_Assets error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'删除软资产失败'})

