#coding:utf-8
import json
import logging
import util

from flask import Flask
from . import app             #等价 from api import app

@app.route("/api",methods=['GET'])
def index():
    dict = {'name':'liuziping','age':18}

    util.write_log('test', 'api_index')
    return json.dumps(dict,indent=4)
