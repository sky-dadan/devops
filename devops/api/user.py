#coding:utf-8
from flask import Flask,request
from . import app
import  json,traceback
import logging,util

@app.route('/api/user/<int:user_id>',methods=['GET','PUT','DELETE'])
def User(user_id):
    try:
        authorization = request.headers['authorization']
        name = util.validate(authorization,app.config['passport_key'])
        if not name :
            logging.getLogger().warning("Request forbiden")
            return json.dumps({'code':1,'errmsg':'User validate error'})
    except:
        logging.getLogger().warning('validate error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'User validate error'})
    
    if request.method == 'GET':  #get one user info from user_id
        try:

            if util.if_userid_exist(user_id) is False:
              return json.dumps({'code':1,'errmsg':'User is not exist'})
            user = {}
            fields = ['id','username','name','email','mobile']
            sql = "SELECT %s FROM user where id=%d" % (','.join(fields),user_id)
            app.config['cursor'].execute(sql)
            res = app.config['cursor'].fetchone()    #返回结果为列表[id,username,……]
            for i,k in enumerate(fields):     #取出列表的值及对应的索引号 0.1,2……
                user[k]=res[i]    #fields中的列名作为user字典的k,索引作为数据库返回列表的k,实现字典赋值
            util.write_log(name, 'get_one_users') 
            return json.dumps({'code':0,'users':user})
        except:
            logging.getLogger().error("Get users list error: %s" % traceback.format_exc())
            return json.dumps({'code':1,'errmsg':'Get users error'})
    elif request.method == 'PUT':   #update user info  from user_id
        try:
            if util.if_userid_exist(user_id) is False:
              return json.dumps({'code':1,'errmsg':'User is not exist'})
            data = request.get_json()
            data = json.loads(data)
            username = data['username']
            name = data['name']
            email = data['email']
            mobile = data['mobile']
            sql = 'update user set username="%s",name="%s",email="%s",mobile="%s" where id=%d' % (username,name,email,mobile,user_id)
            app.config['cursor'].execute(sql)
            util.write_log(name,'update user %s' % username)
            return json.dumps({'code':0,'result':'update %s success' % username})
        except:
            logging.getLogger().error('Create user error : %s' % traceback.format_exc())
            return json.dumps({'code':1,'errmsg':'update user error'})
    elif request.method == 'DELETE':
        try:
            if util.role(name) is False:
                logging.getLogger().warning("You are not admin,Request forbiden")
                return json.dumps({'code':1,'errmsg':'You are not admin,Request forbiden'})

            if util.if_userid_exist(user_id) is False:
                return json.dumps({'code':1,'errmsg':'User is not exist'})
            sql = "DELETE FROM user where id = %d" % (user_id) 
            app.config['cursor'].execute(sql)
            util.write_log(name,'delete user %d' % user_id)
            return json.dumps({'code':0,'result':'delte %d success' % user_id})
        except:
            logging.getLogger().error('delete user error : %s' % traceback.format_exc())
            return json.dumps({'code':1,'errmsg':'delete user error'})
    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method})


@app.route('/api/user',methods=['GET','POST'])
def UserList():
    try:
        authorization = request.headers['authorization']
        name = util.validate(authorization, app.config['passport_key'])
        if not name:
            logging.getLogger().warning("Request forbiden")
            return json.dumps({'code': 1, 'errmsg': 'User validate error'})
    except:
        logging.getLogger().warning("Validate error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'User validate error'})
    
    if request.method == 'GET':
        try:
            if util.role(name) is False:
                logging.getLogger().warning("You are not admin,Request forbiden")
                return json.dumps({'code':1,'errmsg':'You are not admin,Request forbiden'})
            users = []
            fields = ['id', 'username', 'name', 'email', 'mobile']
            sql = "SELECT %s FROM user" % ','.join(fields)
            app.config['cursor'].execute(sql)
            for row in app.config['cursor'].fetchall():
                user = {}
                for i, k in enumerate(fields):
                    user[k] = row[i]
                users.append(user)
            util.write_log(name, 'get_all_users')
            return json.dumps({'code': 0, 'users': users})
        except:
            logging.getLogger().error("Get users list error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Get users error'})

    elif request.method == 'POST':
        try:
            if util.role(name) is False:
                logging.getLogger().warning("You are not admin,Request forbiden")
                return json.dumps({'code':1,'errmsg':'You are not admin,Request forbiden'})
            data = request.get_data()
            data = request.get_data()
            data = json.loads(data)
            fields, values = [], []
            for k, v in data.items():
                fields.append(k)
                values.append("'%s'" % v)
            sql = "INSERT INTO user (%s) VALUES (%s)" % (','.join(fields), ','.join(values))
            app.config['cursor'].execute(sql)
            util.write_log(name, "create_user %s" % data['username'])
            return json.dumps({'code': 0, 'result': 'Create %s success' % data['username']})
        except:
            logging.getLogger().error("Create user error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Create user error'})
    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method})



