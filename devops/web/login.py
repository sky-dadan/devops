#coding:utf-8
from flask import Flask,request,session,render_template,redirect
from  . import app  
from db  import Cursor    #导入数据库连接模块
import requests,json 
import util 

headers = {'content-type': 'application/json'}

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('user_mail')
        password = request.form.get('user_pwd')
        url = "http://%s/api/auth?username=%s&passwd=%s" % (app.config['api_host'],username,password)
        r = requests.get(url, headers=headers)      #for get all user
        result = json.loads(r.content)
        if result['code'] == 0:
            token = result["authorization"]
            res = util.validate(token,app.config['passport_key'])  #返回json对象
            res = json.loads(res)                        #return : dict(username:*,uid:*,role:*)
            #if int(res['role']) == 0:                   #针对管理员和普通用户的前端页面展示，已经通过前端代码处理，后端可忽略
            #    print "%s is admin" % res['username']
            #else:
            #    print "%s is user" % res['username']
            session['author'] = token
           # return redirect('/')
    	    return json.dumps({'code':0})
        else:
            #return redirect('/login')
            return json.dumps({'code':1,'errmsg':result['errmsg']})
    return render_template('login.html')

@app.route("/logout",methods=['GET','POST'])
def logout():
    session.pop('username',None)
    return redirect('/login')  
