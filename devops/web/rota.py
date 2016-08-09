#coding:utf-8
from __future__ import unicode_literals
from flask import Flask, render_template,session,redirect,request
from  . import app
import requests,json
import util,urllib
import public
from public import get_url
headers = {"Content-Type": "application/json"}
data = {
        "jsonrpc": "2.0",
        "id":1,
}

@app.route('/rota')
def rota():
    if  session.get('author','nologin') == 'nologin':
        return redirect('/login')
    session['pre_click'] = 'deploy'
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    if int(validate_result['code']) == 0:
        return render_template('rota.html',info=session)
    else:
        return render_template('rota.html',errmsg=validate_result['errmsg'])


@app.route('/getone')
def getone():
    headers['authorization'] = session['author']
    method = request.args.get('method')
    data['method'] = method+".get2"
    id = request.args.get('id')
    where = {'id': id}
    data['params'] = {'where': where, 'args': request.args}
    r = requests.post(get_url(),headers=headers,json=data)
    return r.text
