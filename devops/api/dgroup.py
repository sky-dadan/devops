#coding:utf-8
import json
import logging
import traceback

import util
from flask import Flask,request
from . import app


@app.route('/api/group',methods=['GET','PUT','DELETE'])
def group_manager():
	try:
		authorization=request.headers['authorization']
		name=util.validate(authorization,app.config['passport_key'])
		if not name :
			logging.getLogger().warining("Request forbiden")
			return json.dumps({'code':1,'errmsg':"User validate error"})
	except:
		logging.getLogger().warning("Validate error: %s" % traceback.format_exc())
		return json.dumps({'code':1,'errmsg':'User Validate error'})
	
#	user=session.get('user')
#	sql="select role from user where username='%s'"  %  (user)
#	app.config['cursor'].execute(sql)
#	for i in app.config['cursor'].fetchone():
#		user_role=int(i)
	
	user_role=1
	if request.method=='DELETE'  and  user_role==1:
		try:
			del_groups=request.get_data()
			del_groups=json.loads(del_groups)
			fields, values=[],[]
			field=del_groups.keys()[0]
			values=del_groups[field]
#			sql="delete from group where name=%s  " 
			for d_group in values:
				sql='delete from groups where name="%s"' % d_group
				app.config['cursor'].execute(sql)	
				util.write_log(name,"delete group %s" %  d_group )
			return json.dumps({'code':0,'result':'successful','values':values})
		except:
			logging.getLogger().error("Create user error: %s" % traceback.format_exc())
			return json.dumps({'code': 1, 'errmsg': 'Create user error'})

	if request.method=='PUT':
		try:
			s_data=request.get_data()
			s_data=json.loads(s_data)
			s_username=s_data.values()[0]		
			s_result=[]
			sql="select name,name_cn  from groups  where id=(select group_id from user_group where user_id =(select id from user where username='%s'))"   %  s_username
			app.config['cursor'].execute(sql)
			for g_name in app.config['cursor'].fetchone():
				s_result.append(g_name)
			util.write_log(name,"select %s belong to group"  % s_username)
			return json.dumps({'code':0,'result':'select successful','g_name':s_result})
		except:
			logging.getLogger().error("select group error:%s" %  traceback.format_exc())
			return json.dumps({'code': 1, 'errmsg': 'select user_group  error'})
			
			
			
