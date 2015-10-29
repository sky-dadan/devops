#!/bin/env python
# -*- encoding: utf-8 -*-
import os, os.path
import sys
import util
import logging

from web import app

if __name__ == '__main__':
    conf_name = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'service.conf') if len(sys.argv) == 1 else sys.argv[1]
    config = util.get_config(conf_name, 'web')
    util.set_logging(config['log_path'], config.get('log_level', 'info'))

    app.run(host=config.get('bind', '0.0.0.0'), port=int(config.get('port')), debug=True)
