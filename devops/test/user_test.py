#!/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import json
import requests

url = "http://127.0.0.1:1000/api"
#登录并获取token
def login(username,password):
        rep_url = "%s/auth?username=%s&passwd=%s" % (url,username,password)
        r = requests.get(rep_url)      
        result = json.loads(r.content)
        if result['code'] == 0:
            token = result["authorization"]
            return json.dumps({'code':0,'token':token})
        else: 
            return json.dumps({'code':1,'errmsg':result['errmsg']})

def rpc():
        res=login('liuziping','123456')
        result = json.loads(res)
        if result['code'] ==0:
            token=result['token']
            headers = {'content-type': 'application/json','authorization':token}
            print token
        else:
            return result
        #getlist请求
        data = {
                'jsonrpc':'2.0',
                'method': 'user_perm.getlist',      
                'id':'1',
                'params':{
                }
        }
        '''
        #getinfo请求
        data = {
                'jsonrpc':'2.0',
                'method': 'user.getinfo',      
                'id':'1',
                'params':{
                }
        }
        '''
        r = requests.post(url, headers=headers,json=data)

        print r.status_code
        print r.text  


rpc()
