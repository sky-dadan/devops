#coding:utf-8
from flask import Flask, render_template,session,redirect,request
from  . import app  
from db  import Cursor  
import util
import requests,json

data = {
        'jsonrpc':'2.0',
        'id':'1',
        }

headers = {'content-type': 'application/json'}
@app.route("/host",methods=['GET'])
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


