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
            authorization = request.headers.get('authorization', '')
            res = util.validate(authorization, app.config['passport_key'])
            if not res:
                logging.getLogger().warning("Request forbiden")
                return json.dumps({'code': 1, 'errmsg': 'User validate error'})
        except:
            logging.getLogger().warning("Validate error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'User validate error'})
        return func(res, *arg, **args)
    return wrapper

