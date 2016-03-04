#!/bin/env python
# -*- encoding: utf-8 -*-

from flask import Flask, request
from . import app
import logging, util
import json, traceback
import urllib2,hashlib


@app.route('/api/cdn',methods=['POST'])
def apicdn() :
    USER = "yuanxin"
    PASS = "MiaoShou!2#4%"
    url = "http://wscp.lxdns.com:8080/wsCP/servlet/contReceiver"
    hash_str = ""
    qs = {}
    qs['username'] = USER
    resource = ''
    try:
	data = dict(request.form)
        #print data
        urls = data['urls'][0].split("\r\n")
        dirs = data['dirs'][0].split("\r\n")

        #url刷新和dir刷新不能同时刷新，也不能同时为空
        if "http" not  in ''.join(urls)  and  "http"  not in ''.join(dirs): 
            print "not null all"
        if "http" in ''.join(urls) and "http" not  in ''.join(dirs):
            resource = ';'.join(["%s" % v.strip()  for v in urls])
            qs['url']=resource
        if "http" in ''.join(dirs) and "http" not in ''.join(urls):
            resource = ';'.join(["%s" % v.strip()  for v in dirs])
            qs['dir']=resource

	hash_str = "%s%s%s" % (USER, PASS, resource)
	qs['passwd'] = hashlib.md5(hash_str).hexdigest()
        #print qs

	f = urllib2.urlopen(url, '&'.join(['%s=%s' % (k,v) for k,v in qs.items()]))
	res = f.read().strip()
        code = f.getcode()
        print "Push CDN:%s: [%s]" % (code,res)
        return json.dumps({"code":code,"result":res})
    except:
        logging.getLogger().error("刷新程序有问题: %s" % traceback.format_exc())
        return json.dumps({"code":1,"errmsg":"程序报错"})

