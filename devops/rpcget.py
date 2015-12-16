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
        'method': 'cabinet.get',      
        'id':'1',
        'params':{
            'output' : ['id','name','power'],   #可选参数，返回指定列，不写或者为空时则返回所有列
            'limit' : 5,                        #可选参数，后台暂不处理
            'where' : {'id':1},                 #选择单条记录时必选，
            'order_by': 'id desc'               #可选参数，后台暂不处理
        }

}

r = requests.post(url, headers=headers,json=data)

print r.status_code
print r.text
#print json.loads(r.text)
