#!/usr/bin/env python
#coding: utf-8
from flask import request
from . import app, jsonrpc
import logging, util
import json, traceback,os
from auth import auth_login
import time,requests

@jsonrpc.method('git.create')
@auth_login
def git_create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    if role != 0:
        return json.dumps({'code':1,'errmsg':'只有管理员才有此权限'})
    try:
        data = request.get_json()['params']
        if not data.has_key('principal') or  not app.config['cursor'].if_id_exist('user',data['principal'].split(',')):         
	    return json.dumps({'code':1,'errmsg':'项目负责人输入不正确'})
        if data.has_key('p_uesr') and not app.config['cursor'].if_id_exist('user',data['p_uesr'].split(',')):         
            return json.dumps({'code':1,'errmsg':'项目成员输入不正确'})
        if data.has_key('p_group') and not app.config['cursor'].if_id_exist('user_group',data['p_group'].split(',')):         
            return json.dumps({'code':1,'errmsg':'项目组输入不正确'})
        data['create_date'] = time.strftime('%Y-%m-%d')  
        app.config['cursor'].execute_insert_sql('git',data)

        r = gitolite()
        if r['code'] == 1:
            return json.dumps(r)
        # project_users = util.project_members(db=app.config['cursor']).get(data['name'])    #获取当前项目的所有人  为下面发邮件准备数据
        project_users,principal = util.project_members(db=app.config['cursor'])   #获取当前项目的所有人  为下面发邮件准备数据

        '''sendemail'''
        smtp_to = [(x+'@yuanxin-inc.com') for x in project_users]
        send_info = '创建%s项目成功,工作愉快..............'   % data['name']
        # util.sendmail(app.config, smtp_to, send_info,send_info)

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
    try:
        data = request.get_json()['params']
        where = data.get('where',None)
        data = data.get('data',None)
        if not where:
            return json.dumps({'code':1, 'errmsg':'需要指定更新项目'})
        if not data.get('principal', []):
            return json.dumps({'code':1, 'errmsg': '必须要指定负责人'})
        for k in ['p_user', 'p_group']:
            if k not in data:
                data[k] = ''
        result = app.config['cursor'].get_one_result('git',['name'],where)
        if not result:
	    return json.dumps({'code':1, 'errmsg':'项目不存在'})    
        app.config['cursor'].execute_update_sql('git', data, where)
           
        r = gitolite()
        if r['code'] == 1:
            return json.dumps(r)
        util.write_log(username,'update project %s success' % result['name'])
        return json.dumps({'code':0,'result':'更新项目%s成功' % result['name']})
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
        output = ['id','name','path','principal','p_user','p_group','is_lock','comment']
        data = request.get_json()['params']
        fields = data.get('output', output)
        where = data.get('where',None)
        if not where:
            return json.dumps({'code':1, 'errmsg':'需要指定项目'})
        result = app.config['cursor'].get_one_result('git', fields, where)
        if result:
            util.write_log(username, 'get project success ') 
            return json.dumps({'code':0,'result':result})
        else:
	    return json.dumps({'code':1, 'errmsg':'项目不存在'})    
    except:
        logging.getLogger().error("select project error: %s " % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '查询项目错误'})

@jsonrpc.method('git.getlist')
@auth_login
def git_getlist(auth_info, **kwargs):
    id2name = lambda names, ids: ','.join([names[x] for x in ids if x in names])

    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    uid = int(auth_info['uid'])
    try:
        output = ['id' ,'name','path','principal','p_user','p_group','is_lock','comment']
        data = request.get_json()['params']
        fields = data.get('output', output)
          
        # 查询用户表，生成id2name的字典
        users=app.config['cursor'].users

        # 查询角色表，生成id2name的字典
        groups=app.config['cursor'].groups

        # 管理员查询项目表，把项目表中p_uesr,p_group,principal的ID 转为name
        # 结果:[{'id':1,'name':'devops','principal':'pc','p_user':'pc,wd'....},......]
        projects = app.config['cursor'].get_results('git', fields, where={'is_lock': 0})
        for p  in projects:  # 循环项目列表，判断项目表中的p_user的id是否存在，如果存在则id2name
            p['principal'] = id2name(users, p['principal'].split(','))
            p['p_user'] =  id2name(users, p['p_user'].split(','))
            p['p_group'] =  id2name(groups, p['p_group'].split(','))
        
        # 普通用户只能查看其有权限的项目,上面总结果集projects中过滤
        if role != 0:  
            p = util.user_projects(username, app.config['cursor'])  # 查出用户的项目id2name
            projects = [pro for pro in projects if str(pro['id']) in p] # 获取项目的详情
        util.write_log(username, '查询项目列表成功')  
        return json.dumps({'code':0,'result':projects,'count':len(projects)})
    except:
        logging.getLogger().error("select project list error: %s" % traceback.format_exc())
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
    unlock_project = app.config['cursor'].get_results('git', ['name'], {'is_lock': 0})
    unlock_project = [x['name'] for x in unlock_project]     # 获取未锁定的项目
    group  = util.group_members(db=app.config['cursor'])    # 获取所有组的成员信息
    project_users,principal = util.project_members(db=app.config['cursor'])  # 获取所有项目的成员及负责人

    try:
        git_confile = app.config['git_confile']
        with open(git_confile,'w') as f:
            # 将用户和组信息写入配置文件
            str1 = ""
            for k,v in group.items():
                str1 += "@%s = %s\n" %(k,' '.join(v))
            f.write(str1)
            f.write("\n")

            # 将项目信息写入配置文件
            str2 = ""
            for k,v in project_users.items():
                if k not in unlock_project:
                    continue;
                # 由于projests中存放了项目所有的成员，包括负责人。需要把负责人剔除
                v = list(set(v)-set(principal[k]))
                str2 += "repo %s \n" % k
                str2 += " RW+ = admin %s \n" % ' '.join(principal[k])   # 负责人的权限最大
		if v:
                    str2 += " -  master = %s \n" %(' '.join(v)) # 项目成员无权操作master分支
                    str2 += " RW = %s \n" %(' '.join(v))        # 项目成员可以操作其他分支
            f.write(str2)
        res, msg=util.run_script_with_timeout("%s/git.sh" % app.config['script_path'])
        if res:
            return {'code':0,'result':"git操作成功"}
        else:
             return {'code':1, 'errmsg': "git更新配置文件失败"}
    except:
        logging.getLogger().error("get config error: %s" % traceback.format_exc())
        return {'code':1,'errmsg':"写配置文件报错"}
