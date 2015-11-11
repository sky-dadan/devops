#!/bin/env python
# -*- encoding: utf-8 -*-

import json
import httplib

import util

if __name__ == '__main__':
	s = util.get_validate('test3', '123456')
	headers = {'Authorization': s}

	conn = httplib.HTTPConnection('localhost', 1000)
	conn.request('GET', '/api', headers=headers)
	response = conn.getresponse()
	print response.read()

#    data = {'username': 'mytest', 'name': '自测', 'email': 'mytest@123.com', 'mobile': '123467'}
#    conn.request('PUT', '/api', json.dumps(data), headers)
#    response = conn.getresponse()
#    print response.read()
	data={'name':['test2','test1']}
	conn.request('DELETE','/api/group', json.dumps(data), headers)
	response=conn.getresponse()
	print response.read()
