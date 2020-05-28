# -*- coding: utf-8 -*-
import uuid
from flask import Flask, jsonify, request
import flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask import Flask
#from flask_cors import CORS
import json
from flask_cors import *
import pymysql
import datetime
from sqlalchemy import func


def getday_in_int():
    current_time = datetime.datetime.now()
    day = current_time.strftime("%Y%m%d")
    return day

def gettime_in_int():
    current_time = datetime.datetime.now()
    time = current_time.strftime("%H%M")
    return time



# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

app.config['SECRET_KEY'] ='123456'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:123456@127.0.0.1:3306/managesystem'
#设置这一项是每次请求结束后都会自动提交数据库中的变动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
#实例化
db = SQLAlchemy(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

import contextlib
#定义上下文管理器，连接后自动关闭连接
@contextlib.contextmanager
def mysql(host='127.0.0.1', port=3306, user='root', passwd='123456', db='managesystem',charset='utf8'):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset,autocommit=True)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        yield cursor
    finally:
        conn.commit()
    cursor.close()
    conn.close()

class RegInfo(db.Model):
    __tablename__ = 'registration_information'
    ID_person = db.Column(db.Integer, primary_key=True,nullable=False)
    name = db.Column(db.String(50))
    status = db.Column(db.String(50))
    age = db.Column(db.Integer)
    date_register = db.Column(db.Integer)
    time_register = db.Column(db.Integer)
    password = db.Column(db.String(50))
    def __repr__(self):
        return '<RegInfo {}>'.format(self.ID_person)


class LocCurr(db.Model):
    __tablename__ = 'location_current'
    ID_visit = db.Column(db.Integer, primary_key=True,nullable=False)
    ID_person = db.Column(db.Integer, db.ForeignKey(RegInfo.ID_person))
    longitude_current = db.Column(db.Float)
    latitude_current = db.Column(db.Float)
    date_current = db.Column(db.Integer)
    time_current = db.Column(db.Integer)
    date_start = db.Column(db.Integer)
    time_start = db.Column(db.Integer)
    time_stay = db.Column(db.Integer)
    def __repr__(self):
        return '<RegInfo {}>'.format(self.ID_visit)

class LocHist(db.Model):
    __tablename__ = 'location_history'
    ID_history = db.Column(db.Integer, primary_key=True,nullable=False)
    ID_visit = db.Column(db.Integer, db.ForeignKey(LocCurr.ID_visit))
    ID_person = db.Column(db.Integer, db.ForeignKey(RegInfo.ID_person))
    longitude_history = db.Column(db.Float)
    latitude_history = db.Column(db.Float)
    date_history = db.Column(db.Integer)
    time_history = db.Column(db.Integer)
    flag = db.Column(db.String(20))
    def __repr__(self):
        return '<RegInfo {}>'.format(self.ID_history)


class TimeAlloc(db.Model):
    __tablename__ = 'time_allocation'
    ID_time = db.Column(db.Integer, primary_key=True,nullable=False)
    ID_visit = db.Column(db.Integer, db.ForeignKey(LocCurr.ID_visit))
    time_stay = db.Column(db.Integer)
    date_time = db.Column(db.Integer)
    def __repr__(self):
        return '<RegInfo {}>'.format(self.ID_time)



@app.route('/wx/login',methods=['GET','POST'])
def loginwx():
    if request.method == 'POST':
        post_data = request.get_json()
        name = post_data.get('data')
        #name = 'hello'
        res = login(name=name)
        if res[0]==True:
            status = res[2]
            response = {'code':20000,'status':status}
            return jsonify(response)
        else:
            res = register(name=name,status='访客')
            if res[0]==True:#注册成功
                response = {'code':20000,'status':'访客'}
                return jsonify(response)
            else:
                response = {'code':60204,'data':'error'}
                return jsonify(response)
    return jsonify({'code':60204,'data':'error'})




