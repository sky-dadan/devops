#!/usr/bin/env python
#coding: utf-8
import datetime
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app, jsonrpc
import logging, util
import json, traceback,os,sys
from auth import auth_login
import time,requests
from user_perm import getid_list


#headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }
headers = {"Content-Type": "application/json"}

#插入一条上线记录
@jsonrpc.method('rota.create')
@auth_login
def rota_create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:

        data = request.get_json()['params']

        app.config['cursor'].execute_insert_sql('rota', data)
        util.write_log(username,{'code':0,'result':'添加值班记录成功'})
        return json.dumps({'code':0,'result':'添加值班记录成功'})    
    except:
        logging.getLogger().error('添加值班记录错误: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'添加值班记录失败'})



@jsonrpc.method('rota.getlist')     
@auth_login
def rota_get(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        output = ['id', 'start_date', 'end_date', 'man_on_duty']
        result = []
        # 今天
        today = datetime.date.today()
        # 通过今天算出每周的周一
        monday = today - datetime.timedelta(today.weekday())
        # 每周的周一加上4周减一天 4*7-1 就是这周到第4周的最后一天
        last_day = monday + datetime.timedelta(days=27)
        sql = "SELECT %s FROM rota WHERE start_date >= '%s' and end_date <= '%s'" % (','.join(output), str(monday), str(last_day))
        #sql = "SELECT * FROM rota WHERE start_date >= '2016-08-08' AND end_date <= '2016-08-28'"
        print sql
        app.config['cursor'].execute(sql)
        for item in app.config['cursor'].fetchall():
            res = {}
            for i,k in enumerate(output):
                res[k] = item[i]
            result.append(res)
        print result
        if result:
            for item in result:
                item['start_date'] = str(item['start_date'])
                item['end_date'] = str(item['end_date'])
            util.write_log(username, '查询值班表单个记录成功') 
            return json.dumps({'code':0,'result':result})
        else:
            return json.dumps({'code':1,'errmsg':'没查到值班表记录'})
    except:
        logging.getLogger().error("查询单个值班记录错误: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '查询单个值班记录错误'})

@jsonrpc.method('rota.get')
@auth_login
def rota_getlist(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps({'code': 1, 'errmsg': '%s' % auth_info['errmsg']})
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        fields = ['id', 'start_date', 'end_date', 'man_on_duty'] 
        result = app.config['cursor'].get_results('rota', fields)
        if result:
            for item in result:
                item['start_date'] = str(item['start_date'])
                item['end_date'] = str(item['end_date'])
            print result
            util.write_log(username, '查询值班列表成功') 
            return json.dumps({'code':0,'result':result,'count':len(result)})
        else:
            util.write_log(username, '没有获取到值班列表') 
            return json.dumps({'code':1,'errmsg':'没有获取到值班列表'})
    except:
        logging.getLogger().error("获取值班列表失败: %s" % traceback.format_exc())
        return json.dumps({'code': 2, 'errmsg': '获取值班列表失败'})

@jsonrpc.method('rota.update')
@auth_login
def update(auth_info,**kwargs):
    if auth_info['code'] == 1:   
        return json.dumps(auth_info)
    username = auth_info['username']
    if auth_info['role'] != '0':
        return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
    try:
        data = kwargs.get('data',None)
        where = kwargs.get('where',None)
        result = app.config['cursor'].execute_update_sql('rota', data, where,
                    ['start_date', 'end_date', 'man_on_duty'])
        if result == '':
            return json.dumps({'code':1,'errmsg':'没有更新'})
        util.write_log(username,'更新值班列表成功!')
        return json.dumps({'code':0,'result':'更新值班列表成功'})
    except:
        logging.getLogger().error('更新值班列表失败: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'更新值班列表失败'})


