#!/bin/env python
# -*- encoding: utf-8 -*-

import json
import requests

import util

if __name__ == '__main__':
    s = util.get_validate('test3', '123456')
    headers = {'Authorization': s,'content-type': 'application/json'}
    data = {'username': 'lzp', 'name': 'lzp', 'email': 'liuziping@123.com', 'mobile': '1234678'}
    # for get one user, update and delete user
    url = "http://192.168.1.243:1000/api/user/4" 
    #r = requests.get(url, headers=headers)     #for get one user
    r = requests.delete(url, headers=headers) #for delete one user
#    r = requests.put(url, headers=headers,json=json.dumps(data))
 
   # for get all user, create user
#    url = "http://192.168.1.243:1000/api/user" 
#    r = requests.get(url, headers=headers)      #for get all user
#    r = requests.post(url, headers=headers,data=json.dumps(data))  #for create user

    print r.status_code
    print r.text
