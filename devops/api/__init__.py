from flask import Flask
from flask_jsonrpc import JSONRPC

app = Flask(__name__)
jsonrpc = JSONRPC(app, '/api')

#import  test
import group
import user
import cabinet
