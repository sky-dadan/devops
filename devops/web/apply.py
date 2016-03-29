#coding:utf-8
from __future__ import unicode_literals
from flask import Flask, render_template,session,redirect,request
from  . import app
import requests,json
import util,urllib
import datetime
import logging
from public import get_url

headers = {"Content-Type": "application/json"}
data = {
        "jsonrpc": "2.0",
        "id":1,
}
#申请发布页面
@app.route('/project/apply')
def project_apply():
    if session.get('author',"nologin")  == "nologin":
       return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    if int(validate_result['code']) == 0:
        url = "http://%s/api/userproject" % app.config['api_host']
        r = requests.post(url, headers=headers)
        result = json.loads(r.text)
        if int(result['code']) == 0:
            return render_template('apply.html',info=session,result=result['result'])
        else:
            return render_template('apply.html',info=session,result=result['errmsg'])
    else:
        return render_template('apply.html',errmsg=validate_result['errmsg'])

#申请任务列表
@app.route('/project/applylist')
def apply_list():
    if  session.get('author','nologin') == 'nologin':
       return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    name = session['username']
    if int(validate_result['code']) == 0:
        return render_template('applylist.html',info=session)
    else:
        return render_template('applylist.html',errmsg=validate_result['errmsg'])


@app.route('/apply/emulation',methods=['GET','POST'])
def emulation():
    if  session.get('author','nologin') == 'nologin':
       return redirect('/login')
    headers['authorization'] = session['author']
    version = request.form.get('version')
    id = request.form.get('id')
    data['params'] = {'version':version,'id':id}
    data['method'] = 'apply.emulation'
    r = requests.post(get_url(),headers=headers,json=data)
    return r.text

@app.route('/apply/cancel')
def cancel():
    if  session.get('author','nologin') == 'nologin':
       return redirect('/login')
    headers['authorization'] = session['author']
    id = request.args.get('id')
    data['params'] = {'where':{'id':id}}
    data['method'] = 'apply.cancel'
    r = requests.post(get_url(),headers=headers,json=data)
    return r.text


@app.route('/apply/success')
def success():
    if  session.get('author','nologin') == 'nologin':
       return redirect('/login')
    headers['authorization'] = session['author']
    id = request.args.get('id')
    data['params'] = {'where':{'id':id}}
    data['method'] = 'apply.success'
    r = requests.post(get_url(),headers=headers, json=data)
    return r.text   

@app.route('/project/uplist')
def deploy_list():
    if  session.get('author','nologin') == 'nologin':
       return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    name = session['username']
    if int(validate_result['code']) == 0:
        return render_template('deploylist.html',info=session,qs=request.args)
    else:
        return render_template('deploylist.html',errmsg=validate_result['errmsg'])

