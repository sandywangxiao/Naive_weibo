import os
from flask import Flask,url_for,redirect,flash,request, render_template
import time
import json
import weiboclass

gStoreusername = "root"
gStorepassword = "123456"


db = weiboclass.GstoreDb()
app = Flask(__name__)

app.config['SECRET_KEY'] = '123456'


@app.route('/',methods=['GET','POST'])
def home():
	return render_template('base.html')

@app.route('/register',methods=['GET','POST'])
def register():
	if request.method=='GET':
		return render_template('register.html')
	else:
		userid = request.form.get('userid')
		username = request.form.get('username')
		password = request.form.get('password')
		repassword = request.form.get('repassword')
		message= db.validate(userid,password,repassword)
		print(message)
		flash(message)
		if message == '注册成功':
			db.register(userid,username,password)  
			flash(message)
			db.islogin=True
			return redirect(url_for('login'))
		else:
			flash(message)
			return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	else:
		userid = request.form.get('userid')
		password = request.form.get('password')
		message = db.validate(userid, password)
		print(message)
		flash(message)
		if message == '登录成功':
			flash(message)
			db.current_uid = userid
			db.islogin=True
			return redirect(url_for('out_info',userid=userid))
		else:
			flash(message)
			return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
	db.islogin=False
	if request.method == 'GET':
		return render_template('login.html')
	else:
		userid = request.form.get('userid')
		password = request.form.get('password')
		message = db.validate(userid, password)
		print(message)
		flash(message)
		if message == '登录成功':
			flash(message)
			db.current_uid = userid
			db.islogin=True
			return redirect(url_for('out_info',userid=userid))
		else:
			flash(message)
			return render_template('login.html')
@app.route('/out_info/<userid>', methods=['GET'])
def out_info(userid):
	####用户资料
	user = db.out_basic_info(userid)
	return render_template('get_info.html',user = user,userid = userid ,islogin=db.islogin)


@app.route('/put_info/<userid>', methods=['GET', 'POST'])
def insert_info(userid):
	####（输入用户信息）
	if request.method == 'GET':
		return render_template('put_info.html',userid=userid,islogin=db.islogin)
	else:
		user = {}
		user['userid'] = userid
		user['gender'] = request.form.get('gender')
		user['city'] = request.form.get('city')
		user['province'] = request.form.get('city')
		user['location'] = request.form.get('location')
		db.input_basic_info(user)
		return  render_template('get_info.html',user = user,userid = userid ,islogin=db.islogin)


@app.route('/login/<userid>', methods=['GET','POST']) #,
def post_myweibo(userid):
	###发布微博
	if request.method == 'GET':
		return render_template('myweibo.html',userid=userid,islogin=db.islogin)
	#发微博,从页面获取微博主题和内容
	else:
		topic = request.form.get('topic')
		weibotext = request.form.get('weibotext')
		weibodate = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
		weibouid = userid
		#print("11111")
		print(weibouid)
		db.post_weibo(topic,weibotext,weibodate,weibouid)
		#发成功后展示更新后的用户页面
		return redirect(url_for('get_myweibo',userid=userid))

@app.route('/weibos/<userid>', methods=['GET','POST']) 
def get_myweibo(userid):
	###我的微博
	if request.method == 'GET':
		#print("tttttttt")
		weibos = db.get_weibos(userid)
		print("ql out:")
		print(weibos)
		#print("lllllll")
		return render_template('get_weibos.html',userid = userid,weibos = weibos,islogin=db.islogin)
	else:
		return redirect(url_for('post_myweibo',userid=userid))

@app.route('/friendsweibos/<userid>', methods=['GET','POST']) 
def get_friend_weibos(userid):
	### 好友微博
	if request.method == 'GET':
		#print("tttttttt")
		weibos = db.get_friend_weibos(userid)
		print("ql out:")
		print(weibos)
		#print("lllllll")
		return render_template('get_friend_weibos.html',userid = userid,weibos = weibos,islogin=db.islogin)
	else:
		return render_template('get_friend_weibos.html',userid = userid,weibos = weibos,islogin=db.islogin)


@app.route('/recommandfriend/<userid>', methods=['GET','POST']) 
def get_recommand_friends(userid):
	### 推荐好友
	if request.method == 'GET':
		#print("tttttttt")
		recommandfriends = db.get_recommand_friends()
		print("ql out:")
		print(recommandfriends)
		#print("lllllll")
		return render_template('get_recommand_friends.html',userid = userid,recommandfriends = recommandfriends,islogin=db.islogin)
	else:
		return render_template('get_recommand_friends.html',userid = userid,recommandfriends = recommandfriends,islogin=db.islogin)

@app.route('/friends/<userid>', methods=['GET','POST']) 
def get_friends(userid):
	###我的好友
	if request.method == 'GET':
		#print("tttttttt")
		friends = db.get_friends(userid)
		print("ql out:")
		print(friends)
		#print("lllllll")
		return render_template('get_friends.html',userid = userid,friends = friends,islogin=db.islogin)
	else:
		return render_template('get_friends.html',userid = userid,friends = friends,islogin=db.islogin)


@app.route('/friendsfollow/<userid>/<userid2>', methods=['GET']) 
def follow_friends(userid,userid2):
	###关注好友
	if request.method == 'GET':
		db.follow(userid,userid2)
		return redirect(url_for('get_friends',userid=userid,islogin=db.islogin))



@app.route('/friendsunfollow/<userid>/<userid2>', methods=['GET']) 
def unfollow_friends(userid,userid2):
	###取消关注好友
	if request.method == 'GET':
		db.unfollow(userid,userid2)
		return redirect(url_for('get_friends',userid=userid,islogin=db.islogin))



@app.route('/friendsqury', methods=['GET','POST']) 
def get_relations():
	if db.islogin:
		# islogin =db.islogin
		if request.method == 'GET':

			return render_template('relations_input.html',islogin=db.islogin,userid=db.current_uid)
		if request.method == 'POST':
			userid1 = request.form.get('userid1')
			userid2 = request.form.get('userid2')
			out = db.user1_relation_user2(userid1,userid2)
			#发成功后展示更新后的用户页面
			return render_template('relations.html',userid1=userid1,userid2=userid2,out=out,islogin=db.islogin,userid=db.current_uid)
	else:
		if request.method == 'GET':

			return render_template('relations_input.html',islogin=db.islogin)
		if request.method == 'POST':
			userid1 = request.form.get('userid1')
			userid2 = request.form.get('userid2')
			out = db.user1_relation_user2(userid1,userid2)
			#发成功后展示更新后的用户页面
			return render_template('relations.html',userid1=userid1,userid2=userid2,out=out,islogin=db.islogin)


if __name__=='__main__':

	app.run(debug=True)

