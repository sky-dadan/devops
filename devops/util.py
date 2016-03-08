#!/bin/env python
# -*- encoding: utf-8 -*-

import os, os.path
import time,json
import base64
import hashlib
import traceback
import logging
import logging.handlers
import ConfigParser
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.header import Header
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

def sendmail(config, rcpt, subject, content):
    smtp_host = config.get("smtp_host", "smtp.mxhichina.com")
    smtp_port = config.get("smtp_port", 25)
    smtp_user = config.get("smtp_user", "sa-notice@yuanxin-inc.com")
    smtp_pass = config.get("smtp_pass", None)

    if isinstance(rcpt, str) or isinstance(rcpt, unicode):
        rcpt = rcpt.split(',')
    elif not isinstance(rcpt, list):
        logging.getLogger().warning("SendMail: rcpt_to format invalid")
        return False

    try:
        smtp = smtplib.SMTP()
        smtp.connect(smtp_host, smtp_port)
        if smtp is not None:
            smtp.login(smtp_user, smtp_pass)

        msg = MIMEText(content,_subtype='plain',_charset='utf-8')
        msg['From'] = smtp_user
        msg['To'] = ','.join(rcpt)
        msg['Subject'] = Header(subject, 'utf-8')

        smtp.sendmail(smtp_user, rcpt, msg.as_string())
        smtp.quit()
        return True
    except:
        logging.getLogger().error("SendMail fail: %s" % traceback.format_exc())
        return False

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
        cmd = cmd.strip().split()
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

def getinfo(table_name,fields):
    '''
    获取用户信息或组信息，返回例如用户信息：{'1':'tom','2','jerry'};组信息{'1':'sa','2':'ask'}
    {u'songpeng': [u'1', u'2'], u'admin': [u'1', u'2', u'4', u'3']}
    fields 格式为['id','name']  ['username','r_id']
    '''
    result = app.config['cursor'].get_results(table_name,fields)
    if fields[1] in ['r_id','p_id','group_all_perm','group_rw_perm','user_all_perm','user_rw_perm']:  #为了区分fields 里面的第二个字段的处理
        result = dict((x[fields[0]],x[fields[1]].split(',')) for x in result)
    else:
        result = dict((str(x[fields[0]]), x[fields[1]]) for x in result)
    return result

#获取一个组里面所有的用户列表
def group_users(users,groups):
    group = {}
    for g_name in groups.values():
        group[g_name] = []
    for u_name, r_id in users.items():
        for g_id, g_name in groups.items():
            if g_id in r_id:
                group[g_name].append(u_name)
    return group
    #print group    #{'ios': ['admin', 'wd'], 'php': ['songpeng'], 'sa': ['admin', 'songpeng']} 
    


def get_git():
    try:  
        users = getinfo('user',['username','r_id'])
        groups = getinfo('groups',['id','name'])
        group = group_users(users,groups) 
        #获取项目列表
        #projects = app.config['cursor'].get_results('project',['id','name'])
        #projects = dict((str(x['id']),x['name']) for x in projects)
        projects = getinfo('project',['id','name'])
        #获取每个项目的权限列表,取出来的是id
        result  = [] 
        perm_fields = ['id','user_all_perm','group_all_perm','user_rw_perm','group_rw_perm']
        for id in projects.keys():
           p_perm = app.config['cursor'].get_one_result('project_perm',perm_fields,{"id":int(id)})
           result.append(p_perm)

    #将权限对应的用户，组id换成适配为name
        #user_git=app.config['cursor'].get_results('user',['id','username'])
        #user_git=dict((str(x['id']),x['username']) for x in user_git)
        user_git = getinfo('user',['id','username'])
    #将每个项目的权限id列表匹配为对应的username  gname,projectname
        p,p_users = {},{}
        for project in result:
            name=projects[str(project['id'])]  #通过id匹配对应的project name
            p[name]={}
            p[name]['user_all_perm'] = [user_git[str(uid)] for uid in project['user_all_perm'].split(',') if uid in user_git] 
            p[name]['user_rw_perm'] = [user_git[str(uid)] for uid in project['user_rw_perm'].split(',') if uid in user_git] 
            p[name]['group_rw_perm'] = [groups[str(gid)] for gid in project['group_rw_perm'].split(',') if gid in groups]  
            p[name]['group_all_perm'] = [groups[str(gid)] for gid in project['group_all_perm'].split(',') if gid in groups]
        print p    
        '''
           p中一条数据  {u'it.miaoshou.com': {'group_rw_perm': [u'sa'], 'group_all_perm': [u'sa'], 'user_rw_perm': [u'admin'], 'user_all_perm': [u'zhangxunan']}
        '''
        print '##############################################################################'
        for key,values in p.items():
            p_users[key] = []
            for k,v in values.items():
                for i in v:
                    if i in group:
                        p_users[key] += group[i]       
                    else: 
                        p_users[key].append(i)
        print p_users
        return {'code':'0','group':group,'project':p,'p_all_users':p_users}
    except:
        logging.getLogger().error("get config error: %s" % traceback.format_exc())
        return {'code':1,'errmsg':"获取用户，组及项目报错"}


#获取每个项目中拥有权限的人的列表,做个并集存到perm_users列表里
def get_userlist(projects,groups,key):
    perm_fields = ['user_all_perm','group_all_perm','user_rw_perm','group_rw_perm']
    perm_users = []
    for field in perm_fields:
        if field.startswith('user'):
            perm_users.extend(projects[key][field])
        else:
            for group in projects[key][field]:
                perm_users.extend(groups[group])
    perm_users = list(set(perm_users))
    return perm_users

