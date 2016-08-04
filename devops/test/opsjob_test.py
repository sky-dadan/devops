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
        res=login('admin','123456')
        result = json.loads(res)
        if result['code'] ==0:
            token=result ['token']
            headers = {'content-type': 'application/json','authorization':token}
            print token
        else:
            return result

        # 创建工单
        '''
        data = {
        'jsonrpc':'2.0',
        'method': 'opsjob.create',      
        'id':'1',
        'params':{
            'apply_type':0,   
            'apply_desc':"just a test"
            }

        }
        '''
        # getlist请求,显示所有工单

        data = {
                'jsonrpc':'2.0',
                'method': 'opsjob.getlist',      
                'id':'1',
                'params':{
                    "condition":"apply"    # getlist可以接受一个条件参数
                }
        }
        # get请求,显示莫一条工单详情
        '''
        data = {
                'jsonrpc':'2.0',
                'method': 'opsjob.get',      
                'id':'1',
                'params':{
                    'where':{'id':63}
                }
        }
        '''
    
        # update请求,更新某一条工单记录
        '''
        data = {
                'jsonrpc':'2.0',
                'method': 'opsjob.update',      
                'id':'1',
                'params':{
                    'where':{'id':63},
                    'status':'3',
                    'deal_desc':"done"
                }
        }
        '''
        r = requests.post(url, headers=headers,json=data)

        print r.status_code
        print r.text  


rpc()
