#!/usr/bin/env python
#coding: utf-8
from flask import Flask, request
from . import app, jsonrpc
import logging, util,time
import json, traceback
from auth import auth_login
from jsondate import MyEncoder
from user_perm import getid_list

script_name='/usr/local/devops/devops/script/online/online.sh'

def get_project_info(where):
    id2name_project = app.config['cursor'].projects()
    res = app.config['cursor'].get_one_result('project_apply', ['project_id', 'version', 'commit', 'apply_type', 'status'], where)
    res['name'] = id2name_project[str(res['project_id'])]
    return res

def apply_pub(username,data,where):
    app.config['cursor'].execute_update_sql('project_apply',data,where)
    util.write_log(username,"success and update project_apply status %s" % data['status'])
    fields = ['project_id','info','version','commit','status','detail','apply_type']  #为project_deplpy 准备数据
    result=app.config['cursor'].get_one_result('project_apply',fields,where)
    result['applicant'] = username
    result['apply_date'] = time.strftime("%Y-%m-%d %H:%M:%S")
    app.config['cursor'].execute_insert_sql('project_deploy',result)
    util.write_log(username,"success and insert project_deploy status  %s"  % data['status'])

#创建申请任务列表
@jsonrpc.method('apply.create') 
@auth_login
def apply_create(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    role = int(auth_info['role'])
    try:
        data = request.get_json()['params']  #project_id,project_name,applicant,info,detail
        # 如果key 'apply_type'存在字典里，说明是紧急发布，不存在，是正常发布
        if 'apply_type' in data:
            data['apply_type'] = 1 # 紧急发布
        else:
            data['apply_type'] = 0 # 正常发布

        ret, commit = util.run_script_with_timeout("sh %s apply %s %d" % (script_name,data['project_username'], data['apply_type']))    
        if not ret:
            return json.dumps({'code': 1, 'errmsg': commit})
        data['version']=''
        data['commit'] = commit
        data['applicant'] = username
        data['apply_date'] = time.strftime('%Y-%m-%d %H:%M')
        data['status'] = 1
        where = {"project_id":int(data['project_id'])}
        data.pop('project_username')  
        res = app.config['cursor'].get_one_result('project_apply',['status','apply_type'],where)
        if res:   # 查询某个项目在上次申请的类型，如果为紧急则更新字段
            data['last_apply_type'] = res['apply_type']
        if res and res['status'] in (1, 2):
            return json.dumps({'code': 1, 'errmsg': '目前项目状态不可申请'})
        if res: 
            app.config['cursor'].execute_update_sql('project_apply', data, where)
        else:
            app.config['cursor'].execute_insert_sql('project_apply', data)
        app.config['cursor'].execute_insert_sql('project_deploy',data)  
        util.write_log(username,{'code':0,'result':'项目申请成功'})
        return json.dumps({'code':0,'result':'项目申请成功'})    
    except:
        logging.getLogger().error('project apply error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'项目申请失败'})


#申请列表，任务列表
@jsonrpc.method('apply.getlist')
@auth_login
def apply_list(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','project_id','info','applicant','version','commit','apply_date','apply_type', 'status','detail']
        fields = kwargs.get('output', output)
        loginer = app.config['cursor'].get_results('project_apply',fields)

        where = {'status':['1','2']}
        result = app.config['cursor'].get_results('project_apply',fields,where)
        #id转换成名字
        id2name_project = app.config['cursor'].projects()
        for res in result:
            res['project_name'] = id2name_project[str(res['project_id'])] 

        util.write_log(username, 'get apply list success!')
        return  json.dumps({'code':0,'data':loginer, 'result':result,'count':len(result)},cls = MyEncoder)
    except:
        logging.getLogger().error("select apply list error:%s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'任务列表获取失败!'})

#任务列表，详情按钮
@jsonrpc.method('apply.get')
@auth_login
def apply_one(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        output = ['id','project_id','info','applicant','version','commit','apply_date','apply_type','last_apply_type','status','detail']
        fields = kwargs.get('output', output)
        where = kwargs.get('where',None)
        result = app.config['cursor'].get_one_result('project_apply',fields,where)
        #id转换成名字
        id2name_project = app.config['cursor'].projects()
        result['project_name'] = id2name_project[str(result['project_id'])]

        util.write_log(username, 'get one apply detail success')
        return json.dumps({'code':0,'result':result},cls=MyEncoder)
    except:
        logging.getLogger().error("get apply detail faild : %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'任务详情获取失败!'})

#仿真发布 脚本打上version版本号,触发仿真测试代码脚本, 返回执行结果 更新project_apply为2  灰度发布中,插入一条记录到project_deploy,状态为2
@jsonrpc.method('apply.emulation')
@auth_login
def apply_emulation(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        version = kwargs.get('version')
        pid = kwargs.get('id')
        data, where = {'version':version,'status':'2'},{'id':pid}
        result = get_project_info(where)
        #调用脚本  sh script_name emultion tag commit project_name
        ret, msg = util.run_script_with_timeout("%s emulation %s %s %s %d" % (script_name,version,result['commit'],result['name'], result['apply_type']))
        if ret:
            apply_pub(username,data,where)
            return json.dumps({'code':0, 'result': '仿真发布成功'})
        else:
            return json.dumps({'code':1, 'errmsg':'仿真发布失败!'})
    except:
        logging.getLogger().error("apply.emulation get failed : %s" %  traceback.format_exc())
        return json.dumps({'code':1, 'errmsg':'仿真发布失败!'})

#仿真失败，取消
@jsonrpc.method('apply.cancel')
@auth_login
def apply_cancel(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        pid = kwargs.get('where')
        pid = pid['id']
        where,data = {'id':pid},{'status':'4'}
        result = get_project_info(where)
#调用脚本  sh script_name  cancel_flag project_name 
        ret, msg = util.run_script_with_timeout("%s cancel %s %s %s %d" % (script_name,result['status'], result['name'], result['version'], result['apply_type']))
        if ret:
            apply_pub(username,data,where)
            return json.dumps({'code':0, 'result': '取消发布成功'})
        else:
            return json.dumps({'code': 1, 'errmsg': '取消发布失败'})
    except:
        logging.getLogger().error("apply.cancel get failed : %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'取消发布失败'})


#仿真测试成功，正式上线
@jsonrpc.method("apply.success")
@auth_login
def apply_success(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        pid = kwargs.get('where')
        pid = pid['id']
        where,data = {'id':pid},{'status':'3'}
        result = get_project_info(where)
#调用脚本  sh script_name product_name
        ret, msg = util.run_script_with_timeout("%s product %s %s" % (script_name,result['name'],result['apply_type']))
        if ret:
            apply_pub(username,data,where)
            return json.dumps({'code':0, 'result': '正式发布成功'})
        else:
            return json.dumps({'code':1,'errmsg':'正式上线失败,请联系运维人员!'})
    except:
        logging.getLogger().error("apply success  get failed : %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'正式上线失败,请联系运维人员!'})

def project_attr(result):
    ret = []
    status2name = {1: '申请上线', 2: '上线审核', 3: '上线完成', 4: '上线取消'}
    #id转换成名字
    id2name_project = app.config['cursor'].projects()
    for res in result:
        if str(res['project_id']) not in id2name_project:
            continue
        res['project_name'] = id2name_project[str(res['project_id'])]
        res['status_name'] = status2name.get(res['status'], '未知状态')
        ret.append(res)
    return ret

#上线历史记录查询
@jsonrpc.method("deploy.getlist")
@auth_login
def deploy_list(auth_info,**kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        fields = ['project_id','applicant','version','commit','apply_date','apply_type','status']
        sql = 'SELECT %s FROM (SELECT %s FROM project_deploy ORDER BY apply_date DESC) AS tbl GROUP BY commit, project_id' % (','.join(fields), ','.join(fields))
        app.config['cursor'].execute(sql)
        result_sets = app.config['cursor'].fetchall()
        deploy_result = [dict([(k, '' if row[i] is None else row[i]) for i,k in enumerate(fields)]) for row in result_sets]
        app.config['cursor'].close_db()

        result = project_attr(deploy_result)

        util.write_log(username, 'get deploy list success!')
        return  json.dumps({'code':0, 'result':result, 'count':len(result)},cls = MyEncoder)
    except:
        logging.getLogger().error("select deploy list error:%s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': '获取上线历史记录失败'})

@jsonrpc.method("deploy.get")
@auth_login
def deploy_get(auth_info, **kwargs):
    if auth_info['code'] == 1:
        return json.dumps(auth_info)
    username = auth_info['username']
    try:
        fields = ['id', 'project_id','info','applicant','version','commit','apply_date','apply_type','status','detail']
        if 'ver' in kwargs.get('args', {}):
            where = {'project_id': kwargs.get('where', {}).get('id'), 'commit': kwargs.get('args', {}).get('ver')}
            deploy_result = app.config['cursor'].get_results('project_deploy', fields, where)
            result = project_attr(deploy_result)
            util.write_log(username, "get deploy '%s' success!" % where['commit'])
            return json.dumps({'code':0, 'result':result, 'count':len(result)},cls = MyEncoder)
        else:
            where = {'id': kwargs.get('where', {}).get('id')}
            deploy_result = app.config['cursor'].get_results('project_deploy', fields, where)
            result = project_attr(deploy_result)[0]
            util.write_log(username, "get deploy '%s' success!" % result['commit'])
            return json.dumps({'code':0, 'result':result},cls = MyEncoder)
    except:
        logging.getLogger().error("get deploy error:%s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': "获取版本上线历史记录失败"})
