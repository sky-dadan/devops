#coding:utf-8
from flask import Flask,request
from . import app
import  json,traceback
import logging,util

@app.route('/api/role/<int:user_id>',methods=['PUT'])
def role(user_id):
    try:
        authorization = request.headers['authorization']
        name = util.validate(authorization,app.config['passport_key'])
        if not name :
            logging.getLogger().warning("Request forbiden")
            return json.dumps({'code':1,'errmsg':'User validate error'})
        else:
            if not  util.role(name):   #not admin 
                logging.getLogger().warning("You are not admin,Request forbiden")
                return json.dumps({'code':1,'errmsg':'You are not admin,Request forbiden'})
    except:
        logging.getLogger().warning('validate error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'User validate error'})
    
    try:
        if not util.if_userid_exist(user_id): 
          return json.dumps({'code':1,'errmsg':'User is not exist'})
        data = request.get_json()
        data = json.loads(data)
        sql = 'update user set role=%d where id=%d' % (data['role'],user_id)
        app.config['cursor'].execute(sql)
        util.write_log(name,'update user  %s role' % user_id)
        return json.dumps({'code':0,'result':'update %s success' % user_id})
    except:
        logging.getLogger().error('update user role error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'update user role error'})
