#!/usr/bin/env python
#coding: utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app, jsonrpc
import logging, util
import json, traceback
from auth import auth_login
import time,requests
from jsondate import MyEncoder
from user_perm import getid_list


#headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }
headers = {"Content-Type": "application/json"}
#将用户id,组id替换为用户name和组name
def id2name(pro_perm_result,fields,users,groups):
    for res in pro_perm_result:
        for key in fields:
            if  key.startswith('user'):
                res[key] = ','.join([users[x] for x in res[key].split(',') if x in users]) if res[key] else ''
            elif key.startswith('group'):
                res[key] = ','.join([groups[x] for x in res[key].split(',') if x in groups]) if res[key] else ''
            else:
                continue

@jsonrpc.method('git.create')
@auth_login
def create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'you are not admin'})
    p_data, p_perm_data = {},{}     # p_data是project表的相关数据，p_perm_data是project_perm表的相关数据
    pro_field = ['name','path','principal','tag','create_date','is_lock','comment']
    try:
        data = request.get_json()['params']
        data['create_date'] = time.strftime('%Y-%m-%d')    #添加项目创建时间
        for key in data:
            if key in pro_field:
                p_data[key] = data[key]
            else:
                p_perm_data[key] = data[key]              #{'user_all_perm':'1,2,3','user_rw_perm':'1','group_all_perm':'4,5','group_rw_perm':'2'}
        app.config['cursor'].execute_insert_sql('project',p_data)
        p_id = app.config['cursor'].get_one_result('project',['id'],{'name':p_data['name']})   #获取当前创建项目的id
        p_perm_data['id'] = p_id['id']                    #创建project_perm准备的数据
        app.config['cursor'].execute_insert_sql('project_perm',p_perm_data)
        project = util.get_git()    #获取当前项目的所有人  为下面发邮件准备数据
        project = project['p_all_users'][p_data['name']]
        project_name = list(set(project))                       #去掉重复的用户名 

        r = requests.get("http://%s/api/gitolite" % app.config['api_host'], headers = headers)
        t = json.loads(r.text)
        if t['code'] == '1':
            return r.text

        '''sendemail'''
        smtp_to = [(x+'@yuanxin-inc.com') for x in project_name]
        send_info = '创建%s项目成功,工作愉快..............'   % p_data['name']
        util.sendmail(app.config, smtp_to, send_info,send_info)

        util.write_log(username,{'code':0,'result':'create  %s success'  %  data['name']})
        return json.dumps({'code':0,'result':'创建项目%s成功'  %  data['name']})    
    except:
        logging.getLogger().error('create project error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'创建项目失败'})


@jsonrpc.method('git.update')
@auth_login
def update(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'you are not admin'})
    p_data, p_perm_data = {},{}
    pro_field = ['name','path','principal','tag','create_date','is_lock','comment']
    try:
        data = kwargs.get('data',None)
        where = kwargs.get('where',None)
        for key in data:
            if key in pro_field:
                p_data[key] = data[key]
            else:
                p_perm_data[key] = data[key]
        result = app.config['cursor'].execute_update_sql('project',p_data,where)
        result2 = app.config['cursor'].execute_update_sql('project_perm',p_perm_data,where)
        if result == '' or result2 == '':
            return json.dumps({'code':1,'errmsg':'you must give an id!'})
        util.write_log(username,'update project %s success' % data['name'])
        return json.dumps({'code':0,'result':'更新项目%s成功' % data['name']})
    except:
        logging.getLogger().error("update project error : %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'更新项目失败'})


@jsonrpc.method('git.get')
@auth_login
def create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'you are not admin'})
    try:
        pro_fields = ['id','name','path','principal','tag','create_date','is_lock','comment']
        pro_perm_fields = ['user_all_perm','group_all_perm','user_rw_perm','group_rw_perm']
        data = request.get_json()
        data = data['params']
        #user表里查出id,name,将查出来的数据改成例如{'1':'tom','2':'jerry'}重新赋值
        users = util.getinfo('user',['id','name'])
        #groups表里查出id,name,将查出来的数据改成例如{'1':'sa','2':'ask'}
        groups = util.getinfo('groups',['id','name'])
        # 条件,项目ID 例如：{'id':1}
        where = kwargs.get('where',None)
        #得到项目id为where条件的结果
        result = app.config['cursor'].get_one_result('project', pro_fields,where) 
        #更新result['principal']的值，将id替换成负责人的用户名
        result['principal'] = users[str(result['principal'])]
        #将项目的id做为条件
        where = {'id':int(result['id'])} 
        #查出项目id对应的权限
        pro_perm_result = app.config['cursor'].get_one_result('project_perm',pro_perm_fields,where) 
        #将用户id替换为用户名,组id替换为组名
        id2name([pro_perm_result],pro_perm_fields,users,groups)
        #将更新后的结果追加到result字典里
        result.update(pro_perm_result) 

        util.write_log(username, 'select project sucess') 
        return json.dumps({'code':0,'result':result},cls=MyEncoder)
    except:
        logging.getLogger().error("select project error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'select project error'})

@jsonrpc.method('git.getlist')
@auth_login
def create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    uid = int(auth_info['uid'])
    try:
        pro_fields = ['id','name','path','principal','tag','create_date','is_lock','comment']
        pro_perm_fields = ['id','user_all_perm','group_all_perm','user_rw_perm','group_rw_perm']
        data = request.get_json()
        data = data['params']
        #user表里查出id,name,将查出来的数据改成例如{'1':'tom','2':'jerry'}重新赋值
        users = util.getinfo('user',['id','name'])
        #groups表里查出id,name,将查出来的数据改成例如{'1':'sa','2':'ask'}
        groups = util.getinfo('groups',['id','name']) 
        #查出项目列表
        result = app.config['cursor'].get_results('project', pro_fields)
        #将负责人id替换成name
        for res in result:
            res['principal'] = users[str(res['principal'])]
        #查出项目权限列表
        pro_perm_result = app.config['cursor'].get_results('project_perm',pro_perm_fields)
        # 将权限表里的用户id,组id，替换成用户名，组名
        id2name(pro_perm_result,pro_perm_fields,users,groups)
        #将pro_perm_result的结果改成{1,{'id':1,'user_all_perm':'tom,jerry',...},2:{'id':2,'user_all_perm':'jack,rose',...}}
        pro_perm_result = dict([(x['id'], x) for x in pro_perm_result])
        #将权限信息追加到result字典里
        for project in result:
            project.update(pro_perm_result[project['id']])
        #管理员反回所有的结果
        if role == 0:
            util.write_log(username, 'select project list sucess')  
            return json.dumps({'code':0,'result':result,'count':len(result)},cls=MyEncoder)
        #普通用户返回他所拥有权限的项目
        else:
            perm_fields = ['user_all_perm','group_all_perm','user_rw_perm','group_rw_perm']
            project_list = []
            git_result = util.get_git() 
            if int(git_result['code']) ==0:
                projects = git_result['project']
                groups = git_result['group']
            for key in projects.keys():
                #获取每个项目中拥有权限的人的列表,做个并集存到perm_users列表里
                perm_users = util.get_userlist(projects,groups,key)
                print "perm_users=",perm_users
                #判断登录用户是否在perm_users列表里，如果存在把这个项目名称存到project_list列表里
                if username in perm_users:
                    project_list.append(key)
            #把上面已经查出来result再做一个判断，判断项目名字是否存在project_list列表里，如果存在则把结果存到res列表里
            res = []
            for pro in result:
                if pro['name'] in project_list:
                    res.append(pro)
            #最后返回过虑后的结果res
            util.write_log(username, 'select project list sucess')  
            return json.dumps({'code':0,'result':res,'count':len(res)},cls=MyEncoder)
    except:
        logging.getLogger().error("select project list error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'select project list error'})


