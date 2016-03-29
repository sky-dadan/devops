#coding:utf-8
from __future__ import unicode_literals
from flask import Flask, render_template,session,redirect,request
from  . import app  
import requests,json 
import util,urllib

headers = {"Content-Type": "application/json"}
data = {
        "jsonrpc": "2.0",
        "id":1,
}

def get_url():
    return "http://%s/api" % app.config['api_host']

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


@app.route('/cmdb/<template>')
def render(template):
    if session.get('author','nologin')  == 'nologin':
       return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    if int(validate_result['code']) == 0:
        return render_template(template+'.html',info=session)
    else:
        return render_template(template+'.html',errmsg=validate_result['errmsg'])

@app.route('/listapi')
def listapi():
    headers['authorization'] = session['author']
    method = request.args.get('method')
    data['method'] = method+".getlist"
    data['params'] = {}
    r = requests.post(get_url(),headers=headers,json=data)
    return r.text 

@app.route('/addapi', methods=['GET','POST'])
def addapi():
    headers['authorization'] = session['author']
    method = request.args.get('method')
    method = request.form.get('method')
    formdata = request.form.get('formdata')  #str
    print repr(formdata)          #flask默认解码为unicode格式如： u'id=13&name=aa&remark=%E4%BD%A0%E5%A5%BD' 中文部分python无法解析 
    try:
        formdata = urllib.unquote(formdata).encode('iso-8859-1') #
        #print repr(formdata)          #解码后中文为utf8格式： u'id=13&name=aa&remark==\xe4\xbd\xa0\xe5\xa5\xbd' 
    except:
       pass
    formdata = Handleformdata(formdata)
    data['method'] = method+".create"
    data['params']=formdata
    r = requests.post(get_url(),headers=headers,json=data)
    return r.text

@app.route('/getapi')
def getapi():
    headers['authorization'] = session['author']
    method = request.args.get('method')
    selected = request.args.get('selected',None)						#为后面的selected接口的统一，增加一个参数
    username = request.args.get('username',session['username']) #获取的是url传过来的username,如果没有取session
    uid = request.args.get('id')
    where = {'username':username} if uid is None else {'id': uid}
    data['params'] = {'selected': selected, 'where': where, 'args': request.args}
    data['method'] = method+".get"
    print data 
    r = requests.post(get_url(),headers=headers,json=data)
    print r.text
    return r.text


@app.route('/updateapi',methods=['GET','POST'])
def updateapi():
    headers['authorization'] = session['author']
    method = request.form.get('method')
    formdata = request.form.get('formdata')  #str
    try:
        formdata = urllib.unquote(formdata).encode('iso-8859-1')
    except:
       pass
    formdata = Handleformdata(formdata)
    data['method'] = method+".update"
    data['params'] = {
        "data":formdata,
        "where":{
            "id":int(formdata['id'])
        }
    }
    print data
    r = requests.post(get_url(), headers=headers, json=data)
    return r.content

@app.route('/deleteapi')
def deleteapi():
    headers['authorization'] = session['author']
    method = request.args.get('method')
    id  = int(request.args.get('id'))
    data['method'] = method+".delete"
    data['params'] = {"id":id}
    r = requests.post(get_url(),headers=headers,json=data)
    return r.text

