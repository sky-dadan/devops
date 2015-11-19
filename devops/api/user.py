#coding:utf-8
from flask import Flask,request
from . import app
import  json,traceback,hashlib
import logging,util

@app.route('/api/user',methods=['GET','PUT','POST','DELETE'])
def User(offset=0,size=10):
    try:
        authorization = request.headers['authorization']
        name = util.validate(authorization,app.config['passport_key'])
        if not name :
            logging.getLogger().warning("Request forbiden")
            return json.dumps({'code':1,'errmsg':'User validate error'})
    except:
        logging.getLogger().warning('validate error: %s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'User validate error'})
    
###########  select for admin and user #################################
    if request.method == 'GET':  #get one user info from user_id
        try:
            user = {}
            users = []
            fields = ['username','name','email','mobile','role']
            if util.role(name) and request.args.get('list') =="true": #是管理员且传值list＝true才输出用户列表
                if request.args.get('offset')  is not  None and request.args.get('size') is  not None:
                    offset = request.args.get('offset')
                    size = request.args.get('size')
                    if int(size) >= 1000:
                        return json.dumps({'code': 1, 'errmsg': 'you input size too big '})
                sql = "SELECT %s FROM user limit %d,%d" % (','.join(fields),int(offset),int(size))
                app.config['cursor'].execute(sql)
                for row in app.config['cursor'].fetchall():
                    for i, k in enumerate(fields):
                        user[k] = row[i]
                    users.append(user)
                app.config['cursor'].execute("select  count(0) from user")
                count=int(app.config['cursor'].fetchone()[0])
                util.write_log(name, 'get_all_users')
                return json.dumps({'code': 0, 'users': users,'count':count})
            else:    #普通用户和管理员都是通过自己的登陆用户名查询自己的信息
                sql = 'SELECT %s FROM user where username="%s"' % (','.join(fields),name)
                app.config['cursor'].execute(sql)
                res = app.config['cursor'].fetchone()    #返回结果为元组(id,username,……)
                for i,k in enumerate(fields):     #取出元组的值及对应的索引号 0.1,2……
                    user[k]=res[i]    #fields中的列名作为user字典的k,索引作为数据库返回列表的k,实现字典赋值
                util.write_log(name, 'get_one_users') 
                return json.dumps({'code':0,'users':user})
        except:
            logging.getLogger().error("Get users list error: %s" % traceback.format_exc())
            return json.dumps({'code':1,'errmsg':'Get users error'})

##############  update user for admin and user ################################
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            data = json.loads(data)
            if  util.role(name):    #admin  update from user_id
                if not  data.has_key('user_id'):
                    return json.dumps({'code':1,'errmsg':'must input user_id'})
                else:
                    user_id = data['user_id']
                    if not util.if_userid_exist(user_id): 
                        return json.dumps({'code':1,'errmsg':'User is not exist'})
                    sql = 'update user set username="%(username)s",name="%(name)s", \
                            email="%(email)s",mobile="%(mobile)s" where id=%%d' % data %user_id
            else:                      #user update from his name
                sql = 'update user set username="%(username)s",name="%(name)s",email="%(email)s", \
                        mobile="%(mobile)s" where username="%%s"' % data %name
            app.config['cursor'].execute(sql)
            util.write_log(name,'update user %s' % data['username'])
            return json.dumps({'code':0,'result':'update %s success' % data['username']})
        except:
            logging.getLogger().error('update user error : %s' % traceback.format_exc())
            return json.dumps({'code':1,'errmsg':'update user error'})

#############  Create user for admin ################################
    elif request.method == 'POST':
        try:
            if not util.role(name):
                return json.dumps({'code':1,'errmsg':'you not admin '})
            data = request.get_json()
            data = json.loads(data)
            fields, values = [], []
            password = '3b53871ffb407966fc330307500ce968'
            for k, v in data.items():
                fields.append(k)
                values.append("'%s'" % v)
            sql = "INSERT INTO user (%s,password) VALUES (%s,'%s')" %  \
                    (','.join(fields), ','.join(values),password)
            app.config['cursor'].execute(sql)
            util.write_log(name, "create_user %s" % data['username'])
            return json.dumps({'code': 0, 'result': 'Create %s success' % data['username']})
        except:
            logging.getLogger().error("Create user error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': 'Create user error'})

#############  DELETE  user for admin ###########################
    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            data = json.loads(data)
            if not util.role(name):
                logging.getLogger().warning("You are not admin,Request forbiden")
                return json.dumps({'code':1,'errmsg':'You are not admin,Request forbiden'})
            else:
                if not  data.has_key('user_id'):
                    return json.dumps({'code':1,'errmsg':'must input user_id'})
                else:
                    user_id = data['user_id']
            if not util.if_userid_exist(user_id):
                return json.dumps({'code':1,'errmsg':'User is not exist'})
            sql = "DELETE FROM user where id = %d" % (user_id) 
            app.config['cursor'].execute(sql)
            util.write_log(name,'delete user %d' % user_id)
            return json.dumps({'code':0,'result':'delte %d success' % user_id})
        except:
            logging.getLogger().error('delete user error : %s' % traceback.format_exc())
            return json.dumps({'code':1,'errmsg':'delete user error'})
   
    return json.dumps({'code': 1, 'errmsg': "Cannot support '%s' method" % request.method })

@app.errorhandler(404)
def page_not_found(e):
    return json.dumps({'code':1,'errmsg':'your request is not found'})
 #   return render_template('404.html'), 404 
    

@app.errorhandler(500)
def internal_server_error(e):
    return json.dumps({'code':1,'errmsg':'server is too busy'})
#    return render_template('500.html'), 500 
