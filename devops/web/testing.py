#coding:utf-8
from __future__ import unicode_literals
from flask import Flask, render_template,session,redirect,request
from  . import app
import requests,json
import util,urllib
import public
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
#        url = "http://%s/api/userproject" % app.config['api_host']
#        r = requests.post(url, headers=headers)
#        result = json.loads(r.text)
        data['method'] = "userproject.getlist"
        data['params'] = {}
        r = requests.post(public.get_url(),headers=headers,json=data)
        result = json.loads(r.text)
        result = json.loads(result['result'])
        print "testing result = ",result

        data['method'] ="test_host.getlist"
        data['params'] = {}
        r = requests.post(public.get_url(),headers=headers,json=data)
        resip = json.loads(r.text)
        resip = json.loads(resip['result'])

        if int(result['code']) == 0 and int(resip['code']) == 0:
            return render_template('testing.html',info=session,result=result['result'],resip=resip['result'])
        else:
            return render_template('testing.html',errmsg=validate_result['errmsg'])


@app.route('/project/testhistory')
def testhistory():
    if  session.get('author','nologin') == 'nologin':
        return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    name = session['username']
    project_id = request.args.get('id')
    project_id = urllib.unquote(project_id).encode('iso-8859-1')
    project_id = int(project_id) 
    if int(validate_result['code']) == 0:
        data['method'] ="project_test.getlist"
        data['params'] = {'where':{'project_id':project_id}}
        r = requests.post(public.get_url(),headers=headers,json=data)
        result = json.loads(r.text)
        result = json.loads(result['result'])
        if int(result['code']) == 0:
            return render_template('test_history.html',info=session,result=result['result'])
        else:
            return render_template('testhistory.html',errmsg=validate_result['errmsg'])
