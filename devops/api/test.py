#coding:utf-8
from flask import Flask
from  . import app             #等价 from api import app
from config  import Cursor
import  json

cur = Cursor()  

@app.route("/api",methods=['GET'])
def index():
    dict = {'name':'liuziping','age':18}

    return json.dumps(dict,indent=4)
