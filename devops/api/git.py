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

@jsonrpc.method('git.create')
@auth_login
def git_create(auth_info, **kwargs):
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

        '''sendemail'''
        smtp_to = [(x+'@yuanxin-inc.com') for x in project_name]
        send_info = '创建%s项目成功,工作愉快..............'   % p_data['name']
        util.sendmail(app.config, smtp_to, send_info,send_info)

        requests.get("http://%s/api/gitolite" % app.config['api_host'], headers = headers)

        util.write_log(username,{'code':0,'result':'create  %s success'  %  data['name']})
        return json.dumps({'code':0,'result':'create  %s success'  %  data['name']})    
    except:
        logging.getLogger().error('create project error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'git project create error: 重复的仓库路径'})


@jsonrpc.method('git.update')
@auth_login
def git_update(auth_info,**kwargs):
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
        return json.dumps({'code':0,'result':'update project %s success' % data['name']})
    except:
        logging.getLogger().error("update project error : %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'update project error'})


@jsonrpc.method('git.get')
@auth_login
def git_get(auth_info, **kwargs):
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

        git_result = util.get_git() 
        if int(git_result['code']) ==0:
            projects = git_result['project']
            groups = git_result['group']
            pro_all_users =git_result['p_all_users']
        #将上面projects里的列表变成以逗号分隔的字符串{'ask.100xhs.com':{'user_all_perm':['zhangxunan','lisi']}}
        for pro in projects:
            for pro_field in pro_perm_fields:
                projects[pro][pro_field] = ','.join(projects[pro][pro_field])
        #user表里查出id,name,将查出来的数据改成例如{'1':'tom','2':'jerry'}重新赋值
        users = util.getinfo('user',['id','name'])
        # 条件,项目ID 例如：{'id':1}
        where = kwargs.get('where',None)
        #得到项目id为where条件的结果
        result = app.config['cursor'].get_one_result('project', pro_fields,where) 
        #更新result['principal']的值，将id替换成负责人的用户名
        result['principal'] = users[str(result['principal'])]
        #将权限表的数据追加到result字典里
        result.update(projects[result['name']])

        util.write_log(username, '查询项目成功') 
        return json.dumps({'code':0,'result':result},cls=MyEncoder)
    except:
        logging.getLogger().error("select project error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '查询项目错误'})

@jsonrpc.method('git.getlist')
@auth_login
def git_getlist(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    uid = int(auth_info['uid'])
    try:
        pro_fields = ['id','name','path','principal','tag','create_date','is_lock','comment']
        pro_perm_fields = ['user_all_perm','group_all_perm','user_rw_perm','group_rw_perm']
        data = request.get_json()
        data = data['params']

        git_result = util.get_git() 
        if int(git_result['code']) ==0:
            projects = git_result['project']
            groups = git_result['group']
            pro_all_users =git_result['p_all_users']
        #将上面projects里的列表变成以逗号分隔的字符串{'ask.100xhs.com':{'user_all_perm':['zhangxunan','lisi']}}
        for pro in projects:
            for pro_field in pro_perm_fields:
                projects[pro][pro_field] = ','.join(projects[pro][pro_field])
        #user表里查出id,name,将查出来的数据改成例如{'1':'tom','2':'jerry'}重新赋值
        users = util.getinfo('user',['id','name'])
        #查出项目列表
        result = app.config['cursor'].get_results('project', pro_fields)
        #将负责人id替换成name
        for res in result:
            res['principal'] = users[str(res['principal'])]
        #将权限信息追加到result字典里
        for project in result:
            project.update(projects[project['name']])
        #管理员反回所有的结果
        if role == 0:
            util.write_log(username, '查询项目列表成功')  
            return json.dumps({'code':0,'result':result,'count':len(result)},cls=MyEncoder)
        #普通用户返回他所拥有权限的项目
        else:
            project_list = []
            for key in projects.keys():
                #获取每个项目中拥有权限的人的列表,做个并集存到perm_users列表里
                perm_users = list(set(pro_all_users[key]))
                #判断登录用户是否在perm_users列表里，如果存在把这个项目名称存到project_list列表里
                if username in perm_users:
                    project_list.append(key)
            #把上面已经查出来result再做一个判断，判断项目名字是否存在project_list列表里，如果存在则把结果存到res列表里
            res = []
            for pro in result:
                if pro['name'] in project_list:
                    res.append(pro)
            #最后返回过虑后的结果res
            util.write_log(username, '查询项目列表成功')  
            return json.dumps({'code':0,'result':res,'count':len(res)},cls=MyEncoder)
    except:
        logging.getLogger().error("select project list error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '查询项目列表错误'})


