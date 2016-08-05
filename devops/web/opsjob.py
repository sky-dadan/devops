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
