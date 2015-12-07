#coding:utf-8
from flask import Flask, render_template,session,redirect,request
from  . import app  #导入__init__包文件中实例化的app，等价 from web import app
from db  import Cursor    #导入数据库连接模块
import util
import requests,json

headers = {'content-type': 'application/json'}
##   for user 
@app.route("/",methods=['GET'])
@app.route("/user/info",methods=['GET'])
def index():
    if session.get('username') == None:
       return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    url = "http://192.168.1.243:2000/api/user"
    r = requests.get(url, headers=headers)      
    result = json.loads(r.content)
    if int(result['code']) == 0:
        return render_template('index.html',name=name,result=result['user'])
    else:
        return render_template('index.html')

@app.route("/user/passwd",methods=['GET','POST'])
def change_passwd():
    if session.get('username') == None:
       return redirect('/login')
    return render_template('change_passwd.html')

@app.route("/user/edit",methods=['GET','POST'])
def user_edit():
    if session.get('username') == None:
       return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    url = "http://192.168.1.243:2000/api/user"
    r = requests.get(url, headers=headers)      
    result = json.loads(r.content)
    if int(result['code']) == 0:
        return render_template('user_edit.html',name=name,user=result['user'])
    else:
        return render_template('user_edit.html')

##  for admin
@app.route("/user/add",methods=['GET','POST'])
def user_add():
    if session.get('username') == None:
        return redirect('/login')
    return render_template('user_add.html')

@app.route("/user/useradd",methods=['GET','POST'])
def useradd():
    if session.get('username') == None:
        return redirect('/login')

    headers['authorization'] = session['author']
    role = int(request.args.get('role'))
    username = request.args.get('username')
    name = request.args.get('user_name')
    email = request.args.get('user_mail')
    mobile = request.args.get('user_phone')
    is_lock = int(request.args.get('lock'))
    password = request.args.get('user_pwd')
    user_repwd = request.args.get('user_repwd')

    data = {'role':role,'username':username,'name':name,'email':email,'mobile':mobile,'is_lock':is_lock,'password':password}
    url = "http://192.168.1.243:2000/api/user"
    r = requests.post(url,headers=headers,json=json.dumps(data))
    return r.content
    
@app.route("/user/list",methods=['GET','POST'])
def user_list():
    if session.get('username') == None:
       return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    url = "http://192.168.1.243:2000/api/user?list=true"
    r = requests.get(url, headers=headers)      
    result = json.loads(r.content)
    if int(result['code']) == 0:
        return render_template('user_list.html',name=name,users=result['users'])
    else:
        return render_template('user_list.html')

@app.route("/getbyid",methods=['GET','POST'])
def getbyid():
    if session.get('username') == None:
    	return redirect('/login')
    id = int(request.args.get('id'))     
    if not id:
    	return "need an id"
    headers['authorization'] = session['author']
    url = "http://192.168.1.243:2000/api/user/getbyid/%d" % id
    r = requests.get(url, headers=headers)      
    result = json.loads(r.content)
    return json.dumps(result)

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

    data = {'user_id':user_id,'username':username,'name':name,'email':email,'mobile':mobile,'role':role,'is_lock':is_lock}
    url = "http://192.168.1.243:2000/api/user"
    r = requests.put(url, headers=headers,json=json.dumps(data))
    result = json.loads(r.content)
    return json.dumps(result)

@app.route("/user/updateoneself",methods=['GET','POST'])
def updateoneself():
    if session.get('username') == None:
       return redirect('/login')
    headers['authorization'] = session['author']
    name = request.args.get('user_name') 
    email = request.args.get('user_email')
    mobile = request.args.get('user_mobile')
    data = {'name':name,'email':email,'mobile':mobile}
    print data
    url = "http://192.168.1.243:2000/api/user"
    r = requests.put(url,headers=headers,json=json.dumps(data))
    return r.content

@app.route("/user/changepasswd",methods=['GET','POST'])
def changepasswd():
    if session.get('username') == None:
       return redirect('/login')
    headers['authorization'] = session['author']
    user_id = int(request.args.get('passwdid'))
    password = request.args.get('changepasswd')
    data = {'user_id':user_id,'password':password}
    url = "http://192.168.1.243:2000/api/password"
    r = requests.put(url, headers=headers,json=json.dumps(data))
    result = json.loads(r.content)
    return json.dumps(result)

@app.route("/user/chpwdoneself",methods=['GET','POST'])
def chpwdoneself():
    if session.get('username') == None:
       return redirect('/login')
    headers['authorization'] = session['author']
    oldpasswd = request.args.get('oldpasswd')
    newpasswd = request.args.get('newpasswd')
    data = {'oldpassword':oldpasswd,'password':newpasswd}
    print data
    url = "http://192.168.1.243:2000/api/password"
    r = requests.put(url, headers=headers,json=json.dumps(data))
    result = json.loads(r.content)
    return json.dumps(result)

