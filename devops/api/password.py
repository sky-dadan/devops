#coding:utf-8
from flask import Flask,request
from . import app
import  json,traceback,hashlib
import logging,util

@app.route('/api/password/<int:user_id>',methods=['PUT'])
def passwd(user_id):
    try:
        authorization = request.headers['authorization']
        name = util.validate(authorization,app.config['passport_key'])
        if not name :
            logging.getLogger().warning("Request forbiden")
            return json.dumps({'code':1,'errmsg':'User validate error'})
    except:
        logging.getLogger().warning('validate error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'User validate error'})
    
    try:
        if not util.if_userid_exist(user_id): 
          return json.dumps({'code':1,'errmsg':'User is not exist'})
        data = request.get_json()
        data = json.loads(data)
        if  util.role(name):   # admin no need oldpassword
            password = hashlib.md5(data['password']).hexdigest()
            sql = 'update user set password="%s" where id=%d' % (password,user_id)
        else:                  #user  need input oldpassword
            if data['oldpassword'] is None:
                return json.dumps({'code':1,'errmsg':'need input your old password'})
            else:
                oldpassword = hashlib.md5(data['oldpassword']).hexdigest()
                sql = 'select password from user where username="%s"' % (name)
                app.config['cursor'].execute(sql)
                res = app.config['cursor'].fetchone()
                if res[0] != oldpassword:
                    return json.dumps({'code':1,'errmsg':'input  old password is wrong'})
                else:
                    password = hashlib.md5(data['password']).hexdigest()
                    sql = 'update user set password="%s" where username="%s"' % (password,name)
        app.config['cursor'].execute(sql)
        util.write_log(name,'update user  %s password' % user_id)
        return json.dumps({'code':0,'result':'update %s success' % user_id})
    except:
        logging.getLogger().error('update user password error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'update user password error'})
