#coding:utf-8
from flask import Flask, render_template,session,redirect,request
from  . import app        #导入__init__包文件中实例化的app，等价 from web import app
from db  import Cursor    #导入数据库连接模块
import util
import requests,json

headers = {'content-type': 'application/json'}
#所有api的web页面展示文件 
@app.route("/cdn",methods=['GET','POST'])
def cdn():
    if session.get('username') == None:
        return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    if int(validate_result['code']) == 0:
        return render_template('cdn.html',info=session)
    else:
        return render_template('cdn.html',errmsg=validate_result['errmsg'])
