#!/usr/bin/env python
#coding: utf-8
from flask import Flask, request
from . import app
import logging, util,mail
import json, traceback,os,subprocess
from auth import auth_login

'''
Use:
    curl http://127.0.0.1:1000/api/gitolite
'''
@app.route('/api/gitolite',methods=['GET'])
def gitolite():
    result = util.get_git() 
    if int(result['code']) ==0:
        group  = result['group'] 
        project = result['project']
        for p in  project.keys():
		project[p]['user_ rw_perm'] = ' '.join(project[p]['user_rw_perm'])
		project[p]['user_all_perm'] = ' '.join(project[p]['user_all_perm'])
		project[p]['group_rw_perm'] = "@%s" %  ' @'.join(project[p]['group_rw_perm'])
		project[p]['group_all_perm'] = "@%s" % ' @'.join(project[p]['group_all_perm'])
#        print group


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

            #git add/commit/push生效.路径暂时写死，定版前修改
            p = subprocess.Popen("/home/liuziping/devops.aiyuanxin.com/devops/script/git.sh",stdout=subprocess.PIPE,shell = True)
            result = p.stdout.read()
            print result


            #给相关人员发邮件,在主程序中调用,格式如下
 #           subject = "devops项目创建成功"
 #           content = "项目地址为：%s" % ("devops")
 #           smtp_to = ['sa@yuanxin-inc.com','liuziping@yuanxin-inc.com']
 #           mail.sendmail(subject,content,smtp_to)


            return  json.dumps({'c ode':0,'result':"git操作成功"})
        except:
            logging.getLogger().error("get config error: %s" % traceback.format_exc())
            return json.dumps({'cod e':1,'errmsg':"写配置文件报错"})
    else:
         return json.dumps({'code':1,'errmsg':"获取用户，组或者仓库出错"})



