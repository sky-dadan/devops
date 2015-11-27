#coding:utf-8
from flask import Flask, render_template
from  . import app  #导入__init__包文件中实例化的app，等价 from web import app
from db  import Cursor    #导入数据库连接模块

@app.route("/",methods=['GET'])
@app.route("/accounts",methods=['GET'])
def index():
    name = "liuziping"
    return render_template('index.html',name=name)


@app.route("/accounts/edit",methods=['GET','POST'])
def user_edit():
    return render_template('edit.html')

@app.route("/accounts/add",methods=['GET','POST'])
def user_add():
    return render_template('add.html')
