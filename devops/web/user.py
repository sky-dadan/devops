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
    url = "http://192.168.1.243:1000/api/user"
    r = requests.get(url, headers=headers)      
    result = json.loads(r.content)
    if int(result['code']) == 0:
        return render_template('index.html',name=name,result=result['user'])
    else:
        return redirect('/login')

#修改个人密码
@app.route("/user/passwd",methods=['GET','POST'])
def change_passwd():
    if session.get('username') == None:
       return redirect('/login')
    return render_template('change_passwd.html')

#获取个人信息，为后面的编辑获取数据,需要和管理员获取信息合并
@app.route("/user/edit",methods=['GET','POST'])
def user_edit():
	if session.get('username') == None:
	   return redirect('/login')
	headers['authorization'] = session['author']
	name = session['username']
	url = "http://192.168.1.243:1000/api/user"
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
    if request.method == 'POST':
        role = int(request.form.get('role'))
        username = request.form.get('username')
        name = request.form.get('user_name')
        email = request.form.get('user_mail')
        mobile = request.form.get('user_phone')
        is_lock = int(request.form.get('lock'))
        password = request.form.get('user_pwd')
        user_repwd = request.form.get('user_repwd')
        r_id = request.form.getlist('r_id')     #获取多一个属性r_id的多个值，保存为列表
        r_id = ','.join(r_id)
        if len(r_id) == 0:
            return json.dumps({'code':1,'errmsg':'你必须选择一个所属组!!!'})
        data = {'role':role,'r_id':r_id,'username':username,'name':name,'email':email,'mobile':mobile,'is_lock':is_lock,'password':password}
        url = "http://192.168.1.243:1000/api/user"
        r = requests.post(url,headers=headers,json=json.dumps(data))
        return r.content
    else:
        return render_template('user_add.html',name=name)
 
#管理员查看用户列表
@app.route("/user/list",methods=['GET','POST'])
def user_list():
    if session.get('username') == None:
       return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    url = "http://192.168.1.243:1000/api/user?list=true"
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
	url = "http://192.168.1.243:1000/api/user/getbyid/%d" % id
	r = requests.get(url, headers=headers)      
	result = json.loads(r.content)
	return json.dumps(result)

#管理员更新用户信息
@app.route("/user/update",methods=['GET','POST'])
def user_update():
    if session.get('username') == None:
       return redirect('/login')
    headers['authorization'] = session['author']

    user_id = int(request.args.get('id'))
    name = request.args.get('name')
    username = request.args.get('username')
    email = request.args.get('email')
    mobile = request.args.get('mobile')
    role = int(request.args.get('role'))
    is_lock = int(request.args.get('lock'))
    r_id = request.args.getlist('r_id')
    r_id=','.join(r_id) 

    data = {'user_id':user_id,'username':username,'name':name,'email':email,'mobile':mobile,'role':role,'r_id':r_id,'is_lock':is_lock}
    url = "http://192.168.1.243:1000/api/user"
    r = requests.put(url, headers=headers,json=json.dumps(data))
    result = json.loads(r.content)
    return  json.dumps(result)

#用户更新个人信息
@app.route("/user/updateoneself",methods=['GET','POST'])
def updateoneself():
    if session.get('username') == None :
       return redirect('/login')
    headers['authorization'] = session['author']
    name = request.args.get('user_name') 
    email = request.args.get('user_email')
    mobile = request.args.get('user_mobile')
    data = {'name':name,'email':email,'mobile':mobile}
    url = "http://192.168.1.243:1000/api/user"
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
        url = "http://192.168.1.243:1000/api/password"
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
        url = "http://192.168.1.243:1000/api/password"
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
    url = "http://192.168.1.243:1000/api/user"
    data = {"user_id":user_id}
    r = requests.delete(url, headers=headers,json=json.dumps(data))
    result = json.loads(r.content)
    return json.dumps(result)

#角色列表
@app.route("/role/list",methods=['GET','POST'])
def role_list():
    if session.get('username') == None :
       return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    return render_template('role_list.html',name=name)

#权限列表
@app.route("/power/user", methods=['GET','POST'])
def power_user():
	if session.get('username')== None:
	    return redirect('/login')
	headers['authorization'] = session['author']
	name = session['username']
	return render_template('user_power.html',name=name)