#!/usr/bin/env python
#coding: utf-8
from flask import Flask, request
from . import app
import logging, util,mail
import json, traceback,os
from auth import auth_login

def get_git():
    try: 
        #获取所有用户信息
        users=app.config['cursor'].get_results('user',['username','r_id'])
        users=dict((x['username'],x['r_id'].split(',')) for x in users)
        #print users   #{u'songpeng': [u'1', u'2'], u'admin': [u'1', u'2', u'4', u'3']}

        #获取所有组信息
        groups=app.config['cursor'].get_results('groups',['id','name'])
        groups=dict((str(x['id']),x['name']) for x in groups)
        #print groups  #{'1': u'sa', '2': u'admin', '3': u'ask', '4': u'PHP']}

        #获取每个组的成员——git配置文件分组数据渲染
        group = {}
        for g_name in groups.values():
            group[g_name]=[]  
        #print group     #{u'admin': [], u'iOS': [], u'sa': [], u'ask': [], u'PHP':[]}
        for u_name,r_id in users.items():
            for g_id,g_name in groups.items():
                if g_id in r_id:
                     group[g_name].append(u_name)
        #print group    #{'ios': ['admin', 'wd'], 'php': ['songpeng'], 'sa': ['admin', 'songpeng']}

        #获取项目列表
        projects = app.config['cursor'].get_results('project',['id','name'])
        projects = dict((str(x['id']),x['name']) for x in projects)
	
        #获取每个项目的权限列表,取出来的是id
	result  = [] 
        perm_fields = ['id','user_all_perm','group_all_perm','user_rw_perm','group_rw_perm']
        for id in projects.keys():
            p_perm = app.config['cursor'].get_one_result('project_perm',perm_fields,{"id":int(id)})
            result.append(p_perm)

	#将权限对应的用户，组id换成适配为name
        user_git=app.config['cursor'].get_results('user',['id','username'])
        user_git=dict((str(x['id']),x['username']) for x in user_git)
	
	#将每个项目的权限id列表匹配为对应的username  gname,projectname
        p = {}
	for project in result:
		name=projects[str(project['id'])]  #通过id匹配对应的project name
        	a = {}  #临时存放不同权限对应的项目及用户和组得字典 #{'user_all_perm': u'zhangxunan,dutianbo'}
        	b = {}
        	c = {}
        	d = {}
		a['user_all_perm'] =' '.join([user_git.get(str(uid),'None') for uid in project['user_all_perm'].split(',')]) #将用户或组id匹配为name 
		b['user_rw_perm'] =' '.join([user_git.get(str(uid),'None') for uid in project['user_rw_perm'].split(',')])  
		c['group_rw_perm'] =' @'.join([groups.get(str(gid),'None') for gid in project['group_rw_perm'].split(',')])  
		d['group_all_perm'] =' @'.join([groups.get(str(gid),'None') for gid in project['group_all_perm'].split(',')])  
		p[name]=a          #第一轮循环 {u'ask.100xhs.com': {'user_all_perm': u'lisi'}}
		p[name].update(b)  #{u'ask.100xhs.com': {'user_all_perm': u'lisi','user_rw_perm': u'wd'}}
		p[name].update(c)
	 	p[name].update(d)
	#print p	
                
        return json.dumps({'code':'0','group':group,'project':p})
    except:
        logging.getLogger().error("get config error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':"获取用户，组及项目报错"})

@app.route('/api/gitolite',methods=['GET'])
#@auth_login
#def gitolite(auth_info):
def gitolite():
    ''' 
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    usename = auth_info['usename']
    role = auth_info['role']
    if role !=0:
        return json.dumps('code':1,'errmsg':'必须管理员才能执行')
    '''
    result = get_git() 
    result = json.loads(result)
    if int(result['code']) ==0:
        group = result['group']
        project = result['project']

        try:
            #每次将原有配置文件删除
            if os.path.exists("/root/gitconfig/gitolite-admin/conf/gitolite.conf"):
                os.system("rm -fr  /root/gitconfig/gitolite-admin/conf/gitolite.conf") 

            #将用户和组信息写入配置文件
            str1 = ""
            for k,v in group.items():
                str1 += "@%s = %s \n" %(k,' '.join(v))
            with open("/root/gitconfig/gitolite-admin/conf/gitolite.conf",'a') as f:
                f.write(str1)

            #将项目信息写入配置文件
            str2 = ""
            for k,v in project.items():
                    str2  += "repo %s \n    RW+ = @%s %s \n    RW = @%s %s \n" % (k,v['group_all_perm'],v['user_all_perm'],v['group_rw_perm'],v['user_rw_perm'])
            with open("/root/gitconfig/gitolite-admin/conf/gitolite.conf",'a') as f:
                f.write(str2)

            #git add/commit/push生效
            #os.system("cd ** && git add && git commit -m 'update git conf' && git push origin master")
            
            #给相关人员发邮件,在主程序中调用,格式如下
            subject = "devops项目创建成功"
            content = "项目地址为：%s" % ("devops")
            smtp_to = ['sa@yuanxin-inc.com','liuziping@yuanxin-inc.com']
            mail.sendmail(subject,content,smtp_to)


            return json.dumps({'code':0,'result':"git操作成功"})
        except:
            logging.getLogger().error("get config error: %s" % traceback.format_exc())
            return json.dumps({'code':1,'errmsg':"写配置文件报错"})
    else:
        return json.dumps({'code':1,'errmsg':"获取用户，组或者仓库出错"})



