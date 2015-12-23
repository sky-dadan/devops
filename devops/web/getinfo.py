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

@app.route('/idc',methods=['GET','POST'])
def idc():
    headers['authorization'] = session['author']
    data['method'] = 'idc.getlist'
    data['params'] = {'output':['id','idc_name']}
    r = requests.post(url,headers=headers,json=data)
    return r.text

@app.route('/cabinet',methods=['GET','POST'])
def cabinet():
    headers['authorization'] = session['author']
    data['method'] = 'cabinet.getlist'
    data['params'] = {'output':['id','name']}
    r = requests.post(url,headers=headers,json=data)
    return r.text

@app.route('/services',methods=['GET','POST'])
def services():
    headers['authorization'] = session['author']
    data['method'] = 'services.getlist'
    data['params'] = {'output':['id','name']}
    r = requests.post(url,headers=headers,json=data)
    return r.text

