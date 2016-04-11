#!/bin/env python
# -*- encoding: utf-8 -*-

from flask import Flask, request, session, redirect
from . import app
import logging, util
import json, traceback
import urllib2,hashlib


@app.route('/api/cdn',methods=['POST'])
def apicdn() :
    if session.get('author',"nologin")  == "nologin":
       return redirect('/login')
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))
    if int(validate_result['code']) != 0:
        return json.dumps(validate_result)

    USER = "yuanxin"
    PASS = "MiaoShou!2#4%"
    url = "http://wscp.lxdns.com:8080/wsCP/servlet/contReceiver"
    qs = {'username': USER, 'url': '', 'dir': ''}
    try:
        data = dict(request.form)
        #print data
        urls = data['urls'][0].split("\r\n")
        dirs = data['dirs'][0].split("\r\n")

        resource = ''
        #url刷新和dir刷新不能同时刷新，也不能同时为空
        if "http" not  in ''.join(urls)  and  "http"  not in ''.join(dirs): 
            logging.getLogger().error('urls and dirs is empty')
            return json.dumps({'code': 1, 'errmsg': "CDN刷新时，url和目录不能全为空"})
        elif "http" in ''.join(urls):
            resource += ';'.join([v.strip()  for v in urls])
            qs['url'] = ';'.join([v.strip()  for v in urls])
        elif "http" in ''.join(dirs):
            resource += ';'.join([v.strip()  for v in dirs])
            qs['dir'] = ';'.join([v.strip()  for v in dirs])

        hash_str = "%s%s%s" % (USER, PASS, resource)
        qs['passwd'] = hashlib.md5(hash_str).hexdigest()

        f = urllib2.urlopen(url, '&'.join(['%s=%s' % (k,v) for k,v in qs.items() if v]))
        res = f.read().strip()
        code = f.getcode()
        logging.getLogger().info('Push CDN (url:%s dir:%s), result: (%s) %s' % (qs['url'], qs['dir'], code, res))
        return json.dumps({"code": 0,"result":res})
    except:
        logging.getLogger().error("Push CDN error: %s" % traceback.format_exc())
        return json.dumps({"code":1,"errmsg":"CDN刷新失败"})

