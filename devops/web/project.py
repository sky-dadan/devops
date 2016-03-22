#coding:utf-8
from __future__ import unicode_literals
from flask import Flask, render_template,session,redirect,request
from  . import app  
import requests,json 
import util,urllib

headers = {'content-type': 'application/json'}
@app.route('/project/apply')
def project_apply():
    if session.get('username',"nologin")  == "nologin":
       return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    if int(validate_result['code']) == 0:
        url = "http://%s/api/userproject" % app.config['api_host']
        r = requests.post(url, headers=headers)
        print type(r.text)
        print r.text
        return render_template('apply.html',info=session)
    else:
        return render_template('apply.html',errmsg=validate_result['errmsg'])
