#coding:utf-8
from flask import Flask, render_template,session,redirect,request
from  . import app        #导入__init__包文件中实例化的app，等价 from web import app
from db  import Cursor    #导入数据库连接模块
import util
import requests,json

headers = {'content-type': 'application/json'}
#获取个人信息 
@app.route("/",methods=['GET'])
@app.route("/user/info",methods=['GET'])
def index():
    if session.get('username') == None:
        return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    url = "http://%s/api/user" % app.config['api_host']
    r = requests.get(url, headers=headers)      
    result = json.loads(r.content)
    if int(result['code']) == 0:
        return render_template('index.html',name=name,result=result['user'])
    else:
        return redirect('/login')


#获取个人信息，为后面的编辑获取数据,需要和管理员获取信息合并
@app.route("/user/edit",methods=['GET','POST'])
def user_edit():
    if session.get('username') == None:
        return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    url = "http://%s/api/user" % app.config['api_host']
    r = requests.get(url, headers=headers)      
    result = json.loads(r.content)
    if int(result['code']) == 0:
        return render_template('user_edit.html',name=name,user=result['user'])
    else:
        return render_template('user_edit.html',name=name,errmsg=result['errmsg'])

##管理员添加用户
@app.route("/user/add",methods=['GET','POST'])
def useradd():
    if session.get('username') == None:
        return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    '''
    if request.method == 'POST':
        r_id = request.form.getlist('r_id')     #获取多一个属性r_id的多个值，保存为列表
        r_id = ','.join(r_id)
        if not r_id:
            return json.dumps({'code':1,'errmsg':'你必须选择一个所属组!'})
        kv = [('username', 'username'), ('name', 'user_name'), ('email', 'user_mail'), ('mobile', 'user_phone'), ('role', 'role'), ('is_lock', 'lock'), ('password', 'user_pwd')]
        data = dict([(k, request.form.get(v)) for k,v in kv])
        if len(data['password']) < 6:
            return json.dumps({'code':1, 'errmsg': '密码至少需要6位!'})
        elif data['password'] != request.form.get('user_repwd'):
            return json.dumps({'code':1, 'errmsg': '两次输入的密码不一致!'})
        data['r_id'] = r_id
        url = "http://%s/api/user" % app.config['api_host']

        r = requests.post(url,headers=headers,json=data)
        return r.content
    else:
    '''    
    return render_template('user_add.html',name=name)
 
#管理员查看用户列表
@app.route("/user/list",methods=['GET','POST'])
def user_list():
    if session.get('username') == None:
        return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    url = "http://%s/api/user?list=true" % app.config['api_host']
    r = requests.get(url, headers=headers)      
    result = json.loads(r.content)
    if int(result['code']) == 0:
        return render_template('user_list.html',name=name,users=result['users'])
    else:
        return render_template('user_list.html',errmsg=result['errmsg'])

#获取更新单条记录的信息
@app.route("/getbyid",methods=['GET','POST'])
def getbyid():
    if session.get('username') == None:
        return redirect('/login')
    id = int(request.args.get('id'))     
    headers['authorization'] = session['author']
    url = "http://%s/api/user/getbyid/%d" % (app.config['api_host'], id)
    r = requests.get(url, headers=headers)      
    result = json.loads(r.content)
    return json.dumps(result)

#管理员更新用户信息
@app.route("/user/update",methods=['GET','POST'])
def user_update():
    if session.get('username') == None:
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

#用户更新个人信息
@app.route("/user/updateoneself",methods=['GET','POST'])
def updateoneself():
    if session.get('username') == None :
        return redirect('/login')
    headers['authorization'] = session['author']
    data = dict([(x, request.args.get('user_%s' % x)) for x in ('name', 'email', 'mobile')])
    url = "http://%s/api/user" % app.config['api_host']
    r = requests.put(url,headers=headers,json=json.dumps(data))
    return r.content

#管理员修改用户密码
@app.route("/user/changepasswd",methods=['GET','POST'])
def changepasswd():
    if session.get('username') == None :
        return redirect('/login')
    headers['authorization'] = session['author']
    if request.method == 'POST':
        user_id = int(request.form.get('passwdid'))
        password = request.form.get('changepasswd')
        data = {'user_id':user_id,'password':password}
        url = "http://%s/api/password" % app.config['api_host']
        r = requests.put(url, headers=headers,json=json.dumps(data))
        result = json.loads(r.content)
        return json.dumps(result)

#用户修改个人密码
@app.route("/user/chpwdoneself",methods=['GET','POST'])
def chpwdoneself():
    if session.get('username') == None:
        return redirect('/login')
    headers['authorization'] = session['author']
    if request.method == 'POST':
        oldpasswd = request.form.get('oldpasswd')
        newpasswd = request.form.get('newpasswd')
        data = {'oldpassword':oldpasswd,'password':newpasswd}
        url = "http://%s/api/password" % app.config['api_host']
        r = requests.put(url, headers=headers,json=json.dumps(data))
        result = json.loads(r.content)
        return json.dumps(result)

#管理员删除用户
@app.route("/user/delete",methods=['GET','POST'])
def userdelete():
    if session.get('username') == None :
        return redirect('/login')
    headers['authorization'] = session['author']
    user_id = int(request.args.get('id'))
    url = "http://%s/api/user" % app.config['api_host']
    data = {"user_id":user_id}
    r = requests.delete(url, headers=headers,json=json.dumps(data))
    result = json.loads(r.content)
    return json.dumps(result)

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

