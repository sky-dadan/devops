#!/usr/bin/env python
#coding:utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app , jsonrpc
import logging, util
from auth import auth_login
import json, traceback
from user_perm import getid_list

#这里是关于用户权限的查看，修改  组的增删改查
@jsonrpc.method('groups.create')
@auth_login
def role_create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        if not data.has_key('p_id'):
            return json.dumps({'code':1,'errmsg':'必须选择一个权限!'})
        if not util.check_name(data['name']):
            return json.dumps({'code': 1, 'errmsg': '组名必须为字母和数字!'})
        app.config['cursor'].execute_insert_sql('user_group', data)
        util.write_log(username, "create group %s scucess" %  data['name'])
        return json.dumps({'code':0,'result':'创建组%s成功' % data['name']})
    except:
        logging.getLogger().error(username,"create groups error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'创建组失败'})

@jsonrpc.method('groups.getlist')
@auth_login
def role_select(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output = ['id','name','name_cn','p_id','comment']
        data = request.get_json()['params']
        fields = data.get('output', output)

        result = app.config['cursor'].get_results('permission', ['id', 'name'])
        perm_name = dict([(x['id'], x['name']) for x in result])

        result = []
        res = app.config['cursor'].get_results('user_group', fields)
        for x in res:
            p_name = [perm_name[int(p_id)] for p_id in x['p_id'].split(',')]
            x['p_id'] = ','.join(p_name)
            result.append(x)

        util.write_log(username, 'select group list success')
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error("select groups list error: %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'获取组列表失败'})

@jsonrpc.method('groups.get')
@auth_login
def groups_get(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output = ['id','name','name_cn','p_id','comment']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('user_group', fields, where)
        if result is None:
            return json.dumps({'code':1, 'errmsg':'需要指定一个组'})
        else:
            util.write_log(username, "select group by id success")
            return json.dumps({'code':0,'result':result})
    except:
        logging.getLogger().error('select groups by id error: %s'  % traceback.format_exc())
        return  json.dumps({'code':1,'errmsg':'获取组信息失败'})

@jsonrpc.method('groups.update')
@auth_login
def role_update(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        where = data.get('where',None)
        data = data.get('data',None)
        if not util.check_name(data['name']):
            return json.dumps({'code': 1, 'errmsg': '组名必须为字母和数字!'})
        result = app.config['cursor'].execute_update_sql('user_group', data, where, ['name', 'name_cn', 'p_id', 'comment'])
        if result == '':
            return json.dumps({'code':1, 'errmsg':'需要指定一个组'})
        util.write_log(username, 'update group %s success!' % data['name'])
        return json.dumps({'code':0,'result':'更新组%s成功' % data['name']})
    except:
        logging.getLogger().error("update error: %s"  % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':"更新组失败"})

@jsonrpc.method('groups.delete')
@auth_login
def role_delete(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = request.get_json()['params']
        result = app.config['cursor'].execute_delete_sql('user_group', data)
        if result == '':
            return json.dumps({'code':1, 'errmsg':'需要指定一个组'})
        util.write_log(username, 'delete group successed')
        return json.dumps({'code':0,'result':'删除组成功'})
    except:
        logging.getLogger().error('delete groups error: %s' %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'删除组失败'})

