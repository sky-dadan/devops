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
    if  session.get('author','nologin') == 'nologin':
        return redirect('/login')
    headers['authorization'] = session['author']
    url = "http://%s/api" % app.config['api_host']
    data = {'jsonrpc': '2.0', 'id': 1, 'method': 'user.getinfo'}
    req = requests.post(url, headers=headers, json=data)
    result = json.loads(json.loads(req.content).get('result', '{}'))
    if result['code'] == 0:
        user = result['user']
        session['role'] = user['role']
        session['group'] = user['r_id']
        session['perm'] = user['p_id'].keys()
        session['username'] = user['name'] if user['name'] else user['username']

        user['groups'] = ','.join(user['r_id'])
        user['perm'] = ','.join(['<a href="%s" style="color:blue">%s</a>' % (x['url'], x['name_cn']) for x in user['p_id'].values()])

        return render_template('index.html',info=session,user=user)
    else:
        return redirect('/login')

##管理员添加用户web页面
@app.route("/user/add",methods=['GET','POST'])
def useradd():
    if  session.get('author','nologin') == 'nologin':
        return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    if int(validate_result['code']) == 0:
        return render_template('user_add.html',info=session)
    else:
        return render_template('user_add.html',errmsg=validate_result['errmsg'])
 
#管理员查看用户列表web页面，
@app.route("/user/list",methods=['GET','POST'])
def user_list():
    if  session.get('author','nologin') == 'nologin':
        return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    if int(validate_result['code']) == 0:
        return render_template('user_list.html',info=session)
    else:
        return render_template('user_list.html',errmsg=validate_result['errmsg'])


#角色列表web页面
@app.route("/role/list",methods=['GET','POST'])
def role_list():
    if  session.get('author','nologin') == 'nologin':
        return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    if int(validate_result['code']) == 0:
        return render_template('role_list.html',info=session)
    else:
        return render_template('role_list.html',errmsg=validate_result['errmsg'])

#权限列表web页面
@app.route('/power/list')
def power_list():
    if  session.get('author','nologin') == 'nologin':
        return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    if int(validate_result['code']) == 0:
        return render_template('power.html',info=session)
    else:
        return render_template('power.html',errmsg=validate_result['errmsg'])

#管理员修改用户密码
@app.route("/user/changepasswd",methods=['GET','POST'])
def changepasswd():
    if  session.get('author','nologin') == 'nologin':
        return redirect('/login')
    headers['authorization'] = session['author']
    if request.method == 'POST':
        user_id = int(request.form.get('passwdid'))
        password = request.form.get('changepasswd')
        data = {'user_id':user_id,'password':password}
        url = "http://%s/api/password" % app.config['api_host']
        r = requests.put(url, headers=headers,json=data)
        result = json.loads(r.content)
        return json.dumps(result)

#用户修改个人密码
@app.route("/user/chpwdoneself",methods=['GET','POST'])
def chpwdoneself():
    if  session.get('author','nologin') == 'nologin':
        return redirect('/login')
    headers['authorization'] = session['author']
    if request.method == 'POST':
        oldpasswd = request.form.get('oldpasswd')
        newpasswd = request.form.get('newpasswd')
        data = {'oldpassword':oldpasswd,'password':newpasswd}
        url = "http://%s/api/password" % app.config['api_host']
        r = requests.put(url, headers=headers,json=data)
        result = json.loads(r.content)
        return json.dumps(result)

