#!/bin/env python
# -*- encoding: utf-8 -*-

import os, os.path
import sys
import time

work_dir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
sys.path.append(work_dir)
import util
import db

ONE_DAY = 24*60*60

if __name__ == '__main__':
    conf_name = os.path.join(work_dir, 'service.conf')
    config = util.get_config(conf_name)

    now = int(time.time()) / ONE_DAY * ONE_DAY
    expire = time.strftime('%Y-%m-%d', time.localtime(now + 20*ONE_DAY))

    content = []
    cursor = db.Cursor(config)
    sql = "SELECT type, expire, remark FROM soft_asset WHERE expire < '%s' ORDER BY expire" % expire
    cursor.execute(sql)
    for row in cursor.fetchall():
        t = time.mktime(time.strptime(str(row[1]), '%Y-%m-%d'))
        last_day = (int(t)-now+8*60*60)/ONE_DAY
        if last_day >= 0:
            msg = '[%s - %s] 到期时间：%s 剩余%s天' % (row[0].encode('utf-8'), row[2].encode('utf-8'), row[1], last_day)
        else:
            msg = '[%s - %s] 到期时间：%s 已过期%s天' % (row[0].encode('utf-8'), row[2].encode('utf-8'), row[1], -last_day)
        content.append(msg)

    if content:
        content.append('以上服务快到期了，请及时续费!')
        util.sendmail(config, 'sa@yuanxin-inc.com', '服务快到期通知', '\n'.join(content))
