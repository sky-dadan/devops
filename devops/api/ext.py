#!/usr/bin/env python
#coding: utf-8
from flask import Flask ,request
from flask_jsonrpc import JSONRPC
from . import app, jsonrpc
import os.path
import logging, util
from auth import auth_login
import json,traceback

@jsonrpc.method('dbreset.update')
@auth_login
def dbreset(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        name = kwargs['data'].get('id', '')
        if name not in ('mall', '100xhs', 'api', 'im', 'all'):
            return json.dumps({'code': 1, 'errmsg': "初始化的数据库不存在"})
        script_name = os.path.join(app.config['script_path'], 'init_db.sh')
        res, msg = util.run_script_with_timeout("%s %s" % (script_name, name), 3600)
        if res:
            util.write_log(username,"Init mysql '%s' success" % name)
            return json.dumps({'code':0,'result':"初始化数据库'%s'完成" % name})
        else:
            logging.getLogger().error("Init mysql '%s' error: %s" % (name, msg))
            return json.dumps({'code':1,'errmsg':'初始化数据库失败'})
    except:
        logging.getLogger().error("Init mysql '%s' error: %s"  % (name, traceback.format_exc()))
        return json.dumps({'code':1,'errmsg':'初始化数据库失败'})
