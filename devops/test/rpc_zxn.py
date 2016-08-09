#!/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import json
import requests

def login(username,password):
    url = "http://192.168.1.243:2000/api/auth?username=%s&passwd=%s" % (username,password)
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
url = "http://127.0.0.1:2000/api"
#data = {
#        'jsonrpc':'2.0',
#        'method': 'host.update',      
#        'id':'1',
#        'params':{
#            'id':1,
#            'hostname':'nginx1',   
#            'sn':'CN-0CNXC3-C1175-1CF-3419',
#            'host_no':1,
#            'inner_ip':'192.168.1.2',
#            'mac_address':'44:A8:42:39:F5:87',
#            'remote_ip':'192.168.1.66',
#            'os_info':'CentOS6.5',
#            'cpu_num':4,
#            'disk_num':2048,
#            'mem_num':64,
#            'host_type':'DELLR730',
#            'manufacturer_id':1,
#            'supplier_id':1,
#            'store_date':'2015-12-15 10:20:46',
#            'expire':'2018-12-15 10:20:46',
#            'idc_id':1,
#            'cabinet_id':1,
#            'service_id':1,
#            'status':0,
#            'vm_status':1,
#            'remark':'nginx1 proxy'
#        }
#
#}
#data = {
#        'jsonrpc':'2.0',
#        'method': 'rota.create',      
#        'id':'1',
#        'params':{
#            'start_date': '2016-09-06',
#            'end_date': '2016-09-12',
#            'man_on_duty': 'duminchao'
#        }
#    }
#
data = {
        'jsonrpc':'2.0',
        'method': 'rota.get',      
        'id':'1',
        'params':{'where':{'id':1}}
    }

#data = {
#        'jsonrpc': '2.0',
#        'method': 'rota.getlist',
#        'id': '1',
#        'params': {}
#        }
#data = {
#        'jsonrpc':'2.0',
#        'method': 'rota.update',      
#        'id':'1',
#        'params':{
#            'data' : {'id':2,'start_date':'2016-08-15', 'end_date': '2016-08-21', 'man_on_duty': 'zhangxunan'},
#            'where' : {'id':2}
#                }
#        }
#data = {'params': {'where': {'id': 3}, 'data': {'remark': 'dnsdfas', 'store_date': '2015-12-17', 'expire': '2018-12-17', 'type': 'dns', 'id': '3', 'manufacturer': 'dnspod'}}, 'jsonrpc': '2.0', 'id': 1,'method':'softassets.update'}


#
#data = {
#        'jsonrpc':'2.0',
#        'method': 'host.delete',      
#        'id':'1',
#        'params':{
#            'id':2,
#            'hostname':'nginx2'
#        }
#    }

#data = {
#        'jsonrpc':'2.0',
#        'method': 'softassets.create',      
#        'id':'1',
#        'params':{
#            'id':1,
#            'type':'dns',
#            'manufacturer':'dnspod',
#            'store_date':'2015-12-15 16:31:20',
#            'expire':'2018-12-15 16:31:20',
#            'remark':'dns'
#        }
#    }
#

#data = {
#        'jsonrpc':'2.0',
#        'method': 'softassets.update',      
#        'id':'1',
#        'params':{
#            'data' : {'id':3,'type':'dns','manufacturer':'dnspod','store_date':'2015-12-17 19:03:03','expire':"2018-12-17 19:03:03",'remark':'dns'},
#            'where' : {'id':3}
#        }
#        }
#data = {'params': {'where': {'id': 3}, 'data': {'remark': 'dnsdfas', 'store_date': '2015-12-17', 'expire': '2018-12-17', 'type': 'dns', 'id': '3', 'manufacturer': 'dnspod'}}, 'jsonrpc': '2.0', 'id': 1,'method':'softassets.update'}


#data = {
#        'jsonrpc':'2.0',
#        'method': 'softassets.getlist',      
#        'id':'1',
#        'params':{
#        }
#    }
#data = {
#        'jsonrpc':'2.0',
#        'method': 'softassets.delete',      
#        'id':'1',
#        'params':{
#            'id':2,
#            'type':'dns',
#            'manufacturer':'net',
#            'store_date':'2015-12-15 16:31:20',
#            'expire':'2018-12-15 16:31:20',
#            'remark':'domain'
#        }
#    }
#data = {
#        'jsonrpc':'2.0',
#        'method': 'switch.create',      
#        'id':'1',
#        'params':{
#            'id':2,
#            'name':'HUASAN',
#            'type':'layer2',
#            'idc_id':1,
#            'cabinet_id':2,
#            'port_num':10,
#            'status':0,
#            'remark':'HUASAN Switch'
#        }
#    }

#data = {
#        'jsonrpc':'2.0',
#        'method': 'switch.get',      
#        'id':'1',
#        'params':{
#            'output':['id','name','type'],
#            'where':{'id':2}
#        }
#    }

#data = {
#        'jsonrpc':'2.0',
#        'method': 'switch.getlist',      
#        'id':'1',
#        'params':{
##            'output':['id','name','type'],
##            'where':{'id':2}
#        }
#    }

#data = {
#        'jsonrpc':'2.0',
#        'method': 'switch.update',      
#        'id':'1',
#        'params':{
#            'id':2,
#            'name':'HUASAN',
#            'type':'layer3',
#            'idc_id':1,
#            'cabinet_id':3,
#            'port_num':10,
#            'status':0,
#            'remark':'HUASAN Switch'
#        }
#    }
#data = {
#        'jsonrpc':'2.0',
#        'method': 'switch.delete',      
#        'id':'1',
#        'params':{
#            'id':2,
#            'name':'HUASAN',
#        }
#    }
#

r = requests.post(url, headers=headers,json=data)

print r.status_code
print r.text
#print json.loads(r.text)