@app.route('/vue-admin-template/user/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        post_data = request.get_json()
        #post_data = {'username':'张西珩','password':'123456'}
        res = login(name=post_data.get('username'),password=post_data.get('password'))
        if (res[0] == True):
            response={"code": 20000,"data": {"token":"admin-token"}}
            return jsonify(response)
        else :
            response = {"code": 60204,'message': '用户名或密码错误'}
            return jsonify(response)
    else:
        return jsonify({"code": 60204,'message': 'error'})

@app.route('/vue-admin-template/user/logout',methods=['POST'])
def logout():
    response={"code": 20000,"data": "success"}
    return jsonify(response)




@app.route('/vue-admin-template/getUserinfo/<name>', methods=['GET'])
def getUserinfo(name):
    res = checkUser(name)
    if (res[0] == True):
        status = res[1].status
        if (status == '保卫处'):
            response = {"code": 20000,"data": {'roles': ['admin'],'introduction': 'I am a super administrator',\
            'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif', 'name': 'Super Admin'}}
            return jsonify(response)
        if (status == '门卫'):
            response = {"code": 20000,"data": {'roles': ['editor'],'introduction': 'I am an editor',\
            'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif', 'name': 'Normal Editor'}}
            return jsonify(response)
        else:
            response = {"code": 60204,'message': 'not admin or editor.'}
            return jsonify(response)
    else:
        response = {"code": 60204,'message': 'Account and password are incorrect.'}
        return jsonify(response)



@app.route('/vue-admin-template/charts', methods=['GET'])
def charts():
    d7 = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    d6 = d7 - oneday
    d5 = d6 - oneday
    d4 = d5 - oneday
    d3 = d4 - oneday
    d2 = d3 - oneday
    d1 = d2 - oneday
    d1=d1.strftime("%Y%m%d")
    d2=d2.strftime("%Y%m%d")
    d3=d3.strftime("%Y%m%d")
    d4=d4.strftime("%Y%m%d")
    d5=d5.strftime("%Y%m%d")
    d6=d6.strftime("%Y%m%d")
    d7=d7.strftime("%Y%m%d")
    n1 = showCountOneDay(d1)
    n2 = showCountOneDay(d2)
    n3 = showCountOneDay(d3)
    n4 = showCountOneDay(d4)
    n5 = showCountOneDay(d5)
    n6 = showCountOneDay(d6)
    n7 = showCountOneDay(d7)
    a1 = showCountAll(d1)
    a2 = showCountAll(d2)
    a3 = showCountAll(d3)
    a4 = showCountAll(d4)
    a5 = showCountAll(d5)
    a6 = showCountAll(d6)
    a7 = showCountAll(d7)
    p1 = showCountInSpecificPlace('一餐',date=getday_in_int())
    p2 = showCountInSpecificPlace('二餐',date=getday_in_int())
    p3 = showCountInSpecificPlace('三餐',date=getday_in_int())
    p4 = showCountInSpecificPlace('四餐',date=getday_in_int())
    p5 = showCountInSpecificPlace('玉兰苑',date=getday_in_int())
    p6 = showCountInSpecificPlace('新图',date=getday_in_int())
    p7 = showCountInSpecificPlace('电院',date=getday_in_int())
    pa = p1+p2+p3+p4+p5+p6+p7
    response = {'code':20000,'data':{'line':{'dates':[d1,d2,d3,d4,d5,d6,d7],'newVisits':[n1,n2,n3,n4,n5,n6,n7],\
        'allVisits':[a1,a2,a3,a4,a5,a6,a7],'panel':{'new':n7,'all':a7,'location':pa},'pie':{'locationName':\
        ['一餐','二餐','三餐','四餐','玉兰苑','新图','电院'],'peopleNum':[p1,p2,p3,p4,p5,p6,p7]}}}}
    return jsonify(response)


@app.route('/vue-admin-template/usertable', methods=['GET'])
def usertable():
    users = showVisitorNow()
    length = len(users)
    items =[]
    for user in users:
        id=user.ID_person
        name=RegInfo.query.filter_by(ID_person=id).first().name
        age = RegInfo.query.filter_by(ID_person=id).first().age
        ds = str(user.date_start) +' ' + str(user.time_start)
        ds2 = datetime.datetime.strptime(ds,"%Y%m%d %H%M")
        dn = str(user.date_current) + ' ' + str(user.time_current)
        dn = datetime.datetime.strptime(dn,"%Y%m%d %H%M")
        timeused = dn-ds2
        secondsused = timeused.total_seconds()
        secondsall= int(user.time_stay/100)*3600 + (user.time_stay%100)*60
        if(secondsused<secondsall):
            sta = '正常'
        else:
            sta = '过期'
        items.append({'ID':id,"name":name,"startTime":ds,'status':sta,'age':age})

    response = {'code': 20000,'data': {'total':length,'items':items}}
    return jsonify(response)

@app.route('/vue-admin-template/locationtable', methods=['GET'])
def locationtable():
    items=[]
    places = {'一餐','二餐','三餐','四餐','玉兰苑','新图','电院'}
    length = len(places)
    for place in places:
        num = showCountInSpecificPlace(place)
        alertNum = 50
        if (num>alertNum):
            status = '警戒'
        else:
            status = '正常'
        items.append({'locationName':place,'status':status,'enterNumber':num,'alertNumber':alertNum})

    response={'code':20000,'data':{'total':length,'items':items}}
    return jsonify(response)




def register(name,status='访客',age=20,password='123456',date_register=getday_in_int(),time_register=gettime_in_int()):
    if (RegInfo.query.filter_by(name=name).count()>0):
        return (False,"name already registered")
    new_user = RegInfo(name=name,status=status,age=age,date_register=date_register,time_register=time_register,password=password)
    try:
        db.session.add_all([new_user])
        db.session.commit()
        return (True,new_user)
    except:
        return (False,"register failed")

def checkUser(name):
    if (RegInfo.query.filter_by(name=name).count()>1):
        print("alert! more than 1 users match this name, choose the first one")
    if (RegInfo.query.filter_by(name=name).count()==0):
        return(False,"no this user")
    user = RegInfo.query.filter_by(name=name).first()
    return (True, user)

def login(name,password='123456'):
    res1=checkUser(name)
    if (res1[0]==False):#用户不存在
        return (False,"no this user")
    else:
        if (password == res1[1].password):
            return (True,res1[1].ID_person,res1[1].status)
        else:
            return (False,"password error")


def endVisitByName(name,longitude_current=121.426365,\
                   latitude_current=31.01966,date_current=getday_in_int(),time_current=gettime_in_int()):
    if(RegInfo.query.filter_by(name=name).count()!=1):
        return (False,"no such name")
    thisID = RegInfo.query.filter_by(name=name).first().ID_person
    return(endVisit(thisID,longitude_current=longitude_current,latitude_current=latitude_current,\
                    date_current=date_current,time_current=time_current))

def endVisit(ID_person,longitude_current=121.426365,\
                   latitude_current=31.01966,date_current=getday_in_int(),time_current=gettime_in_int()):
    if(RegInfo.query.filter_by(ID_person=ID_person).count()!=1):
        return (False,"no visit now")
    if (RegInfo.query.filter_by(ID_person=ID_person).first().status!='访客'):
        return (False,"this is not a visitor")
    try:
        ID_visit = LocCurr.query.filter_by(ID_person=ID_person).first().ID_visit
        time = LocCurr.query.filter_by(ID_person=ID_person).first().time_stay
        res = LocCurr.query.filter_by(ID_person=ID_person).delete()
        db.session.commit()
        res2 = recordVisit(ID_visit=ID_visit,ID_person=ID_person,longitude_current=longitude_current,latitude_current=latitude_current,\
                    date_current=date_current,time_current=time_current,flag='离开')
        res3 = (showTimeStay(ID_visit)[-1] > time)
        if (res==1 and res2[0] == True):
            if (res3):
                return (True,"delete success, but stay longer than allocation")
            else:
                return (True,"delete success")
        else:
            return (False,"delete failed")
    except:
        return(False,"no such ID_person")

def startVisitByName(name,longitude_current=121.426365,\
                   latitude_current=31.01966,time_stay=300,date_current=getday_in_int(),time_current=gettime_in_int(),\
               date_start=getday_in_int(),time_start=gettime_in_int()):
    if(RegInfo.query.filter_by(name=name).count()!=1):
        return (False,"no such name")
    thisID = RegInfo.query.filter_by(name=name).first().ID_person
    return startVisit(thisID,longitude_current,latitude_current,time_stay,date_current,time_current,date_start,time_start)


def startVisit(ID_person,longitude_current='121.426365',\
                   latitude_current='31.01966',time_stay=300,date_current=getday_in_int(),time_current=gettime_in_int(),\
               date_start=getday_in_int(),time_start=gettime_in_int()):
    '''
    默认是思源门地址，3h
    '''

    if(LocCurr.query.filter_by(ID_person=ID_person).count()>0):
        return (False,"this ID is still in visit time")
    else:
        res = RegInfo.query.filter_by(ID_person=ID_person).first()
        if(res.status!='访客'):
            return(False,"this is not a visitor")
        new_user = LocCurr(ID_person=ID_person,longitude_current=longitude_current,\
                   latitude_current=latitude_current,date_current=date_current,time_current=time_current,\
               date_start=date_start,time_start=time_start,time_stay=time_stay)
        #try:
        db.session.add_all([new_user])
        db.session.commit()
        res = recordVisit(ID_visit=new_user.ID_visit,ID_person=ID_person,longitude_current=longitude_current,\
            latitude_current=latitude_current,date_current=date_current,time_current=time_current,flag='进入')
        res2 = newTimeAlloc(ID_visit=new_user.ID_visit,time_stay=time_stay,date_time=date_current)
        if (res[0] == True and res2[0] == True):
            return (True,"new visit start")
        else:
            return (False,"record failed")
        #except:
            #return (False,"start new visit failed")

def updateVisitLocation(ID_person,longitude_current='121.426365',\
                   latitude_current='31.01966',date_current=getday_in_int(),time_current=gettime_in_int()):
    if(LocCurr.query.filter_by(ID_person=ID_person).count()!=1):
        return (False,"no visit now")
    currentuser = LocCurr.query.filter_by(ID_person=ID_person).first()
    currentuser.longitude_current=longitude_current
    currentuser.latitude_current=latitude_current
    currentuser.date_current=date_current
    currentuser.time_current=time_current
    fulltime = int(currentuser.time_stay/100)*60+currentuser.time_stay%100
    minnow = int(int(time_current)/100)*60+int(time_current)%100
    minin = int(currentuser.time_start/100)*60+currentuser.time_start%100
    minleft = fulltime - (minnow-minin)
    '''
    if(TimeAlloc.query.filter_by(ID_visit=currentuser.ID_visit).count()!=1):
        return (False,"no time allocation")
    fulltime = str(TimeAlloc.query.filter_by(ID_visit=currentuser.ID_visit).first().time_stay)
    fulltime = datetime.datetime.strptime(fulltime,"%H%M")
    ds = str(currentuser.date_start) +' ' + str(currentuser.time_start)
    ds = datetime.datetime.strptime(ds,"%Y%m%d %H%M")
    dn = str(date_current) + ' ' + str(time_current)
    dn = datetime.datetime.strptime(dn,"%Y%m%d %H%M")
    timeused = dn-ds
    timeleft = fulltime - timeused
    flag = timeleft.strftime("d")
    currentuser.time_stay = timeleft.strftime("%H%M")
    if(flag>1):
        currentuser.time_stay = 0
        '''
    try:
        db.session.commit()
        res = recordVisit(ID_visit=currentuser.ID_visit,ID_person=ID_person,longitude_current=longitude_current,latitude_current=latitude_current,\
                    date_current=date_current,time_current=time_current,flag='逗留')
        if (res[0] == True ):#and flag==0
            return(True,"update successfully",minleft)
        #elif (flag>1):
        #    return(True,"but time is running out")
        else:
            return(False,"record failed")
    except:
        return(False,"update failed")

def recordVisit(ID_visit,ID_person,longitude_current='121.426365',\
                   latitude_current='31.01966',date_current=getday_in_int(),time_current=gettime_in_int(),flag='逗留'):
    #if(LocCurr.query.filter_by(ID_person=ID_person).count()!=1):
    #    return(False,"no this visitor")
    #visitid = LocCurr.query.filter_by(ID_person=ID_person).first().ID_visit
    loc = LocHist(ID_visit=ID_visit,ID_person=ID_person,longitude_history=longitude_current,latitude_history=latitude_current,\
            date_history=date_current,time_history=time_current,flag=flag)
    #try:
    db.session.add_all([loc])
    db.session.commit()
    return (True,"record success")
    #except:
    #    return (False,"record failed")

def newTimeAlloc(ID_visit,time_stay=300,date_time=getday_in_int()):
    if (TimeAlloc.query.filter_by(ID_visit=ID_visit).count()>0):
        return (False,"already allocate time")
    ta = TimeAlloc(ID_visit=ID_visit,time_stay=time_stay,date_time=date_time)
    try:
        db.session.add_all([ta])
        db.session.commit()
        return (True,"new time allocation successfully")
    except:
        return (False,"new time allocation  failed")

def addTimeAlloc(ID_visit,time_add=300):
    if (TimeAlloc.query.filter_by(ID_visit=ID_visit).count()!=1):
        return (False,"no value")
    ta = TimeAlloc.query.filter_by(ID_visit=ID_visit).first()
    hours = int(time_add/100) + int(ta.time_stay/100)
    minutes = time_add%100 + ta.time_stay%100
    if(minutes>=60):
        hours=hours+1
        minutes=minutes-60
    ta.time_stay = hours*100+minutes
    tv = LocCurr.query.filter_by(ID_visit=ID_visit).first()
    tv.time_stay = ta.time_stay

    try:
        db.session.commit()
        return (True,"update successfully")
    except:
        return (False,"update time allocation failed")

def addTimeAllocByID(ID_person,time_add=300):
    idvisit=LocCurr.query.filter_by(ID_person=ID_person).first().ID_visit
    return (addTimeAlloc(idvisit,time_add))

def showVisitorNow():
    return LocCurr.query.all()

def showCountToday():
    sql = 'SELECT count(*) FROM managesystem.location_history where date_history='+getday_in_int()+' group by ID_visit'
    cursor = db.session.execute(sql)
    result = cursor.fetchall()
    return len(result)

def showCountOneDay(date=getday_in_int()):
    sql = 'SELECT count(*) FROM managesystem.location_history where date_history='+str(date)+' group by ID_visit'
    cursor = db.session.execute(sql)
    result = cursor.fetchall()
    return len(result)

def showCountAll(date=getday_in_int()):
    sql = 'SELECT count(*) FROM managesystem.location_history where date_history<='+str(date)+' group by ID_visit'
    cursor = db.session.execute(sql)
    result = cursor.fetchall()
    return len(result)


def showCountInOnePlaceNow(longitude_low,longitude_high,latitude_low,latitude_high):
    sql = 'SELECT * FROM managesystem.location_current where '\
          +' longitude_current between '+str(longitude_low)+' and '+str(longitude_high)+' and latitude_current between '\
          +str(latitude_low)+' and '+str(latitude_high)
    cursor = db.session.execute(sql)
    result = cursor.fetchall()
    return len(result)

def showCountInOnePlace(longitude_low,longitude_high,latitude_low,latitude_high,date=getday_in_int()):
    sql = 'SELECT count(*) FROM managesystem.location_history where date_history='+date\
          +' and longitude_history between '+str(longitude_low)+' and '+str(longitude_high)+' and latitude_history between '\
          +str(latitude_low)+' and '+str(latitude_high)+' group by ID_visit'
    cursor = db.session.execute(sql)
    result = cursor.fetchall()
    return len(result)

def showCountInSpecificPlace(place,date=getday_in_int()):
    if (place == '一餐'):
        return showCountInOnePlace(121.42617,121.427953,31.023737,31.024749,date)
    if (place == '二餐'):
        return showCountInOnePlace(121.431071,121.432171,31.024551,31.025282,date)
    if (place == '三餐'):
        return showCountInOnePlace(121.430149,121.430878,31.027515,31.028196,date)
    if (place == '四餐'):
        return showCountInOnePlace(121.42247,121.42306,31.026823,31.027555,date)
    if (place == '五餐'):
        return showCountInOnePlace(121.436153,121.437178,31.025269,31.025932,date)
    if (place == '六餐'):
        return showCountInOnePlace(121.439853,121.440223,31.031044,31.031394,date)
    if (place == '新图'):
        return showCountInOnePlace(121.431277,121.43368,31.027301,31.028828,date)
    if (place == '玉兰苑'):
        return showCountInOnePlace(121.426417,121.427028,31.025246,31.025687,date)
    if (place == '电院'):
        return showCountInOnePlace(121.435722,121.43859,31.025841,31.028192,date)

def showCountInSpecificPlaceNow(place):
    if (place == '一餐'):
        return showCountInOnePlaceNow(121.42617,121.427953,31.023737,31.024749)
    if (place == '二餐'):
        return showCountInOnePlaceNow(121.431071,121.432171,31.024551,31.025282)
    if (place == '三餐'):
        return showCountInOnePlaceNow(121.430149,121.430878,31.027515,31.028196)
    if (place == '四餐'):
        return showCountInOnePlaceNow(121.42247,121.42306,31.026823,31.027555)
    if (place == '五餐'):
        return showCountInOnePlaceNow(121.436153,121.437178,31.025269,31.025932)
    if (place == '六餐'):
        return showCountInOnePlaceNow(121.439853,121.440223,31.031044,31.031394)
    if (place == '新图'):
        return showCountInOnePlaceNow(121.431277,121.43368,31.027301,31.028828)
    if (place == '玉兰苑'):
        return showCountInOnePlaceNow(121.426417,121.427028,31.025246,31.025687)
    if (place == '电院'):
        return showCountInOnePlaceNow(121.435722,121.43859,31.025841,31.028192)

def showTimeStay(ID_visit,date=getday_in_int()):
    getins = LocHist.query.filter(and_(LocHist.date_history==date,LocHist.flag=='进入',LocHist.ID_visit==ID_visit)).all()
    getouts = LocHist.query.filter(and_(LocHist.date_history==date,LocHist.flag=='离开',LocHist.ID_visit==ID_visit)).all()
    ts=[]
    for i in range(len(getouts)):
        intime = str(getins[i].time_history)
        outtime = str(getouts[i].time_history)
        timestay = datetime.datetime.strptime(outtime,"%H%M")-datetime.datetime.strptime(intime,"%H%M")
        seconds=timestay.total_seconds()
        minutes = int(seconds/60)
        hours = int(minutes/60)
        mins = minutes%60
        ts.append(hours*100+mins)
    return(ts)

def showTimeAlloc(date=getday_in_int()):
    return TimeAlloc.query.filter(TimeAlloc.date_time==date).all()

if __name__ == '__main__':
    print(getday_in_int())
    print(gettime_in_int())
    #a='999 and 1=1'
    #print(RegInfo.query.filter_by(ID_person=a))
    print(register(name='哔了狗了',status='门卫',password='123456'))
    app.run()
