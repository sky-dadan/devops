#!/usr/bin/env python
#coding:utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app , jsonrpc
import logging, util
from auth import auth_login
import json, traceback,hashlib
import htpasswd

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

def git_passwd(user, password):
    try:
        with htpasswd.Basic(app.config['git_passwd_file']) as user_pwd:
            if user in user_pwd:
                user_pwd.change_password(user, password)
            else:
                user_pwd.add(user.password)
        return True
    except:
        logging.getLogger().error("Set '%s' password error: %s" % (user, traceback.format_exc()))
        return False

#创建用户
@jsonrpc.method('user.create')
@auth_login
def createuser(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return  json.dump(auth_info)
    username = auth_info['username']
    try:
        data = request.get_json()['params']
        if 'r_id' not in data:
            return json.dumps({'code': 1, 'errmsg': "必须选择一个所属组!"})
        if data['password'] != data['repwd']:
            return json.dumps({'code': 1, 'errmsg': "两次输入的密码不一致!"})
        elif len(data['password']) < 6:
            return json.dumps({'code': 1, 'errmsg': '密码至少需要6位!'})
        else:
            data.pop('repwd')    #因为表单是整体打包过来的，第二次输入的密码字段不存在，需要删除
        data['password'] = hashlib.md5(data['password']).hexdigest()
        app.config['cursor'].execute_insert_sql('user', data)

        if not git_passwd(username, data['password']):
            return json.dumps({'code': 1, 'errmsg': '创建Git密码失败，请检查配置环境'})
        util.write_log(username, "create_user %s" % data['username'])
        return json.dumps({'code': 0, 'result': 'Create %s success' % data['username']})
    except:
        logging.getLogger().error("Create user error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '创建用户失败，有异常情况'})

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

#获取用户信息
@jsonrpc.method('user.getinfo')
@auth_login
def userselfinfo(auth_info,**kwargs):
    if auth_info['code'] ==  1:
        return  json.dump(auth_info)
    username = auth_info['username']
    fields = ['id','username','name','email','mobile','role','is_lock','r_id']
    try:
        #获取组所有的id,name并存为字典如：{'1': 'sa', '2': 'php'}
        gids = app.config['cursor'].get_results('groups', ['id', 'name', 'p_id'])
        own_pids = set([])
        for x in gids:
            own_pids |= set(x['p_id'].split(','))
        gids = dict([(str(x['id']), x['name']) for x in gids])

        pids = app.config['cursor'].get_results('power', ['id', 'name', 'name_cn', 'url'])
        pids = dict([(str(x['id']), dict([(k, x[k]) for k in ('name', 'name_cn', 'url')])) for x in pids])

        user = app.config['cursor'].get_one_result('user', fields, where={'username': username})
        user['r_id'] = [gids[x] for x in user['r_id'].split(',') if x in gids]
        user['p_id'] = dict([(pids[x]['name'], pids[x]) for x in own_pids if x in pids])
        util.write_log(username, 'get_user_info')
        return  json.dumps({'code': 0, 'user': user})
    except:
        logging.getLogger().error("Get users list error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'Get users error'})

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
        return json.dumps({'code':1,'errmsg':'只有管理员才可操作!'})
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
@jsonrpc.method('user.delete')
@auth_login
def userdelete(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code':1,'errmsg':'you are not admin!'})
    try: 
        data = request.get_json()['params']
        result = app.config['cursor'].execute_delete_sql('user', data)
        if result == '':
            return json.dumps({'code':1,'errmsg':'you need give an id!'})
        util.write_log(username, 'delete user successed')
        return json.dumps({'code':0,'result':'delete user successed'})
    except:
        logging.getLogger().error('delete groups error: %s' %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'error: %s'  % traceback.format_exc()})


#修改密码
@app.route('/api/password',methods=['PUT'])
@auth_login
def passwd(auth_info):
    if auth_info['code'] == 1:   #主要用于判断认证是否过期，过期会会在web提示
        return json.dumps(auth_info)
    username = auth_info['username']
    uid = int(auth_info['uid'])
    role = int(auth_info['role'])
    try:
        data = request.get_json()
        if role==0 and 'user_id' in data:   # admin no need oldpassword  but need user_id
            user_id = data['user_id']
            if not app.config['cursor'].if_userid_exist(user_id): 
                return json.dumps({'code':1,'errmsg':'需要更改密码的用户不存在'})
            password = hashlib.md5(data['password']).hexdigest()
            app.config['cursor'].execute_update_sql('user', {'password': password}, {'id': user_id})
        else:                  #user  need input oldpassword
            if not data.has_key("oldpassword") :
                return json.dumps({'code':1,'errmsg':'需要提供原密码'})
            oldpassword = hashlib.md5(data['oldpassword']).hexdigest()
            res = app.config['cursor'].get_one_result('user', ['password'], {'username': username})
            if res['password'] != oldpassword:
                return json.dumps({'code':1,'errmsg':'原密码输入有误'})
            password = hashlib.md5(data['password']).hexdigest()
            app.config['cursor'].execute_update_sql('user', {'password': password}, {'username': username})

        if not git_passwd(username, data['password']):
            return json.dumps({'code': 1, 'errmsg': 'Git密码更新失败，请联系管理员'})
        util.write_log(username,'update user password')
        return json.dumps({'code':0,'result':'update password success'  })
    except:
        logging.getLogger().error('update user password error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'更新密码有异常'})


#用户登录
@app.route('/api/auth', methods=['GET'])
def login():
    if request.method == 'GET':
        try:
            username = request.args.get('username', None)
            passwd = request.args.get('passwd', None)
            passwd = hashlib.md5(passwd).hexdigest()
            if not (username and passwd):
                return json.dumps({'code': 1, 'errmsg': "Please input username or password."})

            result = app.config['cursor'].get_one_result('user', ['id', 'username', 'password', 'role', 'is_lock'], {'username': username})
            if not result:
                return json.dumps({'code': 1, 'errmsg': "No such user."})
            if result['is_lock'] == 1:
                return json.dumps({'code': 1, 'errmsg': "User '%s' is locked." % username})

            if passwd == result['password']:
                s = util.get_validate(result['username'], result['id'], result['role'], app.config['passport_key'])
                return json.dumps({'code': 0, 'authorization': s})
            else:
                return json.dumps({'code': 1, 'errmsg': "Password is wrong."})
        except:
            logging.getLogger().error("user login error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': "login exception"})
    else:
        return json.dumps({'code': 1, 'errmsg': "HTTP Method '%s' doesn't support" % request.method})



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

