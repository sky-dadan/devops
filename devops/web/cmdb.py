#coding:utf-8
from flask import Flask, render_template,session,redirect,request
from  . import app  
import requests,json 
import util,urllib

headers = {"Content-Type": "application/json"}
url = 'http://127.0.0.1:1000/api'
data = {
        "jsonrpc": "2.0",
        "id":1,
}

def Handleformdata(formdata):
    res = {}
    for x in formdata.split('&'):
        if x.find('=') <= 0:
            continue
        k, v = x.split('=', 1)
        if k in res and isinstance(res[k], list):
            res[k].append(v)
        elif k in res:
            res[k] = [res[k], v]
        else:
            res[k] = v

    for k in res:
        if isinstance(res[k], list):
            res[k] = ','.join(res[k])
    return res

@app.route('/power/list')
def power_list():
    if session.get('username') == None:
       return redirect('/login')
    headers['authorization'] = session['author']
    name = session['username']
    return render_template('power.html',name=name)


@app.route('/cmdb/<template>')
def render(template):
    if session.get('username')  == None:
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
    r = requests.post(url,headers=headers,json=data)
    print r.text
    return r.text 

@app.route('/addapi', methods=['GET','POST'])
def addapi():
    headers['authorization'] = session['author']
    method = request.args.get('method')
    method = request.form.get('method')
    formdata = request.form.get('formdata')  #str
    formdata = urllib.unquote(formdata).encode('iso-8859-1', 'ignore')
    formdata = Handleformdata(formdata)
    data['method'] = method+".create"
    data['params']=formdata
    r = requests.post(url,headers=headers,json=data)
    return r.text

@app.route('/getapi')
def getapi():
    headers['authorization'] = session['author']
    method = request.args.get('method')
    username = request.args.get('username')
    uid = request.args.get('id')
    if uid is not None:
        data['params'] = {"where":{'id':uid}}
    else:
        data['params'] = {"where":{'username':username}}
    data['method'] = method+".get"
    r = requests.post(url,headers=headers,json=data)
    print r.text
    return r.text


@app.route('/updateapi',methods=['GET','POST'])
def updateapi():
    headers['authorization'] = session['author']
    method = request.form.get('method')
    formdata = request.form.get('formdata')  #str
    formdata = urllib.unquote(formdata).encode('iso-8859-1', 'ignore')
    formdata = Handleformdata(formdata)
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

