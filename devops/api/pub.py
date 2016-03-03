#!/usr/bin/env python
#coding: utf-8
from flask import Flask, request
from flask_jsonrpc import JSONRPC
from . import app, jsonrpc
import logging, util
import json, traceback
from auth import auth_login
from jsondate import MyEncoder

#下拉菜单，已经选上的项目  已选下拉菜单统一接口selected.get  
'''
    u_all_sel 定义名称 t1,c1 查出指定id的c1列,  t2,c2查出指定用户或者组的c2列
    以后需要添加  已选中的下拉菜单,直接在color_selected字典里面添加元素即可
'''
color_selected= {'u_all_sel':{'t1':'project_perm','c1':['user_all_perm'],'t2':'user','c2':['id','name']},
                 'g_all_sel':{'t1':'project_perm','c1':['group_all_perm'],'t2':'groups','c2':['id','name']},
                 'g_rw_sel':{'t1':'project_perm','c1':['group_rw_perm'],'t2':'groups','c2':['id','name']},
                 'u_rw_sel':{'t1':'project_perm','c1':['user_rw_perm'],'t2':'user','c2':['id','name']},
                 'principal_sel':{'t1':'project','c1':['principal'],'t2':'user','c2':['id','name']},
                 'power_sel':{'t1':'groups','c1':['p_id'],'t2':'power','c2':['id','name']},
                 'groups_sel':{'t1':'user','c1':['r_id'],'t2':'groups','c2':['id','name']}
                }


@jsonrpc.method('selected.get')
@auth_login
def selected(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        where = kwargs.get('where',None)
        sel = kwargs.get('selected',None)
        res = app.config['cursor'].get_one_result(color_selected[sel]['t1'],color_selected[sel]['c1'],where)
        tmp_list = getid_list([str(res[color_selected[sel]['c1'][0]])])
        result = app.config['cursor'].get_results(color_selected[sel]['t2'],color_selected[sel]['c2'])
        ids = set([str(x['id']) for x in result])  & set(tmp_list)
        for x in result:
            x['selected'] = 'selected="selected"' if str(x['id'])  in ids else ''
        util.write_log(username,'selected  %s, %s  successfully' % (color_selected[sel]['t1'],color_selected[sel]['c1']))
        return json.dumps({'code':0,'result':result})
    except:
        logging.getLogger().error('selected.get  error: %s' % traceback.format_exc())
        return json.dumps({'code':'1','errmsg':'selected.get  error'})
