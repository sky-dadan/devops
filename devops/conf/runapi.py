#!/bin/env python
# -*- encoding: utf-8 -*-
import os, os.path
import sys
import imp
import logging
import traceback
from api import app
import db
import util


work_dir = os.path.dirname(os.path.realpath('service.conf'))
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

conf_name = os.path.join(work_dir, 'service.conf')
config = util.get_config(conf_name, 'api')
util.set_logging(config['log_path'], config.get('log_level', 'info'))
f = file('/tmp/api.log','w') 
app.config['cursor'] = db.Cursor(config)
app.config.update(config)
print >>f, app.config
f.close()
if __name__ == '__main__':
    app.run(host=config.get('bind', '0.0.0.0'),port=int(config.get('port')), debug=True)
