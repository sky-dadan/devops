#coding:utf-8
from flask import Flask,request,session,render_template,redirect
from  . import app  
import requests,json,urllib 
import util 

headers = {'content-type': 'application/json'}

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('user_mail')
        password = request.form.get('user_pwd')
        url = "http://%s/api/auth?%s" % (app.config['api_host'],urllib.urlencode({'username': username, 'passwd': password}))
        r = requests.get(url, headers=headers)      #for get all user
        result = json.loads(r.content)
        if result['code'] == 0:
            token = result["authorization"]
            res = util.validate(token,app.config['passport_key'])  #返回json对象
            res = json.loads(res)                        #return : dict(username:*,uid:*,role:*)
            session['author'] = token
            session['fix_pwd'] = app.config['passport_key']
            session['first_login'] = result['first_login']
    	    return json.dumps({'code':0})
        else:
            return json.dumps({'code':1,'errmsg':result['errmsg']})
    return render_template('login.html')

@app.route("/logout",methods=['GET','POST'])
def logout():
    try:
        session.pop('author')
        return redirect('/login')  
    except:
        return redirect('/login')  
