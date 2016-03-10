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

        r = gitolite()
        t = json.loads(r)
        print t
        if t['code'] == '1':
            return r

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
        else:
            r = gitolite()
            t = json.loads(r)
            print t
            if t['code'] == '1':
                return r
        util.write_log(username,'update project %s success' % data['name'])
        return json.dumps({'code':0,'result':'更新项目%s成功' % data['name']})
    except:
        logging.getLogger().error("update project error : %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'更新项目失败'})


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
        print "pro_all_users = ",pro_all_users
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
            res = util.partOfTheProject(result,projects,pro_all_users,username)
            util.write_log(username, '查询项目列表成功')  
            return json.dumps({'code':0,'result':res,'count':len(res)},cls=MyEncoder)
    except:
        logging.getLogger().error("select project list error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '查询项目列表错误'})

@app.route('/api/gitolite',methods=['GET'])
def git_api():
    res = gitolite()
    return res

'''
渲染gitolite配置文件及推送接口
Use:
    curl http://127.0.0.1:1000/api/gitolite
'''
def gitolite():
    git_confile = app.config['git_confile']
    api_dir = os.path.dirname(os.path.realpath(__file__))
    script_dir =  os.path.join(api_dir.rstrip('api'),'script')
    result = util.get_git() 
    if int(result['code']) ==0:
        group  = result['group'] 
        project = result['project']
        for p in project:
            project[p]['user_rw_perm'] = ' '.join(project[p]['user_rw_perm'])
            project[p]['user_all_perm'] = ' '.join(project[p]['user_all_perm'])
            project[p]['group_rw_perm'] = "@%s" %  ' @'.join(project[p]['group_rw_perm'])
            project[p]['group_all_perm'] = "@%s" % ' @'.join(project[p]['group_all_perm'])

        try:
            #每次将原有配置文件删除
            if os.path.exists(git_confile):
                os.unlink(git_confile)
            #将用户和组信息写入配置文件
            str1 = ""
            for k,v in group.items():
                str1 += "@%s = %s \n" %(k,' '.join(v))
            with open(git_confile,'a') as f:
                f.write(str1)

            #将项目信息写入配置文件
            str2 = ""
            for k,v in project.items():
                str2  += "repo %s \n    RW+ = %s %s \n    RW = %s %s \n" % (k,v['group_all_perm'],v['user_all_perm'],v['group_rw_perm'],v['user_rw_perm'])
            with open(git_confile,'a') as f:
                f.write(str2)

            #git add/commit/push生效.路径暂时写死，定版前修改
            stdout=util.run_script("sh %s/git.sh" % script_dir)
            print stdout
            return  json.dumps({'code':0,'result':"git操作成功"})
        except:
            logging.getLogger().error("get config error: %s" % traceback.format_exc())
            return json.dumps({'code':1,'errmsg':"写配置文件报错"})
    else:
         return json.dumps({'code':1,'errmsg':"获取用户，组或者仓库出错"})




