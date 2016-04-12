import sys

from flask import Flask
from flask_jsonrpc import JSONRPC

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
jsonrpc = JSONRPC(app, '/api')

import group
import cabinet
import host
import softassets
import switch
import idc
import services
import manufact
import user_perm
import power
import git
import pub
import project_test
import online
import ext
