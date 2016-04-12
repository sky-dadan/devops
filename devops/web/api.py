#coding:utf-8
from flask import Flask, render_template,session,redirect,request
from  . import app        #导入__init__包文件中实例化的app，等价 from web import app
from db  import Cursor    #导入数据库连接模块
import util
import requests,json
import logging, urllib2, hashlib

headers = {'content-type': 'application/json'}
#所有api的web页面展示文件 

def post_cdn():
    USER = "yuanxin"
    PASS = "MiaoShou!2#4%"
    url = "http://wscp.lxdns.com:8080/wsCP/servlet/contReceiver"
    qs = {'username': USER}
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
        if "http" in ''.join(urls):
            resource += ';'.join([v.strip()  for v in urls])
            qs['url'] = ';'.join([v.strip()  for v in urls])
        if "http" in ''.join(dirs):
            resource += ';'.join([v.strip()  for v in dirs])
            qs['dir'] = ';'.join([v.strip()  for v in dirs])

        hash_str = "%s%s%s" % (USER, PASS, resource)
        qs['passwd'] = hashlib.md5(hash_str).hexdigest()

        f = requests.post(url, qs)
        logging.getLogger().info('Push CDN (url:%s dir:%s), result: (%s) %s' % (qs.get('url', ''), qs.get('dir', ''), f.status_code, f.text))
        return json.dumps({"code": 0,"result":f.text})
    except:
        logging.getLogger().error("Push CDN error: %s" % traceback.format_exc())
        return json.dumps({"code":1,"errmsg":"CDN刷新失败"})

@app.route("/cdn",methods=['GET','POST'])
def cdn():
    if session.get('author','nologin') == 'nologin':
        return redirect('/login')
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))

    if request.method == 'GET':
        if int(validate_result['code']) == 0:
            return render_template('cdn.html',info=session)
        else:
            return render_template('cdn.html',errmsg=validate_result['errmsg'])
    elif request.method == 'POST':
        return post_cdn()

@app.route("/dbreset", methods=['GET', 'POST'])
def dbreset():
    if session.get('author','nologin') == 'nologin':
        return redirect('/login')
    headers['authorization'] = session['author']
    validate_result = json.loads(util.validate(session['author'], app.config['passport_key']))

    if request.method == 'GET':
        if int(validate_result['code']) == 0:
            return render_template('dbreset.html',info=session)
        else:
            return render_template('dbreset.html',errmsg=validate_result['errmsg'])
