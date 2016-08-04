#!/usr/bin/env python
#coding:utf-8
from flask import Flask, render_template, session,redirect,request
from . import app
import json, requests,util
from public import get_url

headers = {"Content-Type":"application/json"}
data = {
        'jsonrpc':'2.0',
        'id':1
}

#工单申请页面
@app.route('/opsjob/apply', methods=['GET','POST'])
def opsjob_apply():
    if session.get('author','nologin') == 'nologin':
        return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    if int(validate_result['code']) == 0:
        return render_template('opsjob_add.html',info=session)
    else:
        return render_template('opsjob_add.html',errmsg=validate_result['errmsg'])


#申请，处理工单列表
@app.route('/opsjob/applist')
def opsjob_adeal():
    if session.get('author','nologin') == 'nologin':
        return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    if int(validate_result['code']) == 0:
        return render_template('opsjob_applist.html', info=session)
    else:
        return render_template('opsjob_applist.html',errmsg=validate_result['errmsg'])

#处理
@app.route('/opsjob/deal',methods=['POST'])
def opsjob_deal():
    if session.get('author','nologin') == 'nologin':
        return redirect('/login')
    headers['authorization'] = session['author']
    j_id = request.args.get('id')
    status = request.args.get('status')
    deal_desc = request.args.get('deal_desc',None)
    data['method'] = 'opsjob.update'
    data['params'] = {'where':{'id':j_id},'status':status,'deal_desc':deal_desc}
    print data
    r = requests.post(get_url(), headers=headers,json=data)
    return r.text

@app.route('/opsjob/history')
def opsjob_hisrtory():
    if session.get('author','nologin') == 'nologin':
        return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    if int(validate_result['code']) == 0:
        return render_template('opsjob_alllist.html', info=session)
    else:
        return render_template('opsjob_alllist.html',errmsg=validate_result['errmsg'])
