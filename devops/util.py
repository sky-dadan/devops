#!/bin/env python
# -*- encoding: utf-8 -*-

import os, os.path
import time,json
import base64
import hashlib
import logging
import logging.handlers
import ConfigParser
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

def get_validate(name, uid, role, fix_pwd):
    t = int(time.time())
    validate_key = hashlib.md5('%s%s%s' % (name, t, fix_pwd)).hexdigest()
    return base64.b64encode('%s|%s|%s|%s|%s' % (name, t, uid, role, validate_key)).strip()

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
        return json.dumps({'code':0,'name':x[0],'uid':x[2],'role':x[3]})
    else:
        logging.getLogger().warning("密码不正确")
        return json.dumps({'code':1,'errmsg':'密码不正确'})
        

def if_userid_exist(user_id):
    sql = 'select * from user where id = %d ' % (user_id)
    app.config['cursor'].execute(sql)
    res = app.config['cursor'].fetchone()
    if res is None:
        logging.getLogger().error("user is not exist")
        return False
    else:
        return True

def if_groupid_exist(group_id):
    sql = 'SELECT * FROM groups WHERE id = %d' % (group_id)
    app.config['cursor'].execute(sql)
    res = app.config['cursor'].fetchone()
    if res is None:
        logging.getLogger().error("group is not exist")
        return False
    else:
        return True

