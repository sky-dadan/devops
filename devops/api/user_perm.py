#!/usr/bin/env python
#coding:utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app , jsonrpc
import logging, util
from auth import auth_login
import json, traceback

#这里是关于用户权限的查看，修改  组的增删改查

def getid_list(ids):   #传递过来的列表参数  [u'1,2'] or  [u'1,2', u'1,3,4']
    if not isinstance(ids, list):
        return None
    id_list = set()
    for x in ids:    #取出来的值是元组  lv = (u'1,2',)
        id_list.update(set(x.split(',')))
    id_list = list(id_list)
    id_list.sort()
    print id_list
    return  id_list

@jsonrpc.method('user_perm.getlist')
@auth_login
def getlist(auth_info,**kwargs):
    if auth_info['code']==1:
        return json.dumps(auth_info)
    username = auth_info['username']
    id = auth_info['uid']
    try:
        output = ['name','name_cn','url','info']
        fields = kwargs.get('output', output)

        res = app.config['cursor'].get_one_result('user', ['r_id'], {'username': username})
        r_id = getid_list([res['r_id']])

        res = app.config['cursor'].get_results('groups', ['p_id'], {'id': r_id})
        perm_result = getid_list([x['p_id'] for x in res])

        result = app.config['cursor'].get_results('power', fields, {'id': perm_result})
        util.write_log(username, "get permission success")
        return json.dumps({'result':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error("get list permission error: %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'getlist error : %s'  % traceback.format_exc()})


@jsonrpc.method('user_perm.get')
@auth_login
def getlist_byid(auth_info,**kwargs):
    if auth_info['code']==1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['name','name_cn','url','info']
        fields = kwargs.get('output', output)
        where = kwargs.get('where')
        if not where.has_key('id'):
            return json.dumps({'code':1,'errmsg':'need give an id!'})

        res = app.config['cursor'].get_one_result('user', ['r_id'], where)
        r_id = getid_list([res['r_id']])

        res = app.config['cursor'].get_results('groups', ['p_id'], {'id': r_id})
        perm_result = getid_list([x['p_id'] for x in res])

        result = app.config['cursor'].get_results('power', fields, {'id': perm_result})
        util.write_log(username, "get permission success")
        return json.dumps({'result':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error("get list permission error: %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'getlist error : %s'  % traceback.format_exc()})

@jsonrpc.method('user_perm.update')
@auth_login
def update(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code':1,'errmsg':'you are not admin'})
    try:
        data = request.get_json()['params']
        app.config['cursor'].execute_update_sql('user', {'r_id': data['r_id']}, data['where'])
        util.write_log(username, 'update permission success')
        return json.dumps({'code':0,'result':'update permission success!'})
    except:
        logging.getLogger().error(username,'update user permission error: %s' %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'error: %s' %  traceback.format_exc()})

@jsonrpc.method('user_groups.getlist')
@auth_login
def user_groups(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json,dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','name','name_cn','p_id','info']
        fields = kwargs.get('output', output)

        res = app.config['cursor'].get_one_result('user', ['r_id'], {'username': username})
        r_id= getid_list([res['r_id']])
        print r_id
        result = app.config['cursor'].get_results('groups', fields, {'id': r_id})
        util.write_log(username, "get groups success")
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error("get list groups error: %s"  % traceback.format_exc())
        return json.dumps({'code':1, 'errmsg':'get groups error %s'   %  traceback.format_exc()})

@jsonrpc.method('user_groups.get')
@auth_login
def user_group_byid(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['name','name_cn','id','p_id','info']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        if not where.has_key('id'):
            return json.dumps({'code':1,'errmsg':'need give an id!'})

        res = app.config['cursor'].get_one_result('user', ['r_id'], where)
        r_id = getid_list([res['r_id']])

        result = app.config['cursor'].get_reuslts('groups', fields, {'id': r_id})
        util.write_log(username, "get user_groups success")
        return json.dumps({'result':0, 'result':result,'count':len(result)})
    except:
        logging.getLogger().error('get list user_groups error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':"get list user_groups error  : %s" % traceback.format_exc()})

@jsonrpc.method('groups_sel.get')
@auth_login
def get_color(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        where = kwargs.get('where',None)
        print where
        res = app.config['cursor'].get_one_result('user', ['r_id'], where)
        r_id = getid_list([res['r_id']])

        result = app.config['cursor'].get_results('groups', ['id', 'name'])
        ids = set([str(x['id']) for x in result]) & set(r_id)
        for x in result:
            x['selected'] = 'selected="selected"' if str(x['id']) in ids else ''
        util.write_log(username, "groups_sel.get successful!")
        return json.dumps({'code':0,'result':result})
    except:
        logging.getLogger().error('groups_sel.get error!')
        return json.dumps({'code':1,'errmsg':'error: %s'  %  traceback.format_exc()})

@jsonrpc.method('power_sel.get')
@auth_login
def get_color(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        where = kwargs.get('where',None)
        res = app.config['cursor'].get_one_result('groups', ['p_id'], where)
        p_id = getid_list([res['p_id']])

        result = app.config['cursor'].get_results('power', ['id', 'name'])
        ids = set([str(x['id']) for x in result]) & set(p_id)
        for x in result:
            x['selected'] = 'selected="selected"' if str(x['id']) in ids else ''
        util.write_log(username,"power_sel.get successful!")
        return json.dumps({'code':0,'result':result})
    except:
        logging.getLogger().error('power_sel.get error! %s'  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'error: %s'  %  traceback.format_exc()})


@jsonrpc.method('user.getlist')
@auth_login
def user_getlist(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','username','name','email','mobile','is_lock']
        fields = kwargs.get('output', output)
        result = app.config['cursor'].get_results('user', fields)
        util.write_log(username, 'user.getlist successed!')
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error('user.getlist error : %s')
        return json.dumps({'code':1,'errmsg':'user.getlist error:  %s'  %  traceback.format_exc()})


@jsonrpc.method('user.get')
@auth_login
def user_get(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','username','name','email','mobile','is_lock']
        fields = kwargs.get('output', output)
        where = kwargs.get('where')
        result = app.config['cursor'].get_one_result('user',fields, where)
        util.write_log(username,'user.get successed!')
        return json.dumps({'code':0,'result':result})
    except:
        logging.getLogger().error('user.get error: %s' %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'user.get error: %s' %  traceback.format_exc()})
