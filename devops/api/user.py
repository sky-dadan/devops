#coding:utf-8
from flask import Flask,request
from . import app
import  json,traceback,hashlib
import logging,util
from auth import auth_login


@app.route('/api/user',methods=['GET','PUT','POST','DELETE'])
@auth_login
def User(auth_info,offset=0,size=100):
    if auth_info['code'] == 1:   #主要用于判断认证是否过期，过期会会在web提示
        return json.dumps(auth_info)
    username = auth_info['username']
    uid = int(auth_info['uid'])
    role = int(auth_info['role'])
###########  select for admin and user #################################
    if request.method == 'GET':  #get all user info from user_id
        try:
            users = []
            fields = ['id','username','name','email','mobile','role','is_lock','r_id']
            if role == 0  and request.args.get('list') =="true": #是管理员且传值list＝true才输出用户列表
                if request.args.get('offset')  is not  None and request.args.get('size') is  not None:
                    offset = request.args.get('offset')
                    size = request.args.get('size')
                    if int(size) >= 1000:
                        return json.dumps({'code': 1, 'errmsg': 'you input size too big '})

                gids = app.config['cursor'].get_results('groups', ['id', 'name'])
                gids = dict([(str(x['id']), x['name']) for x in gids])

                result = app.config['cursor'].get_results('user', fields, limit=(offset, size))
                for user in result:
                    user['r_id'] = ','.join([gids[x] for x in user['r_id'].split(',') if x in gids])
                    users.append(user)
                util.write_log(username, 'get_all_users')
                return json.dumps({'code': 0, 'users': users,'count':len(users)})
            elif role != 0  and request.args.get('list') =="true": #普通用户查看用户列表会报错
                return json.dumps({'code': 1,'errmsg':'you not admin ,Cannot look userlist' })

            else:    #普通用户和管理员都是通过自己的登陆用户名查询自己的信息
                user = app.config['cursor'].get_one_result('user', fields, {'username': username})
                util.write_log(username, 'get_one_users') 
                return json.dumps({'code':0,'user':user})
        except:
            logging.getLogger().error("Get users list error: %s" % traceback.format_exc())
            return json.dumps({'code':1,'errmsg':'Get users error'})

##############  update user for admin and user ################################
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            data = json.loads(data)
            if  role == 0 and data.has_key('id'): #是管理员且带有用户id,才说明是管理员更新其他用户   
                user_id = data['id']
                if not util.if_userid_exist(user_id): 
                    return json.dumps({'code':1,'errmsg':'User is not exist'})
                else:
                    sql = app.config['cursor'].execute_update_sql('user', data, {'id': user_id})
            else:                      #普通用户和管理都可以更新自己信息
                sql = app.config['cursor'].execute_update_sql('user', data, {'id': uid})
            util.write_log(username,'update user %s' % username)
            return json.dumps({'code':0,'result':'update %s success' % username})
        except:
            logging.getLogger().error('update user error : %s' % traceback.format_exc())
            return json.dumps({'code':1,'errmsg':'update user error'})

#############  Create user for admin ################################
    elif request.method == 'POST':
        try:
            if role != 0:
                return json.dumps({'code':1,'errmsg':'you not admin '})
            data = request.get_json()
            data = json.loads(data)
#            password = '3b53871ffb407966fc330307500ce968'
            data['password'] = hashlib.md5(data['password']).hexdigest()
            app.config['cursor'].execute_insert_sql('user', data)
            util.write_log(username, "create_user %s" % data['username'])
            return json.dumps({'code': 0, 'result': 'Create %s success' % data['username']})
        except:
            logging.getLogger().error("Create user error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Create user error'})

#############  DELETE  user for admin ###########################
    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            data = json.loads(data)
            if role != 0:
                logging.getLogger().warning("You are not admin,Request forbiden")
                return json.dumps({'code':1,'errmsg':'You are not admin,Request forbiden'})
            else:
                if not data.has_key('user_id'):
                    return json.dumps({'code':1,'errmsg':'must input user_id'})
                else:
                    user_id = data['user_id']
            if not util.if_userid_exist(user_id):
                return json.dumps({'code':1,'errmsg':'User is not exist'})
            app.config['cursor'].execute_delete_sql('user', {'id': user_id})
            util.write_log(username,'delete user %d' % user_id)
            return json.dumps({'code':0,'result':'delte %d success' % user_id})
        except:
            logging.getLogger().error('delete user error : %s' % traceback.format_exc())
            return json.dumps({'code':1,'errmsg':'delete user error'})
   
    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method })

