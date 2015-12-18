#coding:utf-8
from flask import Flask, render_template,session,redirect,request
from  . import app  
import requests,json 
import util 

headers = {"Content-Type": "application/json"}
url = 'http://127.0.0.1:1000/api'
data = {
        "jsonrpc": "2.0",
        "id":1,
}

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
    r = requests.post(url,headers=headers,json=data)
    return r.text

@app.route('/addapi', methods=['GET','POST'])
def addapi():
    headers['authorization'] = session['author']
    method = request.args.get('method')
    method = request.form.get('method')
    formdata = request.form.get('formdata')  #str
    formdata = dict([x.split('=', ) for x in formdata.split('&')])  #dict
    data['method'] = method+".create"
    data['params']=formdata
    #print data
    r = requests.post(url,headers=headers,json=data)
    return r.text

@app.route('/getapi')
def getapi():
    headers['authorization'] = session['author']
    method = request.args.get('method')
    id  = int(request.args.get('id'))
    data['method'] = method+".get"
    data['params'] = {"where":{"id":id}}
    r = requests.post(url,headers=headers,json=data)
    return r.text


@app.route('/updateapi',methods=['GET','POST'])
def updateapi():
    headers['authorization'] = session['author']
    method = request.form.get('method')
    formdata = request.form.get('formdata')  #str
    formdata = dict([x.split('=', ) for x in formdata.split('&')])  #dict
    data['method'] = method+".update"
    data['params'] = {
        "data":formdata,
        "where":{
            "id":int(formdata['id'])
        }
    }
    print data
    r = requests.post(url, headers=headers, json=data)
    return r.content

@app.route('/deleteapi')
def deleteapi():
    headers['authorization'] = session['author']
    method = request.args.get('method')
    id  = int(request.args.get('id'))
    data['method'] = method+".delete"
    data['params'] = {"id":id}
    r = requests.post(url,headers=headers,json=data)
    return r.text


