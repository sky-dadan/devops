#!/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import json
import requests
def login(username,password):
    url = "http://192.168.1.243:1000/api/auth?username=%s&passwd=%s" % (username,password)
    r = requests.get(url)      #for get all user
    result = json.loads(r.content)
    if result['code'] == 0:
        token = result["authorization"]
        return json.dumps({'code':0,'token':token})
    else: 
        return json.dumps({'code':1,'errmsg':result['errmsg']})


res=login('zhangxunan','123456')
result = json.loads(res)
token=result['token']
headers = {'content-type': 'application/json','authorization':token}
url = "http://127.0.0.1:1000/api"
data = {
        'jsonrpc':'2.0',
        'method': 'cabinet.update',      
        'id':'1',
        'params':{
            'data' : {'name':'O04','idc_id':1,'u_num':320,'power':"20A"},
            'where' : {'id':1}
        }

}

r = requests.post(url, headers=headers,json=data)

print r.status_code
print r.text
#print json.loads(r.text)
