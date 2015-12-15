#coding:utf-8
from flask import Flask, render_template,session,redirect,request
from  . import app  
from db  import Cursor    #导入数据库连接模块
import requests,json 
import util 

data = {
        "jsonrpc": "2.0",
        "id":1,
        "auth":None,
}


headers = {"Content-Type": "application/json"}

@app.route('/cmdb/<template>')
def render(template):
    if session.get('username') == None:
       return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    return render_template(template+'.html',name=name)

@app.route('/listapi')
def listapi():
    headers['authorization'] = session['author']
    method = request.args.get('method')
    data['method'] = method+".getlist"
    data['params'] = {}
    print data
    url = 'http://127.0.0.1:1000/api'
    r = requests.post(url,headers=headers,json=data)
    print type(r.text)
    return r.text

@app.route('/addapi', methods=['POST'])
def addapi():
    print request.form
    data['params'] = request.form
    action_type = request.form.get('action_type')
    data['method'] = action_type+".create"
    print data
    url = 'http://127.0.0.1:1000/api'
    r = requests.post(url, headers=headers, json=data)
    return r.content


@app.route('/updateapi',methods=['POST'])
def updateapi():
    formdata = request.form.to_dict()
    # print formdata
    action_type = formdata.pop('action_type')
    # del request.form['action_type']
    data['method'] = action_type+".update"
    data['params'] = {
        "data":formdata,
        "where":{
            "id":request.form.get('id')
        }
    }
    print data
    url = 'http://127.0.0.1:1000/api'
    r = requests.post(url, headers=headers, json=json.dumps(data))
    return r.content



