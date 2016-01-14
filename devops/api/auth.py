#coding:utf-8
import json
import logging
import traceback

import util

from flask import Flask, request
from . import app

def auth_login(func):
    def wrapper(*arg, **args):
        try:
            authorization = request.headers.get('authorization', 'None')
            res = util.validate(authorization, app.config['passport_key'])
            res = json.loads(res)
            if int(res['code']) == 1:
                logging.getLogger().warning("Request forbiden:%s" % res['errmsg'])
                return json.dumps({'code': 1, 'errmsg': '%s' % res['errmsg']})
        except:
            logging.getLogger().warning("Validate error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'User validate error'})
        return func(res, *arg, **args)
    wrapper.__name__ = '%s_wrapper' % func.__name__
    return wrapper

