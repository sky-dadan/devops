#!/usr/bin/env python
#coding: utf-8
from flask import Flask, request
from . import app
import logging, util,mail
import json, traceback,os
from auth import auth_login

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
    result = util.get_git() 
    if int(result['code']) ==0:
        group  = result['group']
        project = result['project']
        for p in  project.keys():
		project[p]['user_rw_perm'] = ' '.join(project[p]['user_rw_perm'])
		project[p]['user_all_perm'] = ' '.join(project[p]['user_all_perm'])
		project[p]['group_rw_perm'] = "@%s" %  ' @'.join(project[p]['group_rw_perm'])
		project[p]['group_all_perm'] = "@%s" % ' @'.join(project[p]['group_all_perm'])
        print group


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
                str2  += "repo %s \n    RW+ = %s %s \n    RW = %s %s \n" % (k,v['group_all_perm'],v['user_all_perm'],v['group_rw_perm'],v['user_rw_perm'])
            with open("/root/gitconfig/gitolite-admin/conf/gitolite.conf",'a') as f:
                f.write(str2)

            #git add/commit/push生效
            #os.system("cd ** && git add && git commit -m 'update git conf' && git push origin master")
            
            #给相关人员发邮件,在主程序中调用,格式如下
 #           subject = "devops项目创建成功"
 #           content = "项目地址为：%s" % ("devops")
 #           smtp_to = ['sa@yuanxin-inc.com','liuziping@yuanxin-inc.com']
 #           mail.sendmail(subject,content,smtp_to)


            return  json.dumps({'code':0,'result':"git操作成功"})
        except:
            logging.getLogger().error("get config error: %s" % traceback.format_exc())
            return json.dumps({'code':1,'errmsg':"写配置文件报错"})
    else:
         return json.dumps({'code':1,'errmsg':"获取用户，组或者仓库出错"})



