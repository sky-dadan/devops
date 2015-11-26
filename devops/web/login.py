#coding:utf-8
from flask import Flask,request,session,render_template,redirect
from  . import app  
from db  import Cursor    #导入数据库连接模块

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('user_mail')
        password = request.form.get('user_pwd')
        if username == "admin" and  password=="13456":
            session['username'] = username
            return redirect('/')
        else:
            return redirect('/login')
    return render_template('login.html')


