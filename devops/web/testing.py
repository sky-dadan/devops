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

@app.route('/project/testing')
def testing():
    if  session.get('author','nologin') == 'nologin':
        return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    name = session['username']
    if int(validate_result['code']) == 0:
        url = "http://%s/api/userproject" % app.config['api_host']
        r = requests.post(url, headers=headers)
        result = json.loads(r.text)
        url = "http://%s/api/testhost" % app.config['api_host']
        r = requests.post(url,headers=headers)
        resip = json.loads(r.text)
        if int(result['code']) == 0 and int(resip['code']) == 0:
            print result
            print resip
            return render_template('testing.html',info=session,result=result['result'],resip = resip['result'])
        else:
            return render_template('testing.html',errmsg=validate_result['errmsg'])
