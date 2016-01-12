#!/bin/env python
# -*- encoding: utf-8 -*-

import json
import requests

import util

if __name__ == '__main__':
    s = util.get_validate('liuziping',1,0,'123456')
    headers = {'Authorization': s,'content-type': 'application/json'}
    data = {"username": "sa", "email": "sap@qq.com", "mobile": "11111", "name": "sa"}

 
   # select user info  or user list 
    url = "http://192.168.1.243:1000/api/user?offset=0&size=10&list=true" 
#    url = "http://192.168.1.243:1000/api/user" 
    r = requests.get(url, headers=headers)      #for get all user
    # update  create  delete user 
#    r = requests.put(url, headers=headers,json=json.dumps(data))
#    r = requests.post(url, headers=headers,json=json.dumps(data))  #for create user
#    data = {"user_id":9}
#    r = requests.delete(url, headers=headers,json=json.dumps(data)) #for delete one user

    # for change password
#    data = {"password":"123456","user_id":7}    #for  admin
#    data = {"oldpassword":"123456","password":"123456"}  #for user
#    url = "http://192.168.1.243:1000/api/password" 
#    r = requests.put(url, headers=headers,json=json.dumps(data))
    
    # for change role
#    data = {"role":0}
#    url = "http://192.168.1.243:1000/api/role/7" 
#    r = requests.put(url, headers=headers,json=json.dumps(data))

    print r.status_code
    print r.text
