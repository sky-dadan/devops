#coding:utf-8
import json
import logging
import traceback

import util

from flask import Flask, request
from . import app             #等价 from api import app
dic={}
@app.route("/api/islocked/<username>",methods=['GET', 'PUT'])
def is_locked(username):
    sql='select is_lock from user where username = "%s"' % username
    app.config['cursor'].execute(sql)
    row = app.config['cursor'].fetchone()
    dic['name']= row[0]
    return json.dumps(dic)
