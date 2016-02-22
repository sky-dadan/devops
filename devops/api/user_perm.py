#!/usr/bin/env python
#coding:utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app , jsonrpc
import logging, util
from auth import auth_login
import json, traceback,hashlib

#本模块提供用户信息的增删改查，以及 用户所在组，所有权限的查询

#处理将多选参数转为列表 传入的参数[u'1,2'] or  [u'1,2', u'1,3,4']，结果为['1','2','3','4']
def getid_list(ids):   
    if not isinstance(ids, list):
        return None
    id_list = set()
    for x in ids:    #取出来的值是元组  lv = (u'1,2',)
        id_list.update(set(x.split(',')))
    id_list = list(id_list)
    id_list.sort()
    print id_list
    return  id_list

#创建用户
@jsonrpc.method('user.create')
@auth_login
def createuser(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return  json.dump(auth_info)
    username = auth_info['username']
    try:
        data = request.get_json()['params']
        print data 
        data.pop('repwd')    #因为表单是整体打包过来的，第二次输入的密码字段不存在，需要删除
        data['password'] = hashlib.md5(data['password']).hexdigest()
        app.config['cursor'].execute_insert_sql('user', data)
        util.write_log(username, "create_user %s" % data['username'])
        return json.dumps({'code': 0, 'result': 'Create %s success' % data['username']})
    except:
        logging.getLogger().error("Create user error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'Create user error'})

#获取(uid or username)个人信息，个人信息展示和个人修改信息，以及用户列表中更新用户信息部分的获取数据
@jsonrpc.method('user.get')
@auth_login
def userinfo(auth_info,**kwargs):
    if auth_info['code'] ==  1:
        return  json.dump(auth_info)
    username = auth_info['username']
    try:
        output = ['id','username','name','email','mobile','role','is_lock','r_id']
        fields = kwargs.get('output',output) #api可以指定输出字段，如果没有指定output，就按默认output输出
        where = kwargs.get('where',None)     #前端传来的where条件，可能是uid或者username
        result = app.config['cursor'].get_one_result('user', fields, where)
        if result is '':
            return json.dumps({'code':1, 'errmsg':'must need give a  where field'})
        util.write_log(username, 'get_one_user info') 
        return json.dumps({'code':0,'result':result})
    except:
        logging.getLogger().error("Get users list error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'Get  users error'})

#获取用户列表
@jsonrpc.method('user.getlist')
@auth_login
def userlist(auth_info,**kwargs):
    if auth_info['code'] ==  1:
        return  json.dump(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    users = []
    fields = ['id','username','name','email','mobile','role','is_lock','r_id']
    if role !=0:
        return json.dumps({'code': 1,'errmsg':'you not admin ,Cannot look userlist' })
    try:
        #获取组所有的id,name并存为字典如：{'1': 'sa', '2': 'php'}
        gids = app.config['cursor'].get_results('groups', ['id', 'name'])
        gids = dict([(str(x['id']), x['name']) for x in gids])
        result = app.config['cursor'].get_results('user', fields)
        for user in result: #查询user表中的r_id,与groups表生成的字典对比，一致则将id替换为name,如，"sa,php"
            user['r_id'] = ','.join([gids[x] for x in user['r_id'].split(',') if x in gids])
            users.append(user)
        util.write_log(username, 'get_all_users')
        return  json.dumps({'code': 0, 'users': users,'count':len(users)})
    except:
        logging.getLogger().error("Get users list error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'Get users error'})


#更新用户信息
@jsonrpc.method('user.update')
@auth_login
def userupdate(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code':1,'errmsg':'you are not admin!'})
    try:
        data = request.get_json()['params']
        where = data.get('where',None)
        data = data.get('data',None)
        print data,where
        if int(auth_info['role']) == 0:
            result = app.config['cursor'].execute_update_sql('user', data, where)
        else:
            result =  app.config['cursor'].execute_update_sql('user', data, where,['name','username','email','mobile'])
        if result == '':
            return json.dumps({'code':1, 'errmsg':'you need give an id!'})
        util.write_log(username, 'update groups %s success!' % data['name'])
        return json.dumps({'code':0,'result':'update  %s successed' % data['name']})
    except:
        logging.getLogger().error("update error: %s"  % traceback.format_exc())
        return json.dumps({'code':1, 'errmsg':"error : %s" % traceback.format_exc()})


#删除用户

#修改密码

#用户登录


#用户登录成功后通过用户username获取自己的权限信息，个人中心用户权限部分使用，点击权限名会连接到响应的url
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
        return json.dumps({'resu lt':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error("get list permission error: %s"  %  traceback.format_exc())
        return json.dumps({'cod e':1,'errmsg':'getlist error : %s'  % traceback.format_exc()})

#用户登录成功后通过用户username获取自己的组信息，个人中心调用
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

        result = app.config['cursor'].get_results('groups', fields, {'id': r_id})
        util.write_log(username, "get groups success")
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error("get list groups error: %s"  % traceback.format_exc())
        return json.dumps({'code':1, 'errmsg':'get groups error %s'   %  traceback.format_exc()})
#用户列表更新时，用户所属的组被选中
@jsonrpc.method('groups_sel.get')
@auth_login
def get_color(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        where = kwargs.get('where',None)
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

'''
#通过用户的id获取到某个用户的所有权限内容，不会根据个人对权限做更新，没什么用。且与上面代码冗余，需要整合
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
        r eturn json.dumps({'code':1,'errmsg':'getlist error : %s'  % traceback.format_exc()})

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
@jsonrpc.method('user_groups.get')
@auth_login
def user_group_byid(auth_info, **kwargs):
    if auth_ info['code'] == 1:
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
        retur n json.dumps({'result':0, 'result':result,'count':len(result)})
    except:
        logging.getLogger().error('get list user_groups error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':"get list user_groups error  : %s" % traceback.format_exc()})



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
        re turn json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        logging.getLogger().error('user.getlist error : %s')
        r eturn json.dumps({'code':1,'errmsg':'user.getlist error:  %s'  %  traceback.format_exc()})

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
        ret urn json.dumps({'code':1,'errmsg':'user.get error: %s' %  traceback.format_exc()})

'''        
