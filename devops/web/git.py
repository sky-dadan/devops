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
@app.route('/git/list')
def git():
    if session.get('username')  == None:
       return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    name = session['username']
    if int(validate_result['code']) == 0:
        return render_template('git.html',name=name)
    else:
        return render_template('git.html',errmsg=validate_result['errmsg'])
