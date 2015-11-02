#!/bin/env python
# -*- encoding: utf-8 -*-
import os, os.path
import sys
import imp
import logging
import traceback

import db
import util

#from api import app

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: %s [api|web]" % sys.argv[0]
        sys.exit()

    module_name = sys.argv[1]
    work_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

    try:
        import_str = "from %s import app" % module_name
        exec import_str
    except:
        print "Load '%s' module error" % module_name
        sys.exit()

    conf_name = os.path.join(work_dir, 'service.conf')
    config = util.get_config(conf_name, module_name)
    util.set_logging(config['log_path'], config.get('log_level', 'info'))

    app.config['cursor'] = db.Cursor(config)
    app.config.update(config)

    app.run(host=config.get('bind', '0.0.0.0'), port=int(config.get('port')), debug=True)
