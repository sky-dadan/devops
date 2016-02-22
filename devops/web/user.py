#coding:utf-8
from flask import Flask, render_template,session,redirect,request
from  . import app        #导入__init__包文件中实例化的app，等价 from web import app
from db  import Cursor    #导入数据库连接模块
import util
import requests,json

headers = {'content-type': 'application/json'}
#个人中心web页面 
@app.route("/",methods=['GET'])
@app.route("/user/info",methods=['GET'])
def index():
    if session.get('username') == None:
        return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    return render_template('index.html',name=name)

##管理员添加用户web页面
@app.route("/user/add",methods=['GET','POST'])
def useradd():
    if session.get('username') == None:
        return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    return render_template('user_add.html',name=name)
 
#管理员查看用户列表web页面，
@app.route("/user/list",methods=['GET','POST'])
def user_list():
    if session.get('username') == None:
        return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    return render_template('user_list.html',name=name)


#管理员更新用户信息
@app.route("/user/update",methods=['GET','POST'])
def user_update():
    if session.get('usern ame') == None:
        return redirect('/login')
    headers['authorization'] = session['author']

    r_id = request.args.getlist('r_id')
    r_id=','.join(r_id) 
    if not r_id:
        return json.dumps({'code':1,'errmsg':'你必须选择一个所属组!'})

    kv = [(x, x) for x in ('id', 'username', 'name', 'email', 'mobile', 'role')] + [('is_lock', 'lock')]
    data = dict([(k, request.args.get(v)) for k,v in kv])
    data['r_id'] = r_id
    url = "http://%s/api/user" % app.config['api_host']
    r = requests.put(url, headers=headers,json=json.dumps(data))
    result = json.loads(r.content)
    return  json.dumps(result)

#角色列表web页面，数据走cmdb.py中统一的JSONRPC, 后期需要整合
@app.route("/role/list",methods=['GET','POST'])
def role_list():
    if session.get('username') == None :
        return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    return render_template('role_list.html',name=name)

#权限列表web页面，数据走cmdb.py统一的jsonrpc,冗余代码后期需要整合
@app.route('/power/list')
def power_list():
    if session.get('username') == None:
        return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    return render_template('power.html',name=name)

