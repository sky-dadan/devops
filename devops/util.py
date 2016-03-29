#!/bin/env python
# -*- encoding: utf-8 -*-

import os, os.path
import time,json
import base64
import shlex
import hashlib
import smtplib
import traceback
import logging
import logging.handlers
import ConfigParser
import collections
import subprocess
import multiprocessing 
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
        return name.isalnum() and len(name) >= 2
    else:
        return False

def run_script(cmd, queue=None):
    if isinstance(cmd, str) or isinstance(cmd, unicode):
        cmd = shlex.split(cmd.strip())
    elif not isinstance(cmd, list):
        logging.getLogger().warning("执行命令格式不正确。命令为: %s" % str(cmd))
        return None

    try:
        subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if queue is not None:
            queue.put(subproc)
        out = subproc.stdout.read().strip()
        if queue is not None:
            queue.put(out)
        logging.getLogger().info("执行命令[%s]结果: %s" % (' '.join(cmd), out))
        return out
    except:
        logging.getLogger().warning("执行命令[%s]异常: %s" % (' '.join(cmd), traceback.format_exc()))
        return None

def run_script_with_timeout(cmd, timeout=30):
    queue = multiprocessing.Queue()
    try:
        process = multiprocessing.Process(target=run_script, args=(cmd, queue))
        process.start()
        process.join(timeout)
        subproc = queue.get(2)
        if process.is_alive():
            subproc.terminate()
            process.terminate()
            logging.getLogger().warning("执行命令超时退出")
        else:
            return queue.get(2)
    except:
        logging.getLogger().warning("执行超时命令[%s]异常: %s" % (cmd, traceback.format_exc()))
    finally:
        queue.close()

def getinfo(table_name,fields):
    '''
    查询单个数据表任意两列的内容，然后将结果拼接成字 
    fields 格式为 ['field1','field2'], 例如['id','name'],['name','r_id']
    返回结果一，两列都是字符串如：用户id2name {'1':'tom','2','jerry'}; 组信息id2name {'1':'sa','2':'ask'}
    返回结果二，第二列是个列表如：用户权限信息：{u'songpeng': [u'1', u'2'], u'admin': [u'1', u'2', u'4', u'3']}
    '''
    result = app.config['cursor'].get_results(table_name,fields)
    if fields[1] in ['r_id','p_id','group_all_perm','group_rw_perm','user_all_perm','user_rw_perm']:  #第二列的结果为列表的字段拼接为字符串
        result = dict((str(x[fields[0]]), x[fields[1]].split(',')) for x in result)
    else:
        result = dict((str(x[fields[0]]), x[fields[1]]) for x in result)
    return result

#获取一个组里面所有的用户列表
#需要传入用户信息users=getinfo(user,['username','r_id'])和组信息groups=getinfo(group,['id','name'])
def group_users(users,groups):
    group = dict([(g_name, []) for g_name in groups.values()])
    for u_name, r_id in users.items():
        for g_id, g_name in groups.items():
            if g_id in r_id:
                group[g_name].append(u_name)
    return group
    #print group    #{'ios': ['admin', 'wd'], 'php': ['songpeng'], 'sa': ['admin', 'songpeng']} 
    

#获取项目对应权限的人员和组，
def get_git():
    try:  
        #获取项目，用户，组表中对应的两个字段返回字典
        projects = getinfo('project',['id','name'])
        users = getinfo('user',['username','r_id'])
        groups = getinfo('user_group',['id','name'])
        group = group_users(users,groups) 
        #获取每个项目的权限列表,取出来的是id
        perm_fields = ['id','user_all_perm','group_all_perm','user_rw_perm','group_rw_perm']
        result = app.config['cursor'].get_results('project_perm', perm_fields)
        #[{'id':'1','user_all_perm':'1,2','user_rw_perm':'1,3',.....},.......]

        #将每个项目的权限id列表匹配为对应的username  gname,projectname
        user_git = getinfo('user',['id','username'])
        p,p_users = {},{}
        for project in result:
            name=projects[str(project['id'])]  #通过id匹配对应的project name
            p[name]={}
            for k, v in [('user_all_perm', user_git), ('user_rw_perm', user_git), ('group_all_perm', groups), ('group_rw_perm', groups)]:
                p[name][k] = [v[x] for x in project[k].split(',') if x in v]
        #p中一条数据  {u'it.miaoshou.com': {'group_rw_perm': [u'sa'], 'group_all_perm': [u'sa'], 'user_rw_perm': [u'admin'], 'user_all_perm': [u'zhangxunan']}

        #进一步查询每个项目都有哪些人参与，即将p里组的成员都都替换为具体的人
        for key,values in p.items():
            p_users[key] = set([])
            for k,v in values.items():
                if k.startswith('group'):
                    for x in v:
                        p_users[key] |= set(group[x])
                elif k.startswith('user'):
                    p_users[key] |= set(v)
        #print p_users
        return {'code':'0','group':group,'project':p,'p_all_users':p_users}
    except:
        logging.getLogger().error("get config error: %s" % traceback.format_exc())
        return {'code':1,'errmsg':"获取用户，组及项目报错"}

#普通用户返回他所拥有权限的项目
def partOfTheProject(result,projects,pro_all_users,username):
    #取出username所在项目的列表
    project_list = [key for key in projects if username in pro_all_users[key]]

    res = []
    for pro in result:
        if pro['name'] in project_list:
            res.append(pro)
    return res

#用户返回他所拥有权限的项目,后期替换掉上面的partOfTheProject的方法
def userproject(username):
    res = get_git()
    p_users = res['p_all_users']
    projects = getinfo('project',['name','id']) #由于发布和申请表中存的都是project_id, 将项目的id 和 name
    #print username
    myproject = [p_name for p_name,p_user in p_users.items() if username in p_user] #用户所有项目名的列表
    result = dict((projects[p_name],p_name) for p_name in myproject)  #返回用户所有项目字典{p_id:p_name,...}
    return result  

class ProjectConfig:
    def __init__(self, config_filename):
        self.name = config_filename
        self.project_list = collections.defaultdict(set)
        self.host_list = []
        self.default_host = None

        self._load_config()

    #配置文件中以[[]]内标示主机，其余行为项目名，其中行以'#'开头的为注释行
    #有效的第一行必须为主机项
    def _load_config(self):
        in_all = False
        for l in file(self.name):
            l = l.strip()
            if not l or l.startswith('#'):
                continue

            if l.startswith('[[') and l.endswith(']]'):
                l = l.lower()[2:-2]
                if l == 'all':
                    in_all = True
                else:
                    self.host_list.append(l)
            else:
                if not self.host_list:
                    logging.getLogger().warning("配置文件'%s'需要先指定一个主机")
                    return
                #若主机下的项目设置为default，则对未设置主机的项目默认为该主机
                if l == 'default':
                    self.default_host = self.host_list[-1]
                    continue
                if in_all:
                    for x in self.host_list:
                        self.project_list[l].add(x)
                else:
                    self.project_list[l].add(self.host_list[-1])

    def reload(self, filename):
        self.name = filename
        self._load_config()

    def get(self, project):
        if project in self.project_list:
            return self.project_list[project]
        else:
            return set([self.default_host]) if self.default_host else self.default_host

    def gets(self, projects):
        return dict([(x, self.get(x)) for x in projects])
