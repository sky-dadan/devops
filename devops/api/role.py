#coding:utf-8
from flask import Flask,request
from . import app
import  json,traceback
import logging,util
from auth import auth_login

@app.route('/api/role/<int:user_id>',methods=['PUT'])
@auth_login
def role(auth_info,user_id):
    try:
        name = auth_info[0]
        role = int(auth_info[2])
        if role != 0:
            logging.getLogger().warning("Request forbiden")
            return json.dumps({'code': 1, 'errmsg': 'User validate error, Request forbiden'})
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
