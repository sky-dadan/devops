#!/usr/bin/env python
#coding: utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app, jsonrpc
import logging, util
import json, traceback,os
from auth import auth_login
import time,requests
from jsondate import MyEncoder
from user_perm import getid_list

@jsonrpc.method('git.create')
@auth_login
def git_create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'只有管理员才有此权限'})
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

        r = gitolite()
        if r['code'] == 1:
            return json.dumps(r)

        project = util.project_members(db=app.config['cursor']).get(p_data['name'])    #获取当前项目的所有人  为下面发邮件准备数据
        '''sendemail'''
        smtp_to = [(x+'@yuanxin-inc.com') for x in project]
        send_info = '创建%s项目成功,工作愉快..............'   % p_data['name']
        util.sendmail(app.config, smtp_to, send_info,send_info)

        util.write_log(username,{'code':0,'result':'create project %s success'  %  data['name']})
        return json.dumps({'code':0,'result':'创建项目%s成功'  %  data['name']})    
    except:
        logging.getLogger().error('create project error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'创建项目失败'})


@jsonrpc.method('git.update')
@auth_login
def git_update(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'只有管理员才有此权限'})
    p_data = {}
    p_perm_data = {'user_all_perm': '', 'group_all_perm': '', 'user_rw_perm': '', 'group_rw_perm': ''}
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
            return json.dumps({'code':1,'errmsg':'需要指定一个项目'})
        else:
            r = gitolite()
            if r['code'] == 1:
                return json.dumps(r)
        util.write_log(username,'update project %s success' % data['name'])
        return json.dumps({'code':0,'result':'更新项目%s成功' % data['name']})
    except:
        logging.getLogger().error("update project error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'更新项目失败'})


@jsonrpc.method('git.get')
@auth_login
def git_get(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'只有管理员才有此权限'})
    try:
        pro_fields = ['id','name','path','principal','tag','create_date','is_lock','comment']
        pro_perm_fields = ['user_all_perm','group_all_perm','user_rw_perm','group_rw_perm']
        data = request.get_json()
        data = data['params']

        projects = util.project_perm_id2name(db=app.config['cursor'])
        #将上面projects里的列表变成以逗号分隔的字符串{'ask.100xhs.com':{'user_all_perm':['zhangxunan','lisi']}}
        for pro in projects:
            for pro_field in pro_perm_fields:
                projects[pro][pro_field] = ','.join(projects[pro][pro_field])
        #user表里查出id,name,将查出来的数据改成例如{'1':'tom','2':'jerry'}重新赋值
        users = app.config['cursor'].users
        # 条件,项目ID 例如：{'id':1}
        where = kwargs.get('where',None)
        #得到项目id为where条件的结果
        result = app.config['cursor'].get_one_result('project', pro_fields,where) 
        #更新result['principal']的值，将id替换成负责人的用户名
        result['principal'] = users.get(str(result['principal']),'')
        #将权限表的数据追加到result字典里
        result.update(projects[result['name']])

        util.write_log(username, 'get project success') 
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

        projects = util.project_perm_id2name(db=app.config['cursor'])
        #将上面projects里的列表变成以逗号分隔的字符串{'ask.100xhs.com':{'user_all_perm':['zhangxunan','lisi']}}
        for pro in projects:
            for pro_field in pro_perm_fields:
                projects[pro][pro_field] = ','.join(projects[pro][pro_field])
        #user表里查出id,name,将查出来的数据改成例如{'1':'tom','2':'jerry'}重新赋值
        users = app.config['cursor'].users
        #查出项目列表
        result = app.config['cursor'].get_results('project', pro_fields)
        #将负责人id替换成name
        url_prefix = app.config.get('git_url_prefix', '').strip('/')
        for res in result:
            res['principal'] = users.get(str(res['principal']),'')
            if not res['path'].startswith("http://"):
                res['path'] = '/'.join([url_prefix, res['path'].strip('/')])
        #将权限信息追加到result字典里
        for project in result:
            project.update(projects[project['name']])
        #管理员反回所有的结果
        if role == 0:
            util.write_log(username, '查询项目列表成功')  
            return json.dumps({'code':0,'result':result,'count':len(result)},cls=MyEncoder)
        #普通用户返回他所拥有权限的项目
        else:
            user_projects = util.user_projects(username, app.config['cursor'])
            result = [x for x in result if str(x['id']) in user_projects]
            util.write_log(username, '查询项目列表成功')  
            return json.dumps({'code':0,'result':result,'count':len(result)},cls=MyEncoder)
    except:
        logging.getLogger().error("select project list error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '查询项目列表错误'})

#新添加查询某个用户所拥有的项目列表，后期将起优化到getlist对应的部分
@jsonrpc.method('userproject.getlist')
@auth_login
def myprojects(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        res = util.user_projects(username, app.config['cursor']) #dict
        return json.dumps({'code': 0, 'result': res})
    except:
        logging.getLogger().error("调用userproject函数失败: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '查询项目列表错误'})

@app.route('/api/gitolite',methods=['GET'])
def git_api():
    res = gitolite()
    return json.dumps(res)

'''
渲染gitolite配置文件及推送接口
Use:
    curl http://127.0.0.1:1000/api/gitolite
'''
def gitolite():
    unlock_project = app.config['cursor'].get_results('project', ['name'], {'is_lock': 0})
    unlock_project = [x['name'] for x in unlock_project]
    group  = util.group_members(db=app.config['cursor'])
    project = util.project_perm_id2name(db=app.config['cursor'])
    for p in project:
        project[p]['user_rw_perm'] = ' '.join(project[p]['user_rw_perm'])
        project[p]['user_all_perm'] = ' '.join(project[p]['user_all_perm'])
        project[p]['group_rw_perm'] = ' '.join(['@%s' % x for x in project[p]['group_rw_perm']])
        project[p]['group_all_perm'] = ' '.join(['@%s' % x for x in project[p]['group_all_perm']])

    try:
        #将用户和组信息写入配置文件
        git_confile = app.config['git_confile']
        with open(git_confile,'w') as f:
            str1 = ""
            for k,v in group.items():
                str1 += "@%s = %s\n" %(k,' '.join(v))
            f.write(str1)
            f.write("\n")

            #将项目信息写入配置文件
            str2 = ""
            for k,v in project.items():
                if k not in unlock_project:
                    continue
                if not any([v['group_all_perm'], v['user_all_perm'], v['group_rw_perm'], v['user_rw_perm']]):
                    continue
                str2 += "repo %s\n" % k
                str2 += "    RW+ = admin\n"
                if v['group_all_perm'] or v['user_all_perm']:
                    str2 += "    RW+ = %s %s\n" % (v['group_all_perm'], v['user_all_perm'])
                if v['group_rw_perm'] or v['user_rw_perm']:
                    str2 += "    - master = %s %s\n" % (v['group_rw_perm'], v['user_rw_perm'])
                    str2 += "    RW = %s %s\n" % (v['group_rw_perm'], v['user_rw_perm'])
            f.write(str2)

        res, msg=util.run_script_with_timeout("%s/git.sh" % app.config['script_path'])
        if res:
            return {'code':0,'result':"git操作成功"}
        else:
            return {'code':1, 'errmsg': "git更新配置文件失败"}
    except:
        logging.getLogger().error("get config error: %s" % traceback.format_exc())
        return {'code':1,'errmsg':"写配置文件报错"}
