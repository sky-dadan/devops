#!/bin/env python
# -*- encoding: utf-8 -*-

import json
import httplib

import util

if __name__ == '__main__':
    s = util.get_validate('test3', 1, 1, '123456')
    headers = {'Authorization': s}

    conn = httplib.HTTPConnection('localhost', 1000)
    conn.request('GET', '/api', headers=headers)
    response = conn.getresponse()
    print response.read()

    data = {'username': 'mytest', 'name': '自测', 'email': 'mytest@123.com', 'mobile': '123467'}
    conn.request('PUT', '/api', json.dumps(data), headers)
    response = conn.getresponse()
    print response.read()

    users= {'user1': 'zhangxunan','user2':'lisi'}
    conn.request('PUT','/api/lock_user',json.dumps(users),headers)
    response = conn.getresponse()
    print response.read()

    group = {'groupname': 'sa','name_cn':'管理员','comment':'test','users':['zhangxunan','lisi']}
    conn.request('PUT','/api/groupadd',json.dumps(group),headers)
    response = conn.getresponse()
    print response.read()

    conn.request('GET','/api/querygroup',headers=headers)
    response = conn.getresponse()
    print response.read()
