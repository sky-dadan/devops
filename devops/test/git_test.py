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
        if int(result['code']) ==0:
            token=result['token']
            headers = {'content-type': 'application/json','authorization':token}
            print token 
        else:
            print  result
            return result
        '''
        # create请求
        data = {
                 'jsonrpc':'2.0',
                'method': 'git.create',      
                'id':'1',
                'params':{
                  'name':'EFEE',   
                  'path': 'admin',
                  'principal':'50',
                  'p_user':'50',
                  'p_group':'2',
                  'is_lock':'0',
                  'comment':'admin'  
                }
            }
        '''
        '''
        #getbyid请求
        data = {
                'jsonrpc':'2.0',
                'method': 'git.get',      
                'id':'1',
                'params':{
   #                 'output':['id','name','name_cn'],
                     'where':{'id':28}
                 }
        }
        '''
        '''
        #getlist请求
        data = {
                'jsonrpc':'2.0',
                'method': 'git.getlist',      
                'id':'30',
                'params':{
                   }
        }

        '''
        #update请求
        data = {
                'jsonrpc':'2.0',
                'method': 'git.update',      
                'id':'1',
                'params':{
                     'data':{'path':'test'},
                     'where':{'id':28}
                }
        }
       
        '''
        #delete请求
        data = {
                'jsonrpc':'2.0',
                'method': 'project.delete',      
                'id':'1',
                'params':{
                    'where':{'id':8}
                }
        }
        '''
     

        r = requests.post(url, headers=headers,json=data)

        print r.status_code
        print r.text  


rpc()
