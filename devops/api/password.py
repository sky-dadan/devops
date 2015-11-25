#coding:utf-8
from flask import Flask,request
from . import app
import  json,traceback,hashlib
import logging,util
from auth import auth_login

@app.route('/api/password',methods=['PUT'])
@auth_login
def passwd(auth_info):
    try:
        data = request.get_json()
        data = json.loads(data)
        name = auth_info[0]
        uid = int(auth_info[1])
        role = int(auth_info[2])
        if  role==0:   # admin no need oldpassword  but need user_id
            if  not data.has_key('user_id') :
                return json.dumps({'code':1,'errmsg':'admin must input user_id'})
            else:
                user_id = data['user_id']
                if not util.if_userid_exist(user_id): 
                    return json.dumps({'code':1,'errmsg':'User is not exist'})
                password = hashlib.md5(data['password']).hexdigest()
                sql = 'update user set password="%s" where id=%d' % (password,user_id)
        else:                  #user  need input oldpassword
            if not data.has_key("oldpassword") :
                return json.dumps({'code':1,'errmsg':'need input your old password' })
            else:
                oldpassword = hashlib.md5(data['oldpassword']).hexdigest()
                sql = 'select password from user where username="%s"' % name
                app.config['cursor'].execute(sql)
                res = app.config['cursor'].fetchone()
                if res[0] != oldpassword:
                    return json.dumps({'code':1,'errmsg':'input  old password is wrong'})
                else:
                    password = hashlib.md5(data['password']).hexdigest()
                    sql = 'update user set password="%s" where username="%s"' % (password,name)
        app.config['cursor'].execute(sql)
        util.write_log(name,'update user password')
        return json.dumps({'code':0,'result':'update password success'  })
    except:
        logging.getLogger().error('update user password error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'update user password error'})
