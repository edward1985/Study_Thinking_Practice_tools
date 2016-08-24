# -*- coding: utf-8 -*-
__author__ = 'ygm'
import csv,os
from zbclass_db import *

def mytest(str):
  f = open("debug.txt","a+");
  f.write(str+'\n');
  f.close();

def get_stat_str(all,num):
  if all == 0 and num>0:
    return str(num)+"/ NA"
  elif all==0 and num==0:
    return str(num)+"/ 0%";
  else:
    return str(num)+"/ "+str(int(100.0*num/all))+"%";

class zbclass (object):
  def __init__(self,dbname):
    self.codetype='gbk';

    need_read_csv=True;
    if os.path.isfile(dbname):
      need_read_csv = False;

    self.db = zbc_conn(dbname);

    self.records_exist = False;#didn't retrieve data

    # try:
    #   self.th_hook = hook_thread();
    # except:
    #   pass;

    try:
      if need_read_csv==True:
        self.read_semester_from_csv();
        self.read_groups_from_csv();
        self.read_student_from_csv();
        self.read_class_require_from_csv();
        self.read_url_from_csv();
    except:
      pass;

    try:
      #get current user who to fill the userlist.
      if False==self.get_current_user():
        self.read_student_from_csv(); #try to load from csv again.
        self.get_current_user();
      self.major=[];
      self.major_jiebie={}
      for m in self.db.get_major():
        if m[0] not in self.major:
          self.major.append(m[0]);
        if m[1] not in self.major_jiebie:
          self.major_jiebie[m[1]]=m[0];

      self.all_student = self.db.get_student();
      self.dict_all_student={};
      for row in self.all_student:
        if row[0] not in self.dict_all_student:
          self.dict_all_student[row[0]]=[];
        self.dict_all_student[row[0]].append(row);

    except:
      print "need insert users"

    self.stat_item_dic={
      "chuancheng":0,\
      "faben":0,\
      "gongxiu":0,\
      "xianzhi_chuancheng":0,\
      "xianzhi_faben":0,\
      "guanxiu_shuliang":0,\
      "guanxiu_shichang":0,\
      "ketou":0,\
      "nmamtf":u"随喜赞叹"
    }
    self.stat_item=[0 for k in self.stat_item_dic];
    pass;

  def is_val(self,iname,uname):
    if iname.decode(self.codetype).replace(u" ",u"") == uname:
      return True;
    else:
      return False;
  def get_string(self,iname):
    return iname.decode(self.codetype).replace(u" ",u"");

  def get_encode(self,iname):
    #iname.decode('gbk').replace(u" ",u"") == u"智悲双运";
    try:
      if iname.decode('gbk').replace(u" ",u"") == u"智悲":
        self.codetype='gbk';
      else: raise(NameError(""))
    except:
      try:
        if iname.decode('utf8').replace(u" ",u"") == u"智悲":
          self.codetype='utf8';
        else:
          raise(NameError(""));
      except:
        try:
          if iname.decode('gb2312').replace(u" ",u"") == u"智悲":
            self.codetype='gb2312';
          else: raise(NameError(""))
        except:
          try:
            if iname.decode('big5').replace(u" ",u"") == u"智悲":
              self.codetype='big5';#gbk
            else: raise(NameError(""))
          except:
            print "encode error";
            return False;
    return True;

  def is_table_empty(self,name):
    if name=='' or name==u"":
      return True;
    else:
      return False;


  #---Functions for get something from database
  def get_current_user(self):
    ctime=time.time();
    s = self.db.get_student(app_user=u"是");
    # print "----read csv takes",time.time()-ctime;ctime=time.time();
    if len(s)==0:
      return False;
    self.student_id=s[0][0]
    self.nick_name = s[0][1];
    self.jiebie = s[0][2];
    self.class_room= s[0][3];
    self.app_user = s[0][4];
    self.default_semester = s[0][5];
    self.status = s[0][6];
    self.remarks = s[0][7];
    self.remarks_student_id = s[0][8];
    self.insert_time = s[0][9];

    self.jiebie_semester = self.db.get_semester_list();

    self.get_time_by_semester();
    return True;

  def set_current_user(self,student_id=None):
    if student_id==None:
      return False;
    # s = self.db.get_student(app_user=u"是");
    # print "----read csv takes",time.time()-ctime;ctime=time.time();
    s=[];
    if student_id in self.dict_all_student:
      s = self.dict_all_student[student_id];
    if len(s)==0:
      return False;

    self.student_id=s[0][0]
    self.nick_name = s[0][1];
    self.jiebie = s[0][2];
    self.class_room= s[0][3];
    self.app_user = s[0][4];
    self.default_semester = s[0][5];
    self.status = s[0][6];
    self.remarks = s[0][7];
    self.remarks_student_id = s[0][8];
    self.insert_time = s[0][9];

    #jiebie don't need to be updated
    # self.jiebie_semester = self.db.get_semester_list();

    self.get_time_by_semester();

    #write default use into database
    self.db.set_default_user(self.student_id);

    return True;


  def get_time_by_semester(self):
    time_r = self.db.get_start_end_time_by_semester(jiebie=self.jiebie,semester=self.default_semester);
    if len(time_r)>0:
      self.stime = int(time_r[0][0]);
      self.etime = int(time_r[0][1]);
    else:
      self.stime = None;
      self.etime = None;
    return;

  #---Functions for Read CSV
  def change_coding_of_csv(self,fname,ecd="utf8"):
    f=open(fname,"rb");
    reader = csv.reader(f);
    frow = reader.next();#first row
    self.get_encode(frow[0]);
    if ecd not in ['utf8','gbk','gb2312','big5'] or self.codetype==ecd:
      f.close();
      return;

    rows=[[self.get_string(r) for r in row] for row in reader]
    rows.insert(0,[self.get_string(r) for r in frow]);
    f.close();

    f = open(fname,"wb");
    w=csv.writer(f,lineterminator='\n');
    for r in rows:
      w.writerow([get_val_unicode(t,ecd) for t in r ]);
    f.close();

  def read_student_from_csv(self,fname="data/student_info.csv"):
    f=open(fname,"rb");
    reader = csv.reader(f);
    row = reader.next();
    self.get_encode(row[0]);
    row = reader.next(); #escape the headerline
    s=[]
    s = [[self.get_string(r) for r in row] for row in reader];
    f.close();

    if len(s) == 0:
      return None;

    for i in range(len(s)):
      # add rolltime,status,remarks,remarks'student_id,insert_time
      s[i].extend([None,None,None,int(time.time()),]);
    self.db.replace_into_many(u"student",s);

  def read_class_require_from_csv(self,fname="data/class_info.csv"):
    f=open(fname,"rb");
    # reader = csv.DictReader(f);
    reader = csv.reader(f);
    row = reader.next();
    self.get_encode(row[0]);
    row = reader.next();
    s=[]
    ctime = time.time();
    # for row in reader:
    #   t.append(row);
    s = [[self.get_string(row[0]),self.get_string(row[1]),self.get_string(row[2]),self.get_string(row[3]),int(row[4]),
          int(row[5]),int(row[6]),int(row[7]),int(row[8]),int(row[9]),time_str_int(row[10])] for row in reader];
    f.close();
    if s==None:
      return None;
    self.db.replace_into_many(u"class_require",s);

  def read_url_from_csv(self,fname="data/url_info.csv"):
    f=open(fname,"rb");
    # reader = csv.DictReader(f);
    reader = csv.reader(f);
    row = reader.next();
    self.get_encode(row[0]);
    row = reader.next();
    s=[]
    ctime = time.time();
    # for row in reader:
    #   t.append(row);
    s = [[self.get_string(row[0]),self.get_string(row[1]),self.get_string(row[1])] for row in reader];
    f.close();
    if s==None:
      return None;
    self.db.replace_into_many(u"u_url",s);

  def read_semester_from_csv(self,fname="data/semester_info.csv"):
    f=open(fname,"rb");
    # reader = csv.DictReader(f);
    reader = csv.reader(f);
    row = reader.next();
    self.get_encode(row[0]);
    row = reader.next();
    s = [[self.get_string(row[0]),self.get_string(row[1]),time_str_int(row[2]),time_str_int(row[3])] for row in reader];
    f.close();
    if len(s)==0:
      return None;
    self.db.replace_into_many(u"semester",s);

  def read_groups_from_csv(self,fname="data/groups_info.csv"):
    f=open(fname,"rb");
    # reader = csv.DictReader(f);
    reader = csv.reader(f);
    row = reader.next();
    self.get_encode(row[0]);
    row = reader.next();
    s = [[self.get_string(row[0]),self.get_string(row[1]),self.get_string(row[2]),self.get_string(row[3]),self.get_string(row[4]),] for row in reader];
    f.close();
    if s==None:
      return None;
    self.db.replace_into_many(u"groups",s);

  #001 get user information.
  def get_current_records(self,jiebie=None,stime=None,etime=None,type=None,stat_type=None,student_id=None):
    # if self.records_exist==False:
    self.records = self.db.get_records(jiebie=jiebie,stime=stime,etime=etime,type=type,stat_type=stat_type,student_id=student_id);
    return self.records;
    # self.records_exist = True;

  def store_into_csv(self,all_course,display_class,rr_jiebie,r_jiebie,\
         r_semester,fname="statistic.csv",stat_only=False):
    st_summary = ([
                           u'个人实际共修出勤累计总次数',
                           u'主修缺听传承课数',
                           u'主修缺看法本课数',
                           u'限制性课程缺听光碟数',
                           u'限制性课程缺看法本数',
                           u'累计观修座次',
                           u'累计观修时间(分钟)',
                           u'加行磕头数',
                           ]);
    st_course = ([
                           u'听传承',
                           u'看法本',
                           u'参加共修',
                           ]);
    st_xianzhi_course = ([
                           u'听传承',
                           u'看法本',
                           ]);
    st_guanxiu = ([
                           u'观修座次',
                           u'观修时间',
                           ]);
    st_dingli = ([
                           u'加行磕头数',
                           ]);
    st_semester = ([
                           u'本学期主修听传承数',
                           u'本学期主修看法本数',
                           u'本学期个人实际共修出勤累计总次数',
                           u'本学期限制性课程听传承数',
                           u'本学期限制性课程看法本数',
                           u'本学期观修总圆满座次',
                           u'本学期观修总时间(分钟)',
                           u'本学期加行磕头数',
                           ]);

    f = open(fname,"wb");
    w=csv.writer(f,lineterminator='\n');

    # mytest("start----")

    # data=[u'' for i in range(4)]
    # 班级, 学员姓名,学期, [闻思课程]，[共修情况],[实修],[累计汇总]
    # 累计汇总:
    for jiebie in r_semester:
      a_row = {};
      for name in rr_jiebie[jiebie]:
        if name!='all':
          a_row[name]=[name,jiebie];
      title = [u'学员届别','']
      subtitle0 = ['','']
      subtitle1 = [u"学员姓名",u'班级']
      #semester extend;
      for semester in r_semester[jiebie]:
        title.extend([semester,'','','','','','','']);
        subtitle0.extend([unicode(semester+u'学期汇总'),'','','','','','','']);
        subtitle1.extend(st_semester);
        for name in r_semester[jiebie][semester]:
          #attach summary of this semester:
          if name == 'all':
            continue;
          a_row[name].extend(
            [
              r_semester[jiebie][semester][name][0],
              r_semester[jiebie][semester][name][1],
              r_semester[jiebie][semester][name][2],
              r_semester[jiebie][semester][name][3],
              r_semester[jiebie][semester][name][4],
              r_semester[jiebie][semester][name][5],
              r_semester[jiebie][semester][name][6],
              r_semester[jiebie][semester][name][7],
            ])

      #jiebie report
      title.extend([jiebie,'','','','','','','']);
      subtitle0.extend([u'届别总汇总','','','','','','','']);
      subtitle1.extend(st_summary);
      for name in rr_jiebie[jiebie]:
        if name=='all':
          continue;
        a_row[name].extend([
          r_jiebie[jiebie][name][2],
          r_jiebie[jiebie]['all'][0] - r_jiebie[jiebie][name][0],
          r_jiebie[jiebie]['all'][1] - r_jiebie[jiebie][name][1],
          r_jiebie[jiebie]['all'][3] - r_jiebie[jiebie][name][3],
          r_jiebie[jiebie]['all'][4] - r_jiebie[jiebie][name][4],
          r_jiebie[jiebie][name][5],
          r_jiebie[jiebie][name][6],
          r_jiebie[jiebie][name][7],
        ]);

      #write into files:
      #write header
      w.writerow([get_val_unicode(t,self.codetype) for t in title]);
      w.writerow([get_val_unicode(t,self.codetype) for t in subtitle0]);
      w.writerow([get_val_unicode(t,self.codetype) for t in subtitle1]);
      # mytest("mid----")

      for name in a_row:
        w.writerow([get_val_unicode(t,self.codetype) for t in a_row[name] ]);
        # mytest("mid----")
    f.close();
    print u"南无阿弥陀佛";
    # mytest("finish")

# t=zbclass("class.db");
# t.read_class('class.csv');