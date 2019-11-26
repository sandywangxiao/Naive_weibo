import os
import sys
sys.path.append('../src')
import GstoreConnector
import json
import random

gStoreusername = "root"
gStorepassword = "123456"

prefix = "<file:///media/bei/309cad20-ab9c-471f-9af0-70990574215d/bei/GraphData/d2rq/vocab/"
weibo_prefix = "<file:///media/bei/309cad20-ab9c-471f-9af0-70990574215d/bei/GraphData/d2rq/weiboo.nt#weibo/"
user_prefix = "<file:///media/bei/309cad20-ab9c-471f-9af0-70990574215d/bei/GraphData/d2rq/weiboo.nt#user/"
userrelation = "<file:///media/bei/309cad20-ab9c-471f-9af0-70990574215d/bei/GraphData/d2rq/weiboo.nt#userrelation/"
integer = "^^<http://www.w3.org/2001/XMLSchema#integer>"
class GstoreDb():
	def __init__(self):
		self.gc = GstoreConnector.GstoreConnector("127.0.0.1", 9000)
		self.ret = self.gc.build("weibo", "data/weibo.nt", gStoreusername, gStorepassword)
		self.ret = self.gc.load("weibo", gStoreusername, gStorepassword)
		self.all_ids = self.get_all_ids()
		self.all_ids_num = len(self.all_ids)
		self.all_weibo_ids = self.get_all_weibo_ids()
		self.current_uid = ""
		self.islogin = False
		

	def get_current_wid(self):
		wid = random.randrange(12211102252038666746, 22211102252038666746) 
		if wid  not in self.all_weibo_ids:
			return wid
		else:
			return self.get_current_wid()


	def insert_data(self,s,p,o):
		sparql = "insert data\
		{\
		%s %s %s.\
		}" %(s,p,o)
		ql = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql)
		return ql

	def get_all_ids(self):
		### 得到所有idS
		sparql = "select distinct ?uid where\
		{\
		?s %suser_uid> ?uid.\
		}" % (prefix)
		print("11111")
		id_q = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql)
		ids = json.loads(id_q)
		ids = ids['results']['bindings']
		all_ids = [x['uid']['value'] for x in ids if x!={}]
		return all_ids

	def get_all_weibo_ids(self):
		### 得到所有idS
		sparql = "select distinct ?weiboid where\
		{\
		?s %sweibo_mid> ?weiboid.\
		}" % (prefix)
		#print("11111")
		id_q = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql)
		ids = json.loads(id_q)
		ids = ids['results']['bindings']
		all_weibo_ids = [x['weiboid']['value'] for x in ids if x!={}]
		return all_weibo_ids

	def validate(self,userid, password, repassword=None):
		### 注册时验证密码两次输入一致，以及userid是否占用
		print("userid",type(userid))
		print("password",type(password))
		if repassword:
			if userid in self.all_ids:
				return '用户id已经存在'
			else:
				if len(userid) < 2:
					return '用户名id至少2个字符'
				elif len(password) < 6:
					return '密码长度至少6个字符'
				elif password != repassword:
					return '两次密码不一致'
				else:
					return '注册成功'
		###登录时验证用户ID是否存在以及密码是否正确
		else:
			if userid in self.all_ids:
				sparql = "select ?pd where\
				{\
				?s %suser_uid> '%s'.\
				?s %suser_pd> ?pd.\
				}" % (prefix,userid,prefix)
				#print(sparql)
				password_true = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql)
				#print(password_true)
				q_json = json.loads(password_true)
				password_true = q_json['results']['bindings'][0]['pd']['value']
				if password_true == password:
					return '登录成功'
				else:
					return '密码错误'
			else:
				return '用户id不存在'


	def register(self,userid,username,password):
		user_id_s = "%s%s>" %(user_prefix,userid)
		user_id_p = "%suser_uid>" %(prefix)
		user_name_p = "%suser_name>" %(prefix)
		user_pd_p = "%suser_pd>" %(prefix)
		user_friend_p = "%suser_friendsnum>" %(prefix)
		user_follower_p = "%suser_followersnum>" %(prefix)
		id_out = self.insert_data(user_id_s,user_id_p,"'%s'" % userid)
		name_out = self.insert_data(user_id_s,user_name_p,"'%s'" % username)
		pd_out = self.insert_data(user_id_s,user_pd_p,"'%s'" % password)
		friend_out = self.insert_data(user_id_s,user_friend_p,"'%d'" % (0))
		follower_out = self.insert_data(user_id_s,user_follower_p,"'%d'" % (0))
		self.all_ids.append(userid)


	def post_weibo(self,topic,weibotext,weibodate,weibouid):
		current_wid = self.get_current_wid()
		weibo_id_s = "%sweiboo.nt#weibo/%d>" %(prefix,current_wid)
		print(current_wid)
		sparql = "insert data \
		{\
		%s %sweibo_mid> '%d'.\
		%s %sweibo_topic> '%s'.\
		%s %sweibo_text> '%s'.\
		%s %sweibo_date> '%s'.\
		%s %sweibo_uid> '%s'.\
		%s %sweibo_attitudesnum> '%d'.\
		%s %sweibo_commentsnum> '%d'.\
		}" % (weibo_id_s,prefix,current_wid,\
			weibo_id_s,prefix,topic,\
			weibo_id_s,prefix,weibotext,\
			weibo_id_s,prefix,weibodate,\
			weibo_id_s,prefix,weibouid,\
			weibo_id_s,prefix,0,\
			weibo_id_s,prefix,0,\
			)
		print(sparql)
		ql_res = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql)

		print("out1",ql_res)


	def get_weibos(self,userid):
		sparql = "select  ?date ?text ?zan_num ?comment_num where\
		{\
		?s %sweibo_uid> '%s'.\
		?s %sweibo_date> ?date.\
		?s %sweibo_text> ?text.\
		?s %sweibo_attitudesnum> ?zan_num.\
		?s %sweibo_commentsnum> ?comment_num.\
		}" % (prefix,userid,prefix,prefix,prefix,prefix)
		ql_res = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql)
		ql_res = json.loads(ql_res)
		weibos = ql_res['results']['bindings']
		return weibos[::-1]#,userid

	def get_friend_weibos(self,userid):

		sparql = "select  ?friendid ?date ?text ?zan_num ?comment_num where\
		{\
		?relation %suserrelation_suid> '%s'.\
		?relation %suserrelation_tuid> ?friendid.\
		?s %sweibo_uid> ?friendid.\
		?s %sweibo_date> ?date.\
		?s %sweibo_text> ?text.\
		?s %sweibo_attitudesnum> ?zan_num.\
		?s %sweibo_commentsnum> ?comment_num.\
		}" % (prefix,userid,prefix,prefix,prefix,prefix,prefix,prefix)
		ql_res = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql)
		ql_res = json.loads(ql_res)
		weibos = ql_res['results']['bindings']
		return weibos[::-1]#,userid


	def get_recommand_friends(self):
		####10个推荐人
		sparql = "select   ?friendid ?username ?followersnum ?friendsnum  where\
		{\
        ?s %suser_uid> ?friendid.\
        ?s %suser_name> ?username.\
        ?s %suser_followersnum> ?followersnum.\
        ?s %suser_friendsnum> ?friendsnum.\
		}limit 1000" % (prefix,prefix,prefix,prefix)
		ql_res = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql)
		ql_res = json.loads(ql_res)
		recommand_friends = random.sample(ql_res['results']['bindings'],10)
		return recommand_friends


	def get_friends(self,userid):
		####我的好友
		sparql = "select  ?friendid ?username ?followersnum ?friendsnum  where\
		{\
		?relation %suserrelation_suid> '%s'.\
		?relation %suserrelation_tuid> ?friendid.\
        ?s %suser_uid> ?friendid.\
        ?s %suser_name> ?username.\
        ?s %suser_followersnum> ?followersnum.\
        ?s %suser_friendsnum> ?friendsnum.\
		}" % (prefix,userid,prefix,prefix,prefix,prefix,prefix,)
		ql_res = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql)
		print(ql_res)
		ql_res = json.loads(ql_res)
		friends = ql_res['results']['bindings']
		return friends


	def input_basic_info(self,user):
		user_id = "%s%s>" %(user_prefix,user['userid'])
		sparql = "insert data \
		{\
		%s %suser_gender> '%s'.\
		%s %suser_city> '%s'.\
		%s %suser_province> '%s'.\
		%s %suser_location> '%s'.\
		}" % (user_id,prefix,user['gender'],user_id,prefix,user['city'],user_id,prefix,user['province'],user_id,prefix,user['location'])
		ql_res = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql)
		print(ql_res)


	def out_basic_info(self,userid):
		user_id = "%s%s>" %(user_prefix,userid)
		sparql = "select ?gender ?city ?province ?location where\
		{\
		%s %suser_gender> ?gender.\
		%s %suser_city> ?city.\
		%s %suser_province> ?province.\
		%s %suser_location> ?location.\
		}" % (user_id,prefix,user_id,prefix,user_id,prefix,user_id,prefix)
		ql_res = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql)
		ql_res = json.loads(ql_res)
		#若为空
		outputs = {}
		if ql_res['results']['bindings']==[]:
			for i in ['gender','city','province','location']:
				outputs[i] = None
		else:
			for i in ['gender','city','province','location']:
				outputs[i] = ql_res['results']['bindings'][0][i]['value']
				print(outputs[i])
		return outputs 


	def follow(self,user1_id,user2_id):
		sparql1 = """insert data \
				{{\
				{userrelation}/{user1_id}/{user2_id}>  {prefix}userrelation_suid> \"{user1_id}\". \
				{userrelation}/{user1_id}/{user2_id}>  {prefix}userrelation_tuid> \"{user2_id}\". \
				}}""" \
				.format(userrelation=userrelation,user1_id=user1_id,user2_id=user2_id,prefix=prefix)
		res1 = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql1)

		sparql2 = "select ?friend_num ?followers_num where\
					{\
					%s%s> %suser_friendsnum> ?friend_num.\
					%s%s> %suser_followersnum> ?followers_num.\
					}"% (user_prefix,user1_id,prefix,user_prefix,user2_id,prefix)
		res2 = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql2)
		content = json.loads(res2)['results']['bindings']
		friend_num = int(content[0]['friend_num']['value'])
		follower_num = int(content[0]['followers_num']['value'])

		sparql3 = "delete where\
					{\
					%s%s> %suser_friendsnum> ?friend_num.\
					%s%s> %suser_followersnum> ?followers_num.\
					}" % (user_prefix,user1_id,prefix,user_prefix,user2_id,prefix)
		res3 = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql3)
		#print(res3)

		sparql4 = "insert data\
					{\
					%s%s> %suser_friendsnum> '%d'.\
					%s%s> %suser_followersnum> '%d'.\
					}" % (user_prefix,user1_id,prefix,friend_num+1,user_prefix,user2_id,prefix,follower_num+1)
		res4 = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql4)
		#print(res4)



	def unfollow(self,user1_id,user2_id):

		sparql2 = "select ?friend_num ?followers_num where\
					{\
					%s%s> %suser_friendsnum> ?friend_num.\
					%s%s> %suser_followersnum> ?followers_num.\
					}"% (user_prefix,user1_id,prefix,user_prefix,user2_id,prefix)
		res2 = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql2)
		#print(res2)
		content = json.loads(res2)['results']['bindings']
		friend_num = int(content[0]['friend_num']['value'])
		follower_num = int(content[0]['followers_num']['value'])

		sparql3 = "delete where\
					{\
					%s%s> %suser_friendsnum> ?friend_num.\
					%s%s> %suser_followersnum> ?followers_num.\
					}" % (user_prefix,user1_id,prefix,user_prefix,user2_id,prefix)
		res3 = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql3)
		#print(res3)

		sparql4 = "insert data\
					{\
					%s%s> %suser_friendsnum> '%d'.\
					%s%s> %suser_followersnum> '%d'.\
					}" % (user_prefix,user1_id,prefix,friend_num-1,user_prefix,user2_id,prefix,follower_num-1)
		res4 = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql4)
		#print(res4)

		sparql1 = """delete where \
				{{\
				{userrelation}/{user1_id}/{user2_id}>  {prefix}userrelation_suid> \"{user1_id}\". \
				{userrelation}/{user1_id}/{user2_id}>  {prefix}userrelation_tuid> \"{user2_id}\". \
				}}""" \
				.format(userrelation=userrelation,user1_id=user1_id,user2_id=user2_id,prefix=prefix)
		res1 = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql1)
		#print(res1)


	def user1_relation_user2(self,user1_id,user2_id):

		sparql0 ="""select ?relation where \
				{{ \
				?relation {prefix}userrelation_suid> \"{user1_id}\". \
				?relation {prefix}userrelation_tuid> \"{user2_id}\".\
				}}""".format(prefix=prefix,user1_id=user1_id,user2_id=user2_id)
		id0s = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql0)
		if id0s==[]:
			zero_hop = False
		else:
			zero_hop = True
		print(zero_hop)

		sparql1 ="""select ?id1 where \
				{{ \
				?relation1 {prefix}userrelation_suid> \"{user1_id}\". \
				?relation1 {prefix}userrelation_tuid> ?id1.\
				?relation2 {prefix}userrelation_suid> ?id1. \
				?relation2 {prefix}userrelation_tuid> \"{user2_id}\".\
				}}""".format(prefix=prefix,user1_id=user1_id,user2_id=user2_id)

		id1s = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql1)
		hjson1 = json.loads(id1s)
		one_hop = hjson1['results']['bindings']


		sparql2 ="""select ?id1 ?id2 where \
				{{ \
				?relation1 {prefix}userrelation_suid> \"{user1_id}\". \
				?relation1 {prefix}userrelation_tuid> ?id1.\
				?relation2 {prefix}userrelation_suid> ?id1. \
				?relation2 {prefix}userrelation_tuid> ?id2.\
				?relation3 {prefix}userrelation_suid> ?id2. \
				?relation3 {prefix}userrelation_tuid> \"{user2_id}\".\

				}}""".format(prefix=prefix,user1_id=user1_id,user2_id=user2_id)

		id2s = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql2)
		hjson2 = json.loads(id2s)
		two_hop = hjson2['results']['bindings']

		sparql3 ="""select ?id1 ?id2 ?id3 where \
				{{ \
				?relation1 {prefix}userrelation_suid> \"{user1_id}\". \
				?relation1 {prefix}userrelation_tuid> ?id1.\
				?relation2 {prefix}userrelation_suid> ?id1. \
				?relation2 {prefix}userrelation_tuid> ?id2.\
				?relation3 {prefix}userrelation_suid> ?id2. \
				?relation3 {prefix}userrelation_tuid> ?id3.\
				?relation4 {prefix}userrelation_suid> ?id3. \
				?relation4 {prefix}userrelation_tuid> \"{user2_id}\".\

				}}""".format(prefix=prefix,user1_id=user1_id,user2_id=user2_id)

		id3s = self.gc.query(gStoreusername, gStorepassword, "weibo",sparql3)
		hjson3 = json.loads(id3s)
		three_hop = hjson3['results']['bindings']
		return zero_hop,one_hop,two_hop,three_hop

