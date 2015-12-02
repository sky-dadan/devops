#coding:utf-8
from flask import Flask,request,session,render_template,redirect
from  . import app  
from db  import Cursor    #导入数据库连接模块
import requests,json 

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
            session['author'] = result["authorization"]
            return redirect('/')
        else:
            return redirect('/login')
    return render_template('login.html')


