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
        url = "http://192.168.1.243:1000/api/auth?name=%s&passwd=%s" % (username,password)
        r = requests.get(url, headers=headers)      #for get all user
#        return r.content
        result = json.loads(r.content)
        if result['code'] == 0:
            token = result["authorization"]
            res = util.validate(token,app.config['passport_key'])  #返回json对象
            res = json.loads(res)  #return : dict(name:*,uid:*,role:*)
            if int(res['role']) == 0:                    #针对管理员和普通用户的前端页面展示，暂不处理
                print "%s is admin" % res['name']
            else:
                print "%s is user" % res['name']
            session['author'] = token
            session['username'] = res['name']
            return redirect('/')
        else:
            return redirect('/login')
    return render_template('login.html')

@app.route("/logout",methods=['GET','POST'])
def logout():
    session.pop('username',None)
    return redirect('/login')
