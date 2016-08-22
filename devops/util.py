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

reverse_dict = lambda d: dict([(v, k) for k, v in d.items()])

def get_config(config_filename, section=''):
    config = ConfigParser.ConfigParser()
    config.read(config_filename)

    conf_items = dict(config.items('common')) if config.has_section('common') else {}
    if section and config.has_section(section):
       conf_items.update(config.items(section))
    return conf_items

class ConcurrentDayRotatingFileHandler(logging.handlers.BaseRotatingHandler):
    def __init__(self, filename, encoding=None, delay=False):
        logging.handlers.BaseRotatingHandler.__init__(self, filename, 'a', encoding, delay)
        self.day = time.strftime('%Y-%m-%d', time.localtime())

    def shouldRollover(self, record):
        now_day = time.strftime('%Y-%m-%d', time.localtime())
        if self.stream is None:
            self.stream = self._open()
        if now_day == self.day:
            return False
        return True

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        rotate_log = "%s.%s" % (self.baseFilename, self.day)
        if not os.path.exists(rotate_log):
            os.rename(self.baseFilename, rotate_log)
        self.day = time.strftime('%Y-%m-%d', time.localtime())

        if not self.delay:
            self.stream = self._open()

def set_logging(log_path, log_level='error'):
    def add_handler(log_name, formatter, level, logger=None):
        if not logger:
            return

        log_handler = ConcurrentDayRotatingFileHandler(log_name)
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
    formatter = '%(asctime)s %(levelname)s %(process)d %(thread)d %(filename)s-%(funcName)s:%(lineno)d %(message)s'
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
        logging.getLogger().error("SendMail to '%s' success" % ','.join(rcpt))
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

def run_script(cmd, res=None):
    if isinstance(cmd, str) or isinstance(cmd, unicode):
        cmd = shlex.split(cmd.strip())
    elif not isinstance(cmd, list):
        logging.getLogger().warning("执行命令格式不正确。命令为: %s" % str(cmd))

    try:
        subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if res is not None:
            res['proc'] = subproc
        out = subproc.stdout.read().strip()
        if res is not None:
            res['output'] = out
        logging.getLogger().info("执行命令[%s]结果: %s" % (' '.join(cmd), out))
        return out
    except:
        if res is not None:
            res['output'] = 'ERROR: 执行脚本异常'
        logging.getLogger().warning("执行命令[%s]异常: %s" % (' '.join(cmd), traceback.format_exc()))

def run_script_with_timeout(cmd, timeout=30):
    manager = multiprocessing.Manager()
    res = manager.dict()
    try:
        process = multiprocessing.Process(target=run_script, args=(cmd, res))
        process.start()
        process.join(timeout)
        if process.is_alive():
            if 'proc' in res:
                res['proc'].terminate()
            process.terminate()
            logging.getLogger().warning("执行命令超时退出")
        else:
            if 'output' in res:
                last_line = res['output'].strip().split('\n')[-1].strip()
                if last_line.startswith('OK:'):
                    return True, last_line[3:].strip()
                else:
                    return False, last_line[6:].strip() if last_line.startswith('ERROR:') else last_line
    except:
        logging.getLogger().warning("执行超时命令[%s]异常: %s" % (cmd, traceback.format_exc()))
    return False, ''

#获取一个组里面所有的用户列表
#需要传入用户信息users=getinfo(user,['id', 'username'])、组信息groups=getinfo(group,['id','name'])和user_groups=getinfo(user,['id','r_id'])
def group_members(users=None, groups=None, user_groups=None, db=None):
    if db:
        users = db.users
        groups = db.groups
        user_groups = db.user_groups

    g = {}
    for u, r_id in user_groups.items():
        for x in r_id:
            if u not in users or x not in groups:
                continue
            if groups[x] not in g:
                g[groups[x]] = []
            g[groups[x]].append(users[u])
    return g
    #print group    #{'ios': ['admin', 'wd'], 'php': ['songpeng'], 'sa': ['admin', 'songpeng']} 

# 获取所有项目中用户成员(用户和组中的成员要去重),结果格式:{'devops':['wd','pc'],'test':['wd','rock']}
def project_members(db=None):
    if db:
        users = db.users     # {'1':'wd','2':'pc'}
        groups = db.groups   #  # {'1':'sa','2':'dba','3':'dev'}
        user_groups = db.user_groups   #  # {'1':'sa','2':'dba','3':'dev'}
	group_users = group_members(users, groups, user_groups)  # {'sa': ['wd'], 'dba': ['wd','pc']}
        result = db.get_results('git',['id','name','principal','p_user','p_group']) 
        # result=[{'id':'1','name':'devops','principal':'1','p_user':'1,2','p_group':'1,3'},......]
        pro_pri = {}     # 项目负责人对应项目的字典
        projects = {}    # 项目成员对应项目的字典
        for p in result:
            projects.setdefault(p['name'],[])
            pro_pri.setdefault(p['name'],[])
            for pri in p['principal'].split(','):
                if pri in users:
                    projects[p['name']].append(users[pri]) 
                    pro_pri[p['name'] ].append(users[pri]) 
            for u in p['p_user'].split(','):
                if u in users:
                      projects[p['name']].append(users[u]) 
            for g in p['p_group'].split(','):
                if g in groups:
                     # 由于r_users不保存空组的信息，但项目表可能选择了空组,故将空组默认位置为空列表
                     projects[p['name']] += group_users.get(groups[g],[]) 
            projects[p['name']] = list(set(projects[p['name']])) # 将p_user和p_group中的用户去重复
            
        return projects,pro_pri


#普通用户返回他所拥有权限的项目
def user_projects(name, db):
    members = project_members(db=db)[0]
    projects = reverse_dict(db.projects)
    return dict([(projects[x], x) for x in members if name in members[x]])

class ProjectConfig:
    def __init__(self, config_filename):
        self.name = config_filename
        self.project_list = collections.defaultdict(set)
        self.host_list = []
        self.default_host = None

        self._load_config()

    # 配置文件中以[[]]内标示主机，其余行为项目名，其中行以'#'开头的为注释行
    # 有效的第一行必须为主机项
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
