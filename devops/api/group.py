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
        app.config['cursor'].execute_insert_sql('groups', data)
	util.write_log(username, "create groups %s scucess" %  data['name'])
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
        output = ['id','name','name_cn','p_id','info']
        data = request.get_json()['params']
        fields = data.get('output', output)

        result = app.config['cursor'].get_results('power', ['id', 'name'])
        perm_name = dict([(x['id'], x['name']) for x in result])

        result = []
        res = app.config['cursor'].get_results('groups', fields)
        for x in res:
            p_name = [perm_name[int(p_id)] for p_id in x['p_id'].split(',')]
            x['p_id'] = ','.join(p_name)
            result.append(x)

	util.write_log(username, 'select groups list success')
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
        output = ['id','name','name_cn','p_id','info']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('groups', fields, where)
        if result is None:
            return json.dumps({'code':1, 'errmsg':'需要指定一个组'})
        else:
	    util.write_log(username, "select groups by id success")
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
        result = app.config['cursor'].execute_update_sql('groups', data, where, ['name', 'name_cn', 'p_id', 'info'])
        if result == '':
            return json.dumps({'code':1, 'errmsg':'需要指定一个组'})
	util.write_log(username, 'update groups %s success!' % data['name'])
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
        result = app.config['cursor'].execute_delete_sql('groups', data)
        if result == '':
            return json.dumps({'code':1, 'errmsg':'需要指定一个组'})
	util.write_log(username, 'delete groups successed')
	return json.dumps({'code':0,'result':'删除组成功'})
    except:
        logging.getLogger().error('delete groups error: %s' %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'删除组失败'})

#组管理显示本来有的权限（给select多选加一个selected属性）
#@jsonrpc.method('power_sel.get')
#@auth_login
#def get_color(auth_info, **kwargs):
#    if auth_info['code'] == 1:
#        return json.dumps(auth_info)
#    username = auth_info['username']
#    try:
#        where = kwargs.get('where',None)
#        res = app.config['cursor'].get_one_result('groups', ['p_id'], where)
#        p_id = getid_list([res['p_id']])
#
#        result = app.config['cursor'].get_results('power', ['id', 'name'])
#        ids = set([str(x['id']) for x in result]) & set(p_id)
#        for x in result:
#            x['selected'] = 'selected="selected"' if str(x['id']) in ids else ''
#        util.write_log(username,"power_sel.get successful!")
#        return json.dumps({'code':0,'result':result})
#    except:
#        logging.getLogger().error('power_sel.get error! %s'  %  traceback.format_exc())
#        return json.dumps({'code':1,'errmsg':'error: %s'  %  traceback.format_exc()})
#