@app.route('/api/user/getbyid/<int:user_id>',methods=['GET'])
@auth_login
def getbyid(auth_info,user_id):
    if auth_info['code'] == 1:   #主要用于判断认证是否过期，过期会会在web提示
        return json.dumps(auth_info)
    username = auth_info['username']
    uid = int(auth_info['uid'])
    role = int(auth_info['role'])
    if request.method == 'GET':  #get user info from user_id
        try:
            fields = ['id','username','name','email','mobile','role','is_lock']
            if role == 0:
                user = app.config['cursor'].get_one_result('user', fields, {'id': user_id})
                util.write_log(username, 'get_one_users') 
                return json.dumps({'code':0,'user':user})
            else:
                util.write_log(username, 'you are not admin!') 
                return json.dumps({'code':1,'result':'you are not admin!'})
        except:
            logging.getLogger().error("Get users list error: %s" % traceback.format_exc())
            return json.dumps({'code':1,'errmsg':'Get users error'})

## 管理员和用户都可以修改密码
@app.route('/api/password',methods=['PUT'])
@auth_login
def passwd(auth_info):
    if auth_info['code'] == 1:   #主要用于判断认证是否过期，过期会会在web提示
        return json.dumps(auth_info)
    username = auth_info['username']
    uid = int(auth_info['uid'])
    role = int(auth_info['role'])
    try:
        data = request.get_json()
        data = json.loads(data)
        if  role==0:   # admin no need oldpassword  but need user_id
            if  not data.has_key('user_id') :
                if data.has_key('oldpassword') and data.has_key('password'):
                    oldpassword = hashlib.md5(data['oldpassword']).hexdigest()
                    res = app.config['cursor'].get_one_result('user', ['password'], {'username': username})
                    if res['password'] != oldpassword:
                        return json.dumps({'code':1,'errmsg':'input  old password is wrong'})
                    else:
                        password = hashlib.md5(data['password']).hexdigest()
                        app.config['cursor'].execute_update_sql('user', {'password': password}, {'username': username})
                        util.write_log(username,'update user password')
                        return json.dumps({'code':0,'result':'update password success'  })
                else:
                    return json.dumps({'code':1,'errmsg':'admin must input user_id'})
            else:
                user_id = data['user_id']
                if not util.if_userid_exist(user_id): 
                    return json.dumps({'code':1,'errmsg':'User is not exist'})
                password = hashlib.md5(data['password']).hexdigest()
                app.config['cursor'].execute_update_sql('user', {'password': password}, {'id': user_id})
        else:                  #user  need input oldpassword
            if not data.has_key("oldpassword") :
                return json.dumps({'code':1,'errmsg':'need input your old password' })
            else:
                oldpassword = hashlib.md5(data['oldpassword']).hexdigest()
                res = app.config['cursor'].get_one_result('user', ['password'], {'username': username})
                if res['password'] != oldpassword:
                    return json.dumps({'code':1,'errmsg':'input  old password is wrong'})
                else:
                    password = hashlib.md5(data['password']).hexdigest()
                    app.config['cursor'].execute_update_sql('user', {'password': password}, {'username': username})
        util.write_log(username,'update user password')
        return json.dumps({'code':0,'result':'update password success'  })
    except:
        logging.getLogger().error('update user password error : %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'update user password error'})


## 用户登录
@app.route('/api/auth', methods=['GET'])
def login():
    if request.method == 'GET':
        try:
            username = request.args.get('username', None)
            passwd = request.args.get('passwd', None)
            passwd = hashlib.md5(passwd).hexdigest()
            if not (username and passwd):
                return json.dumps({'code': 1, 'errmsg': "Please input username or password."})

            result = app.config['cursor'].get_one_result('user', ['id', 'username', 'password', 'role', 'is_lock'], {'username': username})
            if not result:
                return json.dumps({'code': 1, 'errmsg': "No such user."})
            if result['is_lock'] == 1:
                return json.dumps({'code': 1, 'errmsg': "User '%s' is locked." % username})

            if passwd == result['password']:
                s = util.get_validate(result['username'], result['id'], result['role'], app.config['passport_key'])
                return json.dumps({'code': 0, 'authorization': s})
            else:
                return json.dumps({'code': 1, 'errmsg': "Password is wrong."})
        except:
            logging.getLogger().error("user login error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': "login exception"})
    else:
        return json.dumps({'code': 1, 'errmsg': "HTTP Method '%s' doesn't support" % request.method})

