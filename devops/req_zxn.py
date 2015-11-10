#!/bin/env python
# -*- encoding: utf-8 -*-

import json
import requests

import util

if __name__ == '__main__':
    s = util.get_validate('zhangxunan', '123456')
    headers = {'Authorization': s,'content-type': 'application/json'}
#    groups = {'name':'sa','name_cn':'guanliyuan','comment':'Test','users':['zhangxunan','lisi']}
#    group2 = {'name':'admin','name_cn':'guanliyuan2','comment':'Test2','users':['zhangxunan','liuziping']}
#    group3 = {'name':'admin3','name_cn':'guanliyuan3','comment':'Tes3','users':['zhangxunan','lisi']}
#    group4 = {'name':'PHP','name_cn':'PHP','comment':'PHP','users':['zhangxunan','liuziping']}
    uid = {'user_id':1}
#    url1 = "http://192.168.1.243:2000/api/group" 
#    r = requests.post(url1,headers=headers,data=json.dumps(group4))
#    g1 = requests.get(url1, headers=headers)     #for get one user
    
    url2 = "http://192.168.1.243:2000/api/lockuser/1"
    g2 = requests.get(url2,headers=headers)
    p2 = requests.put(url2,headers=headers,data=json.dumps(uid))
#    url3 = "http://192.168.1.243:2000/api/lockuser"
    
#    u2_g = requests.get(url,headers=headers)
#    u2_p = requests.get(url,headers=headers,data=json.dumps(uid))
#    url4 = "http://192.168.1.243:2000/api/group_detail/1"
#    g4 = requests.get(url4,headers=headers)
#    print r.status_code
#    print r.text
#    print g1.status_code
#    print g1.text
    print g2.status_code
    print g2.text
    print p2.status_code
    print p2.text
#    print g4.status_code
#    print g4.text

