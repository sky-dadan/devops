#!/bin/env python
# -*- encoding: utf-8 -*-

import os, os.path
import time,json
import base64
import hashlib
import logging
import logging.handlers
import ConfigParser
import subprocess
from api import app

def get_config(config_filename, section=''):
    config = ConfigParser.ConfigParser()
    config.read(config_filename)

    conf_items = dict(config.items('common')) if config.has_section('common') else {}
    if section and config.has_section(section):
       conf_items.update(config.items(section))
    return conf_items

def set_logging(log_path, log_level='error'):
    def add_handler(log_name, formatter, level, logger=None):
        if not logger:
            return

        log_handler = logging.handlers.TimedRotatingFileHandler(log_name, when='midnight')
        log_formatter = logging.Formatter(formatter)
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)
        logger.setLevel(level)

    LOG_LEVELS = {
                  'critical': logging.CRITICAL, 'error': logging.ERROR,
                  'warning': logging.WARNING, 'info': logging.INFO,
                  'debug': logging.DEBUG
                 }

    if not os.path.isdir(log_path):
        os.makedirs(log_path)
    log_name = os.path.join(log_path, 'record.log')
    logger = logging.getLogger('record')
    formatter = '%(message)s'
    add_handler(log_name, formatter, logging.DEBUG, logger)

    log_name = os.path.join(log_path, 'service.log')
    logger = logging.getLogger()
    formatter = '%(asctime)s %(levelname)s %(filename)s-%(funcName)s:%(lineno)d %(message)s'
    add_handler(log_name, formatter, LOG_LEVELS.get(log_level.lower(), logging.ERROR), logger)

def write_log(user, msg):
    logging.getLogger('record').debug('%s %s %s' % (int(time.time()), user, msg))

def get_validate(username, uid, role, fix_pwd):
    t = int(time.time())
    validate_key = hashlib.md5('%s%s%s' % (username, t, fix_pwd)).hexdigest()
    return base64.b64encode('%s|%s|%s|%s|%s' % (username, t, uid, role, validate_key)).strip()

def validate(key, fix_pwd):
    t = int(time.time())
    key = base64.b64decode(key)
    x = key.split('|')
    if len(x) != 5:
        logging.getLogger().warning("token参数数量不足")
        return json.dumps({'code':1,'errmsg':'token参数不足'})

    if t > int(x[1]) + 2*60*60:
        logging.getLogger().warning("登录已经过期")
        return json.dumps({'code':1,'errmsg':'登录已过期'})
    validate_key = hashlib.md5('%s%s%s' % (x[0], x[1], fix_pwd)).hexdigest()
    if validate_key == x[4]:
        logging.getLogger().info("api认证通过")
        return json.dumps({'code':0,'username':x[0],'uid':x[2],'role':x[3]})
    else:
        logging.getLogger().warning("密码不正确")
        return json.dumps({'code':1,'errmsg':'密码不正确'})

def check_name(name):
    if isinstance(name, str) or isinstance(name, unicode):
        return name.isalnum() and len(name) > 2
    else:
        return False

def run_script(cmd):
    if isinstance(cmd, str) or isinstance(cmd, unicode):
        cmd = cmd.trim().split()
    elif not isinstance(cmd, list):
        logging.getLogger().warning("执行命令格式不正确。命令为: %s" % str(cmd))
        return None

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = process.read().strip()
        logging.getLogger().info("执行命令[%s]结果: %s" % (' '.join(cmd), out))
        return out
    except:
        logging.getLogger().warning("执行命令[%s]异常: %s" % (' '.join(cmd), traceback.format_exc()))
        return None


def get_git():
    try:  
        #获取所有用户信息
        users=app.config['cursor'].get_results('user',['username','r_id'])
        users=dict((x['username'],x['r_id'].split(',')) for x in users)
        #print users   #{u'songpeng': [u'1', u'2'], u'admin': [u'1', u'2', u'4', u'3']}

        #获取所有组信息
        groups=app.config['cursor'].get_results('groups',['id','name'])
        groups=dict((str(x['id']),x['name']) for x in groups)
        #print groups  #{'1': u'sa', '2': u'admin', '3': u'ask', '4': u'PHP']}

        #获取每个组的成员——git配置文件分组数据渲染
        group = {}
        for g_name in groups.values():
            group[g_name]=[]  
        #print group     #{u'admin': [], u'iOS': [], u'sa': [], u'ask': [], u'PHP':[]}
        for u_name,r_id in users.items():
            for g_id,g_name in groups.items():
                if g_id in r_id:
                     group[g_name].append(u_name)
        #print group    #{'ios': ['admin', 'wd'], 'php': ['songpeng'], 'sa': ['admin', 'songpeng']}

        #获取项目列表
        projects = app.config['cursor'].get_results('project',['id','name'])
        projects = dict((str(x['id']),x['name']) for x in projects)
	
        #获取每个项目的权限列表,取出来的是id
	result  = [] 
        perm_fields = ['id','user_all_perm','group_all_perm','user_rw_perm','group_rw_perm']
        for id in projects.keys():
            p_perm = app.config['cursor'].get_one_result('project_perm',perm_fields,{"id":int(id)})
            result.append(p_perm)

	#将权限对应的用户，组id换成适配为name
        user_git=app.config['cursor'].get_results('user',['id','username'])
        user_git=dict((str(x['id']),x['username']) for x in user_git)
	
	#将每个项目的权限id列表匹配为对应的username  gname,projectname
        p = {}
	for project in result:
 		name=projects[str(project['id'])]  #通过id匹配对应的project name
                p[name]={}
		p[name]['user_all_perm'] = [user_git[str(uid)] for uid in project['user_all_perm'].split(',') if uid in user_git.keys()] #将用户或组id匹配为name 
		p[name]['user_rw_perm'] = [user_git[str(uid)] for uid in project['user_rw_perm'].split(',') if uid in user_git.keys()] 
		p[name]['group_rw_perm'] = [groups[str(gid)] for gid in project['group_rw_perm'].split(',') if gid in groups.keys()]  
	 	p[name]['group_all_perm'] = [groups[str(gid)] for gid in project['group_all_perm'].split(',') if gid in groups.keys()]
	#print p	
                
        return json.dumps({'code':'0','group':group,'project':p})
    except:
        logging.getLogger().error("get config error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':"获取用户，组及项目报错"})

