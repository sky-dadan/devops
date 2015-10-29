#coding:utf-8
from flask import Flask, render_template
from  . import app  #导入__init__包文件中实例化的app，等价 from web import app
from db  import Cursor    #导入数据库连接模块

@app.route("/",methods=['GET'])
def index():
    name = "liuziping"
    return render_template('index.html',name=name)


