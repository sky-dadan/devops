#coding:utf-8
from flask import Flask, render_template
from  . import app  #导入__init__包文件中实例化的app，等价 from web import app
from db  import Cursor    #导入数据库连接模块

##   for user 
@app.route("/",methods=['GET'])
@app.route("/user/info",methods=['GET'])
def index():
    name = "liuziping"
    return render_template('index.html',name=name)

@app.route("/user/passwd",methods=['GET','POST'])
def change_passwd():
    return render_template('change_passwd.html')

@app.route("/user/edit",methods=['GET','POST'])
def user_edit():
    return render_template('user_edit.html')

##  for admin
@app.route("/user/add",methods=['GET','POST'])
def user_add():
    return render_template('user_add.html')


@app.route("/user/list",methods=['GET','POST'])
def user_list():
    return render_template('user_list.html')

