# -*- coding: utf-8 -*-
import time;
import wx

from wx.lib.agw import ultimatelistctrl as ULC
from zbclass import *
from functools import partial
from copy import deepcopy;
import os
import Queue;
import wx.lib.agw.hyperlink as hl
#create a text
def pkc_create_text(parent,pos,value='N/A',size=(170,-1),style=wx.TE_READONLY|wx.NO_BORDER,nrow=0):
  #wx.TE_RICH will use wx.richtext.RichTextCtrl without vertical scrollbar
  text = wx.TextCtrl(parent,value=value,pos=pos,size=size,style=style|wx.TE_RICH);
  text.SetBackgroundColour(parent.GetBackgroundColour());
  pos[0] += size[0];
  pos[1] += nrow;
  return text;
#create imput static text.
def pkc_create_static_text(parent,pos,value='',size=(107,-1),style=wx.TE_READONLY|wx.NO_BORDER,nrow=0):
  text = wx.TextCtrl(parent,value=value,pos=pos,size=size,style=style|wx.TE_RICH);
  text.SetBackgroundColour(parent.GetBackgroundColour());
  pos[0] += size[0];
  pos[1] += nrow;
  return text;

class zbc_summary(wx.Panel):
  def __init__(self, parent , mframe):
    self.mframe = mframe;
    wx.Panel.__init__(self, parent,size=(3000,3000))
    self.SetBackgroundColour((255,255,255));

    self.urlultimatelist = ULC.UltimateListCtrl(self,size=(530,-1), agwStyle = wx.LC_REPORT
                                     | wx.LC_VRULES
                                     | wx.LC_HRULES
                                     |ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
                                     |ULC.ULC_NO_HIGHLIGHT)
    thelist=[u"",u"常用链接描述",u"网址",u"操作"]
    idx = 0;
    for n in thelist:
      info = ULC.UltimateListItem()
      info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
      info._image = []
      info._format = wx.LIST_FORMAT_LEFT
      info._kind = 1
      info._text = n;
      self.urlultimatelist.InsertColumnInfo(idx, info)
      idx += 1;
    self.urlultimatelist.SetColumnWidth(0, 0)
    self.urlultimatelist.SetColumnWidth(1, 87)
    self.urlultimatelist.SetColumnWidth(2, 300)
    self.urlultimatelist.SetColumnWidth(3, 137)
    #法名，界别，真名，共修小组
    #统计信息：圆满课程数；第几学期；
    si={}
    si_list=[]
    for x in self.mframe.zbc.all_student:
      if x[1] not in si:
        si[x[1]]=x;
        si_list.append(x[1]);
    si_list.sort();
    # si_list = [x[0] for x in self.mframe.zbc.all_student];
    if self.mframe.type=="personal":
      si_list = [self.mframe.zbc.nick_name];

    xpos=[0,3];nick_name = pkc_create_static_text(self,xpos,size=(87,-1), value=u"规范昵称");
    self.si_choice = wx.Choice(self,wx.ID_ANY,choices=si_list,size=(167,-1),)
    self.si_choice.SetStringSelection(self.mframe.zbc.nick_name)
    self.si_choice.Bind(wx.EVT_CHOICE, self.si_change)

    box0 = wx.BoxSizer(wx.HORIZONTAL);
    box0.Add(nick_name, 0, wx.ALL|wx.RIGHT|wx.TOP, 0)
    box0.Add(self.si_choice, 0, wx.ALL|wx.RIGHT|wx.TOP, 0)

    xpos=[0,3];buddha_name_s = pkc_create_static_text(self,xpos,size=(87,-1), value=u"学员编号");
    self.si_text = pkc_create_static_text(self,xpos,value=mframe.zbc.student_id,size=(167,-1));
    box1 = wx.BoxSizer(wx.HORIZONTAL);
    box1.Add(buddha_name_s, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
    box1.Add(self.si_text, 0, wx.ALL|wx.LEFT|wx.TOP, 0)

    #jiebie and semester can be selectable
    jiebie_list=[]
    for row in self.mframe.zbc.db.get_student_jiebie(self.mframe.zbc.student_id):
      jiebie_list.append(row[0]);
    jiebie_list.sort();
    # wx.Choice(panel, -1, (85, 18), choices=sampleList)
    xpos=[0,3];buddha_name_s = pkc_create_static_text(self,xpos,size=(87,-1), value=u"届别及专业");
    self.jiebie_choice = wx.Choice(self,wx.ID_ANY,choices=jiebie_list,size=(167,-1),)
    self.jiebie_choice.SetStringSelection(self.mframe.zbc.jiebie);
    self.jiebie_choice.Bind(wx.EVT_CHOICE, self.jiebie_change)
    # self.jiebie_text = pkc_create_text(self,xpos,value=self.mframe.zbc.jiebie,style=wx.BORDER);

    box2 = wx.BoxSizer(wx.HORIZONTAL);
    box2.Add(buddha_name_s, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
    box2.Add(self.jiebie_choice, 0, wx.ALL|wx.LEFT|wx.TOP, 0)

    g_list =[];
    for cr in self.mframe.zbc.db.get_class_room(self.mframe.zbc.jiebie):
      g_list.append(cr[0]);
    g_list.sort()

    buddha_name_s = pkc_create_static_text(self,xpos,size=(87,-1), value=u"组      别");
    # self.g_name = pkc_create_text(self,xpos,value=mframe.zbc.class_room,style=wx.BORDER);
    self.g_choice = wx.Choice(self,wx.ID_ANY,choices=g_list,size=(167,-1),)
    self.g_choice.SetStringSelection(self.mframe.zbc.class_room);
    self.g_choice.Bind(wx.EVT_CHOICE, self.group_change)
    box3 = wx.BoxSizer(wx.HORIZONTAL);
    box3.Add(buddha_name_s, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
    box3.Add(self.g_choice, 0, wx.ALL|wx.LEFT|wx.TOP, 0)

    #semesters
    cjiebie = self.mframe.zbc.jiebie;
    seme_list = [];
    if cjiebie in self.mframe.zbc.jiebie_semester:
      for seme in self.mframe.zbc.jiebie_semester[cjiebie]:
        seme_list.append(seme[0]);
    seme_list.sort();

    buddha_name_s = pkc_create_static_text(self,xpos,size=(87,-1), value=u"当前学期");
    self.seme_choice = wx.Choice(self,wx.ID_ANY,choices=seme_list,size=(167,-1))
    self.seme_choice.SetStringSelection(self.mframe.zbc.default_semester);
    self.seme_choice.Bind(wx.EVT_CHOICE, self.semester_change)
    box4 = wx.BoxSizer(wx.HORIZONTAL);
    box4.Add(buddha_name_s, 0, wx.ALL|wx.RIGHT|wx.TOP, 0)
    box4.Add(self.seme_choice, 0, wx.ALL|wx.LEFT|wx.TOP, 0)

    self.info_val = unicode(u"""使用说明：重新读取课表信息按钮，将导入在data目录下的所有学生信息，课表信息，分组信息，学期信息。
学员编号是唯一标识，在没有分配学员编号之前，可先由小组长选择一个学号，保证在小组或中组内唯一即可。
等学员编号下发后，小组长可以将数据库内学员编号修改为标准学员编号。
    """)
    help_info = pkc_create_static_text(self,[3,0],size=(837,101), value=self.info_val,style=wx.TE_MULTILINE|wx.TE_READONLY|wx.SIMPLE_BORDER);

    #==============================================================================
    box_li = wx.BoxSizer(wx.HORIZONTAL);
    load_info = wx.Button(self, wx.ID_ANY, u"重新读取课表信息", pos=(30, 0),size=(137,59));
    self.Bind(wx.EVT_BUTTON, self.load_info, load_info);
    li_info = pkc_create_static_text(self,[0,3],size=(700,59), value="",style=wx.TE_MULTILINE|wx.TE_READONLY|wx.SIMPLE_BORDER);
    li_info.SetValue(u"加载data目录下的指定的studeng.csv,groups.csv,semester.csv,class_require.csv文件");
    box_li.Add(load_info, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
    box_li.Add(li_info, 0, wx.ALL|wx.LEFT|wx.TOP, 0)

    self.op_status = pkc_create_static_text(self,[30,150],size=(300,87), value=u"南无阿弥陀佛",style=wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER);

    box5 = wx.BoxSizer(wx.HORIZONTAL);
    box5.Add(self.op_status,0, wx.ALL|wx.LEFT|wx.CENTER, 5)

    # self.cbs = wx.RadioBox(self,-1,choices=[u'都显示',u'只显示本学期'])
    # self.cbs.SetSelection(1);
    # self.Bind(wx.EVT_RADIOBOX, self.checkbox_display)
    # box6 = wx.BoxSizer(wx.HORIZONTAL);
    # box6.Add(self.cbs,0, wx.ALL|wx.LEFT|wx.CENTER, 5)

    # add 常用网站
    #Usage: like mySizer.Add(window, proportion, flag(s), border, userData)

    box = wx.BoxSizer(wx.VERTICAL)

    box_f = wx.BoxSizer(wx.HORIZONTAL)
    box_l = wx.BoxSizer(wx.VERTICAL)
    box_l.Add(box0, flag= wx.LEFT|wx.TOP, border=2)
    box_l.Add(box1, flag= wx.LEFT|wx.TOP, border=2)
    box_l.Add(box2, flag= wx.LEFT|wx.TOP, border=2)
    box_l.Add(box3, flag= wx.LEFT|wx.TOP, border=2)
    box_l.Add(box4, flag= wx.LEFT|wx.TOP, border=2)
    box_l.Add(box5, flag= wx.LEFT|wx.TOP, border=2)
    # box_l.Add(box6, flag= wx.LEFT|wx.TOP, border=2)

    box_f.Add(box_l, flag= wx.LEFT|wx.TOP, border=1)
    box_f.Add(self.urlultimatelist,flag = wx.EXPAND)

    box.Add(box_f, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=2)

    box.Add(help_info, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=2)
    #
    box.Add(box_li, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=1)


    #add command to change csv to setted coding type
    code_type = wx.Button(self, wx.ID_ANY, u"修改编码", pos=(30, 0),size=(97,78));
    self.Bind(wx.EVT_BUTTON, self.change_ct, code_type);
    ct_info = pkc_create_static_text(self,[0,0],size=(657,78), value="",style=wx.TE_MULTILINE|wx.TE_READONLY|wx.SIMPLE_BORDER);
    ct_info.SetValue(u"如果您的csv文件打开后是乱码，请先关闭所有csv文件，尝试不同的编码（所有data目录下的csv文件都会更改）。英文系统选utf8,简体选gb2312,或都试一遍");

    self.ct_choice = wx.Choice(self,wx.ID_ANY,choices=['utf8','gb2312'],size=(83,78))
    self.ct_choice.SetStringSelection('utf8');
    box11 = wx.BoxSizer(wx.HORIZONTAL);
    box11.Add(code_type, 0, wx.ALL|wx.RIGHT|wx.TOP, 0)
    box11.Add(self.ct_choice, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
    box11.Add(ct_info, 0, wx.ALL|wx.RIGHT|wx.TOP, 0)
    box.Add(box11, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=1)

    #add command line to change 学号
    merge_id = wx.Button(self, wx.ID_ANY, u"修改学号-记得重启工具", pos=(30, 0),size=(200,30));
    self.Bind(wx.EVT_BUTTON, self.change_id, merge_id);

    xpos=[0,3];old_id_tx = pkc_create_static_text(self,xpos,size=(87,-1), value=u"旧学号");
    self.old_id = pkc_create_static_text(self,xpos,value=mframe.zbc.student_id,size=(167,-1),style=wx.BORDER);

    new_id_tx = pkc_create_static_text(self,xpos,size=(87,-1), value=u"新学号");
    self.new_id = pkc_create_static_text(self,xpos,value=mframe.zbc.student_id,size=(167,-1),style=wx.BORDER);


    clear_class_student = wx.Button(self, wx.ID_ANY, u"清空旧课表和学员信息", pos=(30, 0),size=(163,30));
    self.Bind(wx.EVT_BUTTON, self.clear_class_student, clear_class_student);

    box13 = wx.BoxSizer(wx.HORIZONTAL);
    box13.Add(clear_class_student, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
    box12 = wx.BoxSizer(wx.HORIZONTAL);
    box12.Add(merge_id, 0, wx.ALL|wx.RIGHT|wx.TOP, 0)
    box12.Add(old_id_tx, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
    box12.Add(self.old_id, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
    box12.Add(new_id_tx, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
    box12.Add(self.new_id, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
    box.Add(box13, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=1)
    box.Add(box12, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=1)



    if self.mframe.type=="group":
      box_tools = wx.BoxSizer(wx.HORIZONTAL);
      box_ir = wx.BoxSizer(wx.HORIZONTAL);

      import_records = wx.Button(self, wx.ID_ANY, u"加载学员修行记录", pos=(30, 0),size=(137,37));
      self.Bind(wx.EVT_BUTTON, self.import_records, import_records);
      # ir_info = pkc_create_static_text(self,[0,0],size=(687,37), value="",style=wx.TE_MULTILINE|wx.TE_READONLY|wx.SIMPLE_BORDER);
      # ir_info.SetValue(u"统计使用：加载*.db数据库内包含的学员信息，学员出勤信息，学员修行的统计: （为了减少数据库大小，这里不包括每次操作的历史记录）");
      box_tools.Add(import_records, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
      # box_ir.Add(ir_info, 0, wx.ALL|wx.LEFT|wx.TOP, 0)

      box_is = wx.BoxSizer(wx.HORIZONTAL);
      import_student = wx.Button(self, wx.ID_ANY, u"加载学员信息", pos=(30, 0),size=(137,37));
      self.Bind(wx.EVT_BUTTON, self.import_student, import_student);
      # is_info = pkc_create_static_text(self,[0,0],size=(687,37), value="",style=wx.TE_MULTILINE|wx.TE_READONLY|wx.SIMPLE_BORDER);
      # is_info.SetValue(u"统计使用：加载student_info.csv信息，各大/中/小组拥有自己的student信息。学员的学号必须是规定好的，唯一的号，届别也必须是统一安排的名称，不允许学员随意改动");
      box_tools.Add(import_student, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
      # box_is.Add(is_info, 0, wx.ALL|wx.LEFT|wx.TOP, 0)

      box_ic = wx.BoxSizer(wx.HORIZONTAL);
      import_class_require = wx.Button(self, wx.ID_ANY, u"加载课表信息", pos=(30, 0),size=(137,37));
      self.Bind(wx.EVT_BUTTON, self.import_class_require, import_class_require);
      # ic_info = pkc_create_static_text(self,[0,0],size=(687,37), value="",style=wx.TE_MULTILINE|wx.TE_READONLY|wx.SIMPLE_BORDER);
      # ic_info.SetValue(u"统计使用：加载class_info.csv信息，各届别拥有不同的课表，每个学员只需要加载属于自己的课表。各组统计时，需要加载所有课表。为了避免出错，数据库加载时不加载该表");
      box_tools.Add(import_class_require, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
      # box_ic.Add(ic_info, 0, wx.ALL|wx.LEFT|wx.TOP, 0)

      box_ig = wx.BoxSizer(wx.HORIZONTAL);
      import_groups = wx.Button(self, wx.ID_ANY, u"加载组信息", pos=(30, 0),size=(137,37));
      self.Bind(wx.EVT_BUTTON, self.import_groups, import_groups);
      # ig_info = pkc_create_static_text(self,[0,0],size=(687,37), value="",style=wx.TE_MULTILINE|wx.TE_READONLY|wx.SIMPLE_BORDER);
      # ig_info.SetValue(u"统计使用：加载group_info.csv信息，比如加行有多少届别，大组有哪些中组，中组有哪些小组。统计时使用");
      box_tools.Add(import_groups, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
      # box_ig.Add(ig_info, 0, wx.ALL|wx.LEFT|wx.TOP, 0)

      box_iseme = wx.BoxSizer(wx.HORIZONTAL);
      import_semester = wx.Button(self, wx.ID_ANY, u"加载学期信息", pos=(30, 0),size=(137,37));
      self.Bind(wx.EVT_BUTTON, self.import_semester, import_semester);
      # s_info = pkc_create_static_text(self,[0,0],size=(687,37), value="",style=wx.TE_MULTILINE|wx.TE_READONLY|wx.SIMPLE_BORDER);
      # s_info.SetValue(u"统计使用：加载semester.csv信息，每个届别有多少个学期，每个学期开学和放学时间。个人只需要有自己的届别的学期信息");
      box_tools.Add(import_semester, 0, wx.ALL|wx.LEFT|wx.TOP, 0)
      # box_iseme.Add(s_info, 0, wx.ALL|wx.LEFT|wx.TOP, 0)

      box.Add(box_tools, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=1)
      # box.Add(box_ir, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=1)
      # box.Add(box_is, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=1)
      # box.Add(box_ic, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=1)
      # box.Add(box_ig, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=1)
      # box.Add(box_iseme, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=1)

    self.SetSizer(box);
    box.Fit(self)
    self.update_ulti()
  def group_change(self,event=None):
    pass;

  def change_id(self,event=None):
    newid=self.new_id.GetValue();
    oldid=self.old_id.GetValue();
    #change old id into new id;
    if newid!=oldid:
      self.mframe.zbc.db.change_oldid_to_newid(oldid,newid);
      self.op_status.SetValue(u"请您重新启动小工具")
      self.mframe.refresh_tables();

  def change_ct(self,event=None):
    ct=self.ct_choice.GetStringSelection();
    fpath = "data"
    for f in os.listdir(fpath):
      t=f.strip().split(".");
      if t[-1].upper()=="CSV" and os.path.isfile(fpath+"/"+f):
        self.mframe.zbc.change_coding_of_csv(fpath+"/"+f,ct);
    pass

  def update_ulti(self):
    self.urlultimatelist.DeleteAllItems();
    records=self.mframe.zbc.db.get_useful_url();
    idx = 0;
    for row in records:
      self.urlultimatelist.InsertStringItem(idx,'')

      ha = hl.HyperLinkCtrl(self.urlultimatelist, -1, row[0], pos=(0, 0),URL=row[1])
      self.urlultimatelist.SetItemWindow(idx, col=1, wnd=ha, expand=True);

      dval = row[1];
      #wx.TE_PROCESS_ENTER is required for evt_text_enter
      uurl = wx.TextCtrl(self.urlultimatelist,value=unicode(dval),pos=(0,0),size=(300,25),style=wx.TE_RICH|wx.TE_PROCESS_ENTER);
      self.urlultimatelist.SetItemWindow(idx, col=2, wnd=uurl, expand=True);
      uurl.Bind(wx.EVT_TEXT_ENTER, partial(self.mod_url,param=[row[0],uurl]))

      button=wx.Button(self.urlultimatelist, wx.ID_ANY, u"删除", pos=(0, 0),size=(137,30));
      self.urlultimatelist.SetItemWindow(idx, col=3, wnd=button, expand=True);
      button.Bind(wx.EVT_BUTTON, partial(self.delete_url,param=[row[0]]));
      idx += 1;

    x  = self.urlultimatelist.InsertStringItem(idx, '')
    url_name = wx.TextCtrl(self.urlultimatelist,value='',pos=(0,0),size=(87,-1),style=wx.TE_RICH);
    self.urlultimatelist.SetItemWindow(idx, col=1, wnd=url_name, expand=True);
    uurl = wx.TextCtrl(self.urlultimatelist,value='',pos=(0,0),size=(300,-1),style=wx.TE_RICH);
    self.urlultimatelist.SetItemWindow(idx, col=2, wnd=uurl, expand=True);

    button=wx.Button(self.urlultimatelist, wx.ID_ANY, u"增加", pos=(0, 0),size=(137,30));
    self.urlultimatelist.SetItemWindow(idx, col=3, wnd=button, expand=True);
    button.Bind(wx.EVT_BUTTON, partial(self.add_url,param=[url_name,uurl,]))
    pass;
  def delete_url(self,event=None,param=None):
    self.mframe.zbc.db.delete_url(param[0]);
    self.update_ulti();
    pass
  def add_url(self,event=None,param=None):
    t = param[1].GetValue();
    name = param[0].GetValue();
    self.mframe.zbc.db.add_url(name,t)
    self.update_ulti()
    pass
  def mod_url(self,event=None,param=None):
    t = param[1].GetValue();
    name = param[0];
    self.mframe.zbc.db.update_url(name,t)
    self.update_ulti()
    pass
  def si_change(self,event):
    nick_name = self.si_choice.GetString(self.si_choice.GetCurrentSelection());
    student_id = self.mframe.zbc.student_id;
    for row in self.mframe.zbc.all_student:
      if row[1]==nick_name:
        student_id=row[0];
        break;
    self.mframe.zbc.set_current_user(student_id);

    self.jiebie_choice.Clear();
    for row in self.mframe.zbc.db.get_student_jiebie(self.mframe.zbc.student_id):
      self.jiebie_choice.Append(row[0]);
    self.jiebie_choice.SetSelection(0);
    self.jiebie_change();

    self.refresh_student_info();
    self.mframe.refresh_tables();
    print "student info changed"

  def jiebie_change(self,event=None):
    #when jiebie is changed, semester should change too
    cjiebie = self.jiebie_choice.GetString(self.jiebie_choice.GetCurrentSelection());
    seme_list = [];
    if cjiebie in self.mframe.zbc.jiebie_semester:
      for seme in self.mframe.zbc.jiebie_semester[cjiebie]:
        seme_list.append(seme[0]);
    seme_list.sort();

    self.seme_choice.Clear() # Clear the current user list
    self.seme_choice.AppendItems(seme_list) # Repopulate the list
    self.seme_choice.SetSelection(0)

    g_list =[];
    for cr in self.mframe.zbc.db.get_class_room(cjiebie):
      g_list.append(cr[0]);
    g_list.sort()
    self.g_choice.Clear() # Clear the current user list
    self.g_choice.AppendItems(g_list) # Repopulate the list
    self.g_choice.SetSelection(0)

    self.semester_change(event);
    pass;

  def refresh_student_info(self):
    self.si_text.SetValue(self.mframe.zbc.student_id);
    self.jiebie_choice.SetStringSelection(self.mframe.zbc.jiebie)
    self.jiebie_change();

    #update choices
    # cjiebie = self.mframe.zbc.jiebie;
    # seme_list = [];
    # t = {};
    # if cjiebie in self.mframe.zbc.jiebie_semester:
    #   for seme in self.mframe.zbc.jiebie_semester[cjiebie]:
    #     if seme[0] not in t:
    #       seme_list.append(seme[0]);
    #       t[seme[0]]=1
    # seme_list.sort();
    #
    # self.seme_choice.Clear();
    # self.seme_choice.AppendItems(seme_list);
    # if self.mframe.zbc.default_semester!=None:
    #   self.seme_choice.SetStringSelection(self.mframe.zbc.default_semester);
    # else:
    #   self.seme_choice.SetSelection(0);
    #
    # # self.location.SetValue(self.mframe.zbc.department);
    # self.g_choice.SetValue(self.mframe.zbc.class_room);

  def semester_change(self,event):

    jiebie = self.jiebie_choice.GetString(self.jiebie_choice.GetCurrentSelection());#.GetString(self.jiebie_choice.GetCurrentSelection());
    semester = self.seme_choice.GetString(self.seme_choice.GetCurrentSelection());
    uname = self.si_choice.GetString(self.si_choice.GetCurrentSelection());

    if self.mframe.zbc.jiebie==jiebie and \
      self.mframe.zbc.nick_name==uname and \
      self.mframe.zbc.default_semester==semester:
      #nothing changed so do nothing
      return;

    # self.mframe.zbc.jiebie=jiebie;
    # self.mframe.zbc.student_id=uname;
    self.mframe.zbc.default_semester=semester;
    self.mframe.zbc.get_time_by_semester();

    #Store the default_semester into the student_list.
    if jiebie in self.mframe.zbc.all_student:
      self.mframe.zbc.all_student[jiebie][uname][8] = semester;
    self.mframe.zbc.db.set_default_user(student_id=uname,default_semester=semester);

    self.mframe.refresh_tables();
    self.op_status.SetValue(u"南无阿弥陀佛，学期设置成功！")
    pass;

  def checkbox_display(self,event):
    # self.mframe.page_wens
    cb = event.GetEventObject()
    x = cb.GetSelection()

    # jiebie=self.mframe.zbc.jiebie;
    # uname=self.mframe.zbc.student_id;
    # semester=self.mframe.zbc.semester;
    if x==0: #get all information
       self.mframe.zbc.etime=self.mframe.zbc.stime=None;

    self.mframe.refresh_tables();

    self.op_status.SetValue(u"南无阿弥陀佛，相应数据已修改！")
    print x;
    pass;

  def select_path(self,message=u"南无阿弥陀佛,请选择文件夹",defaultPath="student_info.csv"):
    of  = wx.DirDialog(None,style=wx.DD_DEFAULT_STYLE,defaultPath=defaultPath,message=message);
    if of.ShowModal() == wx.ID_CANCEL:
      print "cancel"
      # of.Destroy();
      return None;
    # of.Destroy();
    return of.GetPath();

  def select_file(self,title=u"csv file",file_type="*.csv",default_name="student_info.csv"):
    of  = wx.FileDialog(None,title,u"南无阿弥陀佛",default_name,file_type,wx.FD_OPEN | wx.FD_FILE_MUST_EXIST);
    if of.ShowModal() == wx.ID_CANCEL:
      print "cancel"
      # of.Destroy();
      return None;
    # of.Destroy();
    return of.GetPath();

  def save_file(self,title=u"csv file",file_type="*.csv",default_name="student_info.csv"):
    of  = wx.FileDialog(None,title,u"南无阿弥陀佛",default_name,file_type,wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT);
    if of.ShowModal() == wx.ID_CANCEL:
      print "cancel"
      # of.Destroy();
      return None;
    # of.Destroy();
    return of.GetPath();

  #---checking ...

  def load_info(self,event=None,para=None):
    # cb = event.GetEventObject()
    self.mframe.zbc.read_semester_from_csv();
    self.mframe.zbc.read_groups_from_csv();
    self.mframe.zbc.read_student_from_csv();
    self.mframe.zbc.read_class_require_from_csv();
    self.mframe.zbc.read_url_from_csv();

    #get current user who to fill the userlist.
    try:
      if False==self.mframe.zbc.get_current_user():
        self.mframe.zbc.read_student_from_csv(); #try to load from csv again.
        self.mframe.zbc.get_current_user();
      self.mframe.zbc.major=[];
      self.mframe.zbc.major_jiebie={}
      for m in self.mframe.zbc.db.get_major():
        if m[0] not in self.mframe.zbc.major:
          self.mframe.zbc.major.append(m[0]);
        if m[1] not in self.mframe.zbc.major_jiebie:
          self.mframe.zbc.major_jiebie[m[1]]=m[0];

      self.mframe.zbc.all_student = self.mframe.zbc.db.get_student();
      self.mframe.zbc.dict_all_student={};
      for row in self.mframe.zbc.all_student:
        if row[0] not in self.mframe.zbc.dict_all_student:
          self.mframe.zbc.dict_all_student[row[0]]=[];
        self.mframe.zbc.dict_all_student[row[0]].append(row);

    except:
      print "need insert users"

    self.mframe.refresh_tables()

    self.op_status.SetValue(u"南无阿弥陀佛，已经从class_info.csv,student_info.csv获取课表等信息！请您重启小工具")
    # self.op_status.Set

    # fname = self.select_file(u"南无阿弥陀佛，请您选择学员列表文件: student_info.csv","*.csv",default_name=os.getcwd()+"/data/student_info.csv");
    # self.mframe.zbc.read_all_user(fname);
    # print para;

  def import_records(self,event):
    fname = self.select_file(u"南无阿弥陀佛，请您选择学员的数据库文件: yuanfa.db","*.db",default_name=unicode(os.getcwd()+"/data/wensixiu.db"));
    self.mframe.zbc.db.import_records(fname,tablename="student");
    self.mframe.zbc.db.import_records(fname,tablename="attendance");
    self.mframe.zbc.db.import_records(fname,tablename="records");
    # cb = event.GetEventObject()

  def clear_class_student(self,event=None):
    self.mframe.zbc.db.clear_db_class_student();

  def import_student(self,event=None):
    try:
      fpath = self.select_path(message=u"请您选择包含了学员信息的文件夹");
      num = 0;
      for f in os.listdir(fpath):
        t = f.strip().split(".");
        if t[-1].upper()=="CSV" and os.path.isfile(fpath+"/"+f):
          self.mframe.zbc.read_student_from_csv(fpath+"/"+f);
          num += 1;
      self.op_status.SetValue(u"南无阿弥陀佛，已经获取"+unicode(num)+u"张学员信息文件！")
    except:
      self.op_status.SetValue(u"南无阿弥陀佛，没有找到正确的 学员 信息文件！")
      print " there are no correct student info"

  def import_class_require(self,event=None):
    try:
      fpath = self.select_path(message=u"请您选择包含了 课表 信息的文件夹");
      num = 0;
      for f in os.listdir(fpath):
        t = f.strip().split(".");
        if t[-1].upper()=="CSV" and os.path.isfile(fpath+"/"+f):
          self.mframe.zbc.read_class_require_from_csv(fpath+"/"+f);
          num += 1;
      self.op_status.SetValue(u"南无阿弥陀佛，已经获取"+unicode(num)+u"张 课表 信息文件！")
    except:
      self.op_status.SetValue(u"南无阿弥陀佛，没有找到正确的课表信息文件！")
      print " there are no correct class_require info"

  def import_groups(self,event=None):
    try:
      fpath = self.select_path(message=u"请您选择包含了 组结构 信息的文件夹");
      num = 0;
      for f in os.listdir(fpath):
        t = f.strip().split(".");
        if t[-1].upper()=="CSV" and os.path.isfile(fpath+"/"+f):
          self.mframe.zbc.read_groups_from_csv(fpath+"/"+f);
          num += 1;
      self.op_status.SetValue(u"南无阿弥陀佛，已经获取"+unicode(num)+u"张 小组结构 信息文件！")
    except:
      self.op_status.SetValue(u"南无阿弥陀佛，没有找到正确的 小组结构 信息文件！")
      print " there are no correct groups info"
    print "import groups"

  def import_semester(self,event=None):
    try:
      fpath = self.select_path(message=u"请您选择包含了 学期 信息的文件夹");
      num = 0;
      for f in os.listdir(fpath):
        t = f.strip().split(".");
        if t[-1].upper()=="CSV" and os.path.isfile(fpath+"/"+f):
          self.mframe.zbc.read_semester_from_csv(fpath+"/"+f);
          num += 1;
      self.op_status.SetValue(u"南无阿弥陀佛，已经获取"+unicode(num)+u"张 学期 信息文件！")
    except:
      self.op_status.SetValue(u"南无阿弥陀佛，没有找到正确的 学期 信息文件！")
      print " there are no correct semester info"
    print "import semester"

  #output all the records into a csv file to let people see his records_history
  #current don't support
  def output_records(self,event):
    re = self.mframe.zbc.db.get_history_records(uname=self.mframe.zbc.student_id);
    fname = self.save_file(u"南无阿弥陀佛，请您选择另存为文件名: records.csv",default_name=os.getcwd()+"/records_"+str(time.time())+".csv");
    f = open(fname,"w");
    w=csv.writer(f,lineterminator='\n');
    t=[u'法名',u'届别',u'课程名称',u'课程类型',u"统计类型",u'完成传承数',u'完成法本',u'完成共修',u'座次(观修)',u'本次观修量(观修/顶礼)',u'完成时间',u'填表时间',u'undo 状态'];
    w.writerow([get_val_unicode(item,self.mframe.zbc.codetype) for item in t]);
    for row in re:
      w.writerow([
        get_val_unicode(row[0],self.mframe.zbc.codetype),
        get_val_unicode(row[1],self.mframe.zbc.codetype),
        get_val_unicode(row[2],self.mframe.zbc.codetype),
        get_val_unicode(row[3],self.mframe.zbc.codetype),
        get_val_unicode(row[4],self.mframe.zbc.codetype),
        get_val_unicode(row[5],self.mframe.zbc.codetype),
        get_val_unicode(row[6],self.mframe.zbc.codetype),
        get_val_unicode(row[7],self.mframe.zbc.codetype),
        get_val_unicode(row[8],self.mframe.zbc.codetype),
        get_val_unicode(row[9],self.mframe.zbc.codetype),
        time_int_str(row[10]),
        time_int_str(row[11]),
        get_val_unicode(row[12],self.mframe.zbc.codetype),
      ]);
    f.close();
    self.op_status.SetValue(u"南无阿弥陀佛，个人学修记录已经正确导出到csv文件，请您查收！")
    print "flower amtf flower"

  def output_p_stat(self,event):
    student=[ [self.mframe.zbc.student_id,
               self.mframe.zbc.real_name,
               self.mframe.zbc.jiebie
               ] ];
    semester=self.mframe.zbc.db.get_semester(self.mframe.zbc.jiebie);
    class_require=self.mframe.zbc.db.get_all_r_class(
      jiebie = self.mframe.zbc.jiebie,
    );
    records=self.mframe.zbc.db.get_records(
      jiebie=self.mframe.zbc.jiebie,
      uname=self.mframe.zbc.student_id,
    );

    self.statistic(student,semester,class_require,records,stat_only=True);

    self.op_status.SetValue(u"南无阿弥陀佛，个人学修统计信息已经正确导出到csv文件，请您查收！")

    pass;

  def output_statistic(self,event):
    #out put like:
    #法名+届别+學期
    all_student=self.mframe.zbc.db.get_student();
    all_semester=self.mframe.zbc.db.get_semester();
    all_class_require=self.mframe.zbc.db.get_all_r_class();
    all_records=self.mframe.zbc.db.get_records();

    self.statistic(all_student,all_semester,all_class_require,all_records,stat_only=False);
    self.op_status.SetValue(u"南无阿弥陀佛，所有学员统计信息已保存，请您查收！")

  def statistic(self,all_student,all_semester,all_class_require,all_records,stat_only=False):
    #prepare for jiebie + semester
    # sitem=self.mframe.zbc.sitem;

    rr_jiebie={};
    r_semester={};
    r_jiebie={};
    name_map={}
    #prepare for student_id + jiebie + semester
    for row in all_student:
      name=row[0]
      jiebie=row[2]
      if name not in name_map:
        name_map[name]=1;
      if jiebie not in all_semester:
        continue;
      if jiebie not in rr_jiebie:
        rr_jiebie[jiebie]=["all"];#deepcopy({jiebie:r_jiebie[jiebie]});# name->jiebie
      rr_jiebie[jiebie].append(name);

    for jiebie in rr_jiebie:
      #statistic record
      if jiebie not in r_jiebie:
        r_jiebie[jiebie]={};
      for name in rr_jiebie[jiebie]:
        r_jiebie[jiebie][name]=deepcopy(self.mframe.zbc.stat_item);# name->jiebie

      if jiebie not in r_semester:
        r_semester[jiebie]={}
        for semester in all_semester[jiebie]:
          r_semester[jiebie][semester]={}
          for name in rr_jiebie[jiebie]:
            r_semester[jiebie][semester][name]=deepcopy(self.mframe.zbc.stat_item); #name->jiebie->semester

    real_data_jiebie={} #requirement for this jiebie
    real_data_semester={} #requirement for this semester
    for jiebie in rr_jiebie:
      #make sure there are at least one user in this jiebie
      # if jiebie in rr_jiebie:#can be deleted
        if jiebie not in real_data_jiebie:
          real_data_jiebie[jiebie]={}
          for name in rr_jiebie[jiebie]:
            real_data_jiebie[jiebie][name]= deepcopy(self.mframe.zbc.stat_item);

        for semester in all_semester[jiebie]:
          if jiebie not in real_data_semester:
            real_data_semester[jiebie] = {}
          if semester not in real_data_semester[jiebie]:
            real_data_semester[jiebie][semester]={};
          for name in rr_jiebie[jiebie]:
            real_data_semester[jiebie][semester][name]= deepcopy(self.mframe.zbc.stat_item);

    display_class={}
    for row in all_class_require:
      semester=row[0];
      jiebie=row[1]
      type = row[3]
      stat_type = row[4]
      course_name = row[2]

      if jiebie not in rr_jiebie: #we don't need to display jiebie without user apply for it.
        continue;

      #jiebie,semester,course_name
      if jiebie not in display_class:
        display_class[jiebie]={};
      if semester not in display_class[jiebie]:
        display_class[jiebie][semester]={};
      if type not in display_class[jiebie][semester]:
        display_class[jiebie][semester][type]={};
      display_class[jiebie][semester][type][course_name]=row;

      if type==u"主修":
        r_jiebie[jiebie]["all"][0] += get_int(row[5])
        r_jiebie[jiebie]["all"][1] += get_int(row[6])
        r_jiebie[jiebie]["all"][2] += get_int(row[7])

        r_semester[jiebie][semester]["all"][0] += get_int(row[5])
        r_semester[jiebie][semester]["all"][1] += get_int(row[6])
        r_semester[jiebie][semester]["all"][2] += get_int(row[7])

      elif type==u"限制性课程":
        r_jiebie[jiebie]["all"][3] += get_int(row[5])
        r_jiebie[jiebie]["all"][4] += get_int(row[6])

        r_semester[jiebie][semester]["all"][3] += get_int(row[5])
        r_semester[jiebie][semester]["all"][4] += get_int(row[6])

      elif type==u"观修":
        r_jiebie[jiebie]["all"][5] += get_int(row[8])
        r_jiebie[jiebie]["all"][6] += get_int(row[10])

        r_semester[jiebie][semester]["all"][5] += get_int(row[8])
        r_semester[jiebie][semester]["all"][6] += get_int(row[10])

      elif type==u"顶礼":
        r_jiebie[jiebie]["all"][7] += get_int(row[10])
        r_semester[jiebie][semester]["all"][7] += get_int(row[10])

    #do statistication for all the records.
    #name,jiebie,semester: statistical
    all_course={} # all records for each records

    #do statistic
    for row in all_records:
      name = row[11];
      jiebie = row[1]
      semester = row[0]
      type = row[3]
      st_type=row[17]
      course_name = row[2]
      #initial index for records
      if name==None:
        continue;
      if jiebie not in all_course:
        all_course[jiebie]={}
      if semester not in all_course[jiebie]:
        all_course[jiebie][semester]={}
      if type not in all_course[jiebie][semester]:
        all_course[jiebie][semester][type]={};
      if course_name not in all_course[jiebie][semester][type]:
        all_course[jiebie][semester][type][course_name]={}
      all_course[jiebie][semester][type][course_name][name]=row;#course name
      # try:
      if name in name_map and jiebie in r_jiebie and name in r_jiebie[jiebie]:
        if type==u"主修":
            r_jiebie[jiebie][name][0]+=get_int(row[12]);
            r_jiebie[jiebie][name][1]+=get_int(row[13]);
            r_jiebie[jiebie][name][2]+=get_int(row[14]);
            r_semester[jiebie][semester][name][0]+=get_int(row[12]);
            r_semester[jiebie][semester][name][1]+=get_int(row[13]);
            r_semester[jiebie][semester][name][2]+=get_int(row[14]);
        elif type==u"限制性课程":
            r_jiebie[jiebie][name][3]+=get_int(row[12]);
            r_jiebie[jiebie][name][4]+=get_int(row[13]);
            r_semester[jiebie][semester][name][3]+=get_int(row[12]);
            r_semester[jiebie][semester][name][4]+=get_int(row[13]);
        elif type==u"观修":
            r_jiebie[jiebie][name][5]+=get_int(row[15]);
            r_jiebie[jiebie][name][6]+=get_int(row[16]);
            r_semester[jiebie][semester][name][5]+=get_int(row[15]);
            r_semester[jiebie][semester][name][6]+=get_int(row[16]);
        elif type==u"顶礼":
            r_jiebie[jiebie][name][7]+=get_int(row[16]);
            r_semester[jiebie][semester][name][7]+=get_int(row[16]);
        else:
          pass;
      # except:
      #   continue;
    #
    try:
      import os;
      fname = self.save_file(u"南无阿弥陀佛，请您选择另存为文件名: statistic.csv",default_name=os.getcwd()+"/statistic.csv");
      self.mframe.zbc.store_into_csv(all_course,display_class,rr_jiebie,\
           r_jiebie,r_semester,fname,stat_only);

    except:
      pass;
    # print sd;
    pass;


class zbc_attendance(wx.Panel):
  def __init__(self, parent , mframe):
    self.mframe = mframe;
    self.mframe = mframe;
    wx.Panel.__init__(self, parent,size=(3000,3000))
    self.SetBackgroundColour((255,255,255));

    #drop box list
    #mayjor
    box_title = wx.BoxSizer(wx.HORIZONTAL);
    major_list=[u"所有主修",]
    major_list.extend(self.mframe.zbc.major);
    self.major_choice = wx.Choice(self,wx.ID_ANY,choices=major_list,size=(150,-1),)
    zhxiu=u"所有主修";
    if self.mframe.zbc.jiebie in self.mframe.zbc.major_jiebie:
      zhxiu=self.mframe.zbc.major_jiebie[self.mframe.zbc.jiebie];
    self.major_choice.SetStringSelection(zhxiu)
    self.major_choice.Bind(wx.EVT_CHOICE, self.major_change)
    box_title.Add(self.major_choice, 0, wx.ALL|wx.LEFT|wx.TOP, 5)

    #jiebie
    jiebie_list=[u"所有届别",self.mframe.zbc.jiebie,]
    self.jiebie_choice = wx.Choice(self,wx.ID_ANY,choices=jiebie_list,size=(150,-1),)
    self.jiebie_choice.SetStringSelection(self.mframe.zbc.jiebie)
    self.jiebie_choice.Bind(wx.EVT_CHOICE, self.jiebie_change)
    box_title.Add(self.jiebie_choice, 0, wx.ALL|wx.LEFT|wx.TOP, 5)

    #class_room
    cr = self.mframe.zbc.db.get_class_room(self.mframe.zbc.jiebie);
    class_room_list = [];
    for r in cr:
      class_room_list.append(r[0]);
    class_room_list.sort();
    class_room_list.insert(0,u"所有小组");
    # class_room_list=[u"所有小组",self.mframe.zbc.class_room,]
    self.class_room_choice = wx.Choice(self,wx.ID_ANY,choices=class_room_list,size=(150,-1),)
    self.class_room_choice.SetStringSelection(self.mframe.zbc.class_room)
    self.class_room_choice.Bind(wx.EVT_CHOICE, self.class_room_change)
    box_title.Add(self.class_room_choice, 0, wx.ALL|wx.LEFT|wx.TOP, 5)

    #student_id
    # student_list=[u"所有学员",]
    # self.student_choice = wx.Choice(self,wx.ID_ANY,choices=student_list,size=(150,-1),)
    # self.student_choice.SetStringSelection(u"所有学员")
    # self.student_choice.Bind(wx.EVT_CHOICE, self.student_change)
    # box_title.Add(self.student_choice, 0, wx.ALL|wx.LEFT|wx.TOP, 5)

    #learning_time
    box_subtitle = wx.BoxSizer(wx.HORIZONTAL);
    xpos=[0,3]
    self.label1 = pkc_create_static_text(self,xpos,size=(67,-1), value=u"共修时间");
    self.learning_time=pkc_create_text(self,xpos,value=time_int_str(time.time()),style=wx.BORDER);
    box_subtitle.Add(self.label1, 0, wx.ALL|wx.LEFT|wx.TOP, 5)
    box_subtitle.Add(self.learning_time, 0, wx.ALL|wx.LEFT|wx.TOP, 5)

    #class_name
    class_list=[u"",]
    self.label2 = pkc_create_static_text(self,xpos,size=(67,-1), value=u"共修课程");
    self.course_choice = wx.Choice(self,wx.ID_ANY,choices=class_list,size=(150,-1),)
    self.course_choice.SetStringSelection(u"所有学员")
    self.course_choice.Bind(wx.EVT_CHOICE, self.course_change)
    box_subtitle.Add(self.label2, 0, wx.ALL|wx.LEFT|wx.TOP, 5)
    box_subtitle.Add(self.course_choice, 0, wx.ALL|wx.LEFT|wx.TOP, 5)

    #remarks
    self.add_course_b =  wx.Button(self, wx.ID_ANY, u"增加课程", pos=(0, 0));
    self.Bind(wx.EVT_BUTTON, partial(self.add_course, ),self.add_course_b,);
    self.new_course_t=pkc_create_text(self,xpos,value="",style=wx.BORDER);
    box_subtitle.Add(self.add_course_b, 0, wx.ALL|wx.LEFT|wx.TOP, 5)
    box_subtitle.Add(self.new_course_t, 0, wx.ALL|wx.LEFT|wx.TOP, 5)

    box_button = wx.BoxSizer(wx.HORIZONTAL);
    self.flush_list =  wx.Button(self, wx.ID_ANY, u"刷新考勤名单", pos=(0, 0));
    self.Bind(wx.EVT_BUTTON, partial(self.update_page, ),self.flush_list,);
    box_button.Add(self.flush_list, 0, wx.ALL|wx.LEFT|wx.TOP, 5)

    finish_shangke =  wx.Button(self, wx.ID_ANY, u"记录准时上课考勤", pos=(0, 0));
    self.Bind(wx.EVT_BUTTON, partial(self.finish_kaoqin,para="join" ),finish_shangke,);
    box_button.Add(finish_shangke, 0, wx.ALL|wx.LEFT|wx.TOP, 5)

    finish_xiake =  wx.Button(self, wx.ID_ANY, u"记录按时下课考勤", pos=(0, 0));
    self.Bind(wx.EVT_BUTTON, partial(self.finish_kaoqin,para="leave" ),finish_xiake,);
    box_button.Add(finish_xiake, 0, wx.ALL|wx.LEFT|wx.TOP, 5)

    restart_kaoqin =  wx.Button(self, wx.ID_ANY, u"清空缓存", pos=(0, 0));
    self.Bind(wx.EVT_BUTTON, partial(self.restart_kaoqin, ),restart_kaoqin,);
    box_button.Add(restart_kaoqin, 0, wx.ALL|wx.LEFT|wx.TOP, 5)

    restart_kaoqin =  wx.Button(self, wx.ID_ANY, u"导出考勤列表", pos=(0, 0));
    self.Bind(wx.EVT_BUTTON, partial(self.output_kaoqin, ),restart_kaoqin,);
    box_button.Add(restart_kaoqin, 0, wx.ALL|wx.LEFT|wx.TOP, 5)


    # lists
    font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    boldfont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    boldfont.SetWeight(wx.BOLD)
    boldfont.SetPointSize(12)

    '''
    self.ultimateList = ULC.UltimateListCtrl(self, agwStyle = wx.LC_REPORT
                                     | wx.LC_VRULES
                                     | wx.LC_HRULES
                                     |ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
                                     |ULC.ULC_NO_HIGHLIGHT)

    info = ULC.UltimateListItem()
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
    info._image = []
    info._format = wx.LIST_FORMAT_LEFT
    info._kind = 1
    info._text = u'届别'
    self.ultimateList.InsertColumnInfo(0, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text =  u'班级'
    info._font =  font
    self.ultimateList.InsertColumnInfo(1, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text =  u'学员id'
    info._font =  font
    self.ultimateList.InsertColumnInfo(2, info)

    info = ULC.UltimateListItem()
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._format = wx.LIST_FORMAT_LEFT
    info._text = u'学员昵称'
    info._font = font
    info._image = []
    self.ultimateList.InsertColumnInfo(3, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text =  u'圆满共修'
    info._font =  font
    self.ultimateList.InsertColumnInfo(4, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text =  u'按时上课'
    info._font =  font
    self.ultimateList.InsertColumnInfo(5, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text =  u'按时下课'
    info._font =  font
    self.ultimateList.InsertColumnInfo(6, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text =  u'当前状态'
    info._font =  font
    self.ultimateList.InsertColumnInfo(7, info)


    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text = u'备注'
    info._font = font
    self.ultimateList.InsertColumnInfo(8, info)

    self.ultimateList.SetColumnWidth(0, 97)
    self.ultimateList.SetColumnWidth(1, 97)
    self.ultimateList.SetColumnWidth(2, 97)
    self.ultimateList.SetColumnWidth(3, 137)
    self.ultimateList.SetColumnWidth(4, 87)
    self.ultimateList.SetColumnWidth(5, 87)
    self.ultimateList.SetColumnWidth(6, 87)
    self.ultimateList.SetColumnWidth(7, 100)
    self.ultimateList.SetColumnWidth(8, 150)
    '''
    box = wx.BoxSizer(wx.VERTICAL)
    box.Add(box_title, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=5)
    box.Add(box_subtitle, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=5)
    box.Add(box_button, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=5)
    # box.Add(self.ultimateList, 1, wx.EXPAND)
    self.SetSizer(box)
    box.Fit(self)

    self.class_room_change();

    # self.refresh_major_list();
    # self.update_page();

  def onClick(self, event):
    self.update_page();

  def output_kaoqin(self, event):
    jiebie = self.jiebie_choice.GetStringSelection();
    cname = self.course_choice.GetStringSelection();
    rec = self.mframe.zbc.db.get_kaoqin(jiebie,cname,self.mframe.zbc.student_id);
    if rec == None:return;
    sdict={}
    for r in rec:
      if r[5] == "join":
        if r[3] not in sdict:
          sdict[r[3]]=[0,0,r[4]];
        sdict[r[3]][0] = 1;
      elif r[5]=="leave":
        if r[3] not in sdict:
          sdict[r[3]]=[0,0,r[4]];
        sdict[r[3]][1] = 1;
    #sort by YY number
    slist =[];
    for s in sdict:
      rp = 0;
      if sdict[s][0]==1 and sdict[s][1]==1:
        rp = 1;
      slist.append([sdict[s][2].encode('utf8'),s,sdict[s][0],sdict[s][1],rp]);
    slist.sort();

    fname = jiebie+cname+".csv";
    f=open(fname,'wb');
    w=csv.writer(f,lineterminator='\n');
    w.writerow([u"YY号码".encode('utf-8'),
                u"上课签到".encode('utf-8'),
                u"下课签到".encode('utf-8'),
                u"考勤结果".encode('utf-8'),
                u"共修昵称".encode('utf-8'),
                ]);
    for row in slist:
      w.writerow(['YY'+str(row[1]),row[2],row[3],row[4],row[0]]);
    f.close();


  def finish_kaoqin(self,event,para):
    jiebie = self.jiebie_choice.GetStringSelection();
    cname = self.course_choice.GetStringSelection();
    while self.mframe.sq.qsize()>0:
      nlist = self.mframe.sq.get();
      #nlist {yyID:[nick_name,time]}
      #use yyID as student_ID
      vlist = [];
      for sid,val in nlist.iteritems():
        vlist.append([jiebie,cname,self.mframe.zbc.student_id,sid,val[0],para,val[1]]);
      self.mframe.zbc.db.replace_into_many('kaoqin_table',vlist);

    print "successful get items"

  def restart_kaoqin(self,event):
    self.mframe.sq.empty();

  def add_course(self,event):
    cname = self.new_course_t.GetValue();
    if len(cname)<2:
      return;
    jiebie = self.jiebie_choice.GetStringSelection();
    clist = [jiebie,cname,u'主修',u'共修',1,1,1,0,0,0,time.time()]
    self.mframe.zbc.db.replace_into('class_require',clist);
    #change the couse_choice
    self.course_choice.SetStringSelection(cname);
    self.course_choice.Refresh()

  def refresh_major_list(self):
    self.major_choice.Clear();
    self.major_choice.Append(u"所有主修");

    for m in self.mframe.zbc.major:
      self.major_choice.Append(m);

    zhxiu=u"所有主修";
    if self.mframe.zbc.jiebie in self.mframe.zbc.major_jiebie:
      zhxiu=self.mframe.zbc.major_jiebie[self.mframe.zbc.jiebie];
    self.major_choice.SetStringSelection(zhxiu)
    # self.major_choice.SetSelection(0)
    self.major_choice.Refresh();

  def major_change(self,inst):
    self.jiebie_choice.Clear();
    self.jiebie_choice.Append(u"所有届别");

    major = self.major_choice.GetString(self.major_choice.GetCurrentSelection());

    if major == u"所有主修":
      major = None;
    rows = self.mframe.zbc.db.get_jiebie(major);

    for row in rows:
      self.jiebie_choice.Append(row[0]);

    self.jiebie_choice.SetSelection(0);
    self.jiebie_choice.Refresh();
    pass

  #jiebie change -> update the class_room information
  def jiebie_change(self,inst):
    self.class_room_choice.Clear();
    self.class_room_choice.Append(u"所有小组");

    jiebie = self.jiebie_choice.GetString(self.jiebie_choice.GetCurrentSelection());

    rows = self.mframe.zbc.db.get_class_room(jiebie);

    cr = self.mframe.zbc.db.get_class_room(self.mframe.zbc.jiebie);
    class_room_list = [];
    for r in cr:
      class_room_list=r[0];
    class_room_list.sort();
    class_room_list.insert(0,u"所有小组");

    for cr in class_room_list:
      self.class_room_choice.Append(cr);

    self.class_room_choice.SetSelection(0);
    self.class_room_choice.Refresh();

  #class_room change --> Update the courses
  def class_room_change(self,inst=None):
    self.course_choice.Clear();

    jiebie = self.jiebie_choice.GetString(self.jiebie_choice.GetCurrentSelection());

    #chose inner the last 2 week and next 2 weeks
    ctime=int(time.time());

    # rows = self.mframe.zbc.db.get_courses_required(jiebie,type=u"主修",stime=ctime-1209600,etime=ctime+1209600);
    rows = self.mframe.zbc.db.get_courses_required(jiebie,type=u"主修");

    # course_list=[]
    # for row in rows:
    #   course_list.append(row[0]);
    # course_list.sort();
    # self.course_choice.AppendItems(course_list)
    for row in rows:
      self.course_choice.Append(row[0]);

    self.course_choice.SetSelection(0);
    self.course_choice.Refresh();
    self.update_page();
    pass

  def update_page(self,inst=None):
    #Update the UltimateList
    records=[];

    jiebie = self.jiebie_choice.GetString(self.jiebie_choice.GetCurrentSelection());
    class_room = self.class_room_choice.GetString(self.class_room_choice.GetCurrentSelection());
    course_name = self.course_choice.GetString(self.course_choice.GetCurrentSelection());

    if course_name == u"":
      course_name=None;
    if jiebie == u"所有届别":
      jiebie=None;
    if class_room== u"所有小组":
      class_room = None;

    rows = self.mframe.zbc.db.get_attendence_of_student(jiebie=jiebie,class_room=class_room,course_name=course_name);
    self.update_ultimateList(rows);
    pass;

  def update_ultimateList(self,rec):
    pass;
    '''
    self.ultimateList.DeleteAllItems();
    idx = 0;

    disable_flag=False;
    if u"" == self.course_choice.GetString(self.course_choice.GetCurrentSelection()):
      disable_flag=True;

    for i in range(len(rec)):
      t = rec[i][10].encode("utf8");
      rec[i][10]= rec[i][0]
      rec[i][0] = t;
    rec.sort();
    for i in range(len(rec)):
      rec[i][0] = rec[i][0].decode("utf8");

    for row in rec:
      sid = row[10];
      jiebie = row[1];
      course_name = row[2];
      class_room = row[3];
      report = row[4]
      attend_ot = row[5];
      leave_ot = row[6]
      if row[7]==None:
        remarks="";
      else:
        remarks = row[7]
      insert_time = row[8]
      status = row[9]
      nick_name = row[0]
      #jiebie
      self.ultimateList.InsertStringItem(idx,unicode(jiebie))
      #class_room
      self.ultimateList.SetStringItem(idx,1,unicode(class_room));
      #student_id
      self.ultimateList.SetStringItem(idx,2,unicode(sid));
      #student_nick_name
      self.ultimateList.SetStringItem(idx,3,unicode(nick_name));
      #report
      report_btn=wx.Button(self.ultimateList, wx.ID_ANY, unicode(report), pos=(0, 0),size=(73,25));
      self.ultimateList.SetItemWindow(idx, col=4, wnd=report_btn, expand=False)
      report_btn.Bind(wx.EVT_BUTTON, partial(self.click_report,para=list(row)))

      #attend on time
      attime_btn=wx.Button(self.ultimateList, wx.ID_ANY, unicode(attend_ot), pos=(0, 0),size=(73,30));
      self.ultimateList.SetItemWindow(idx, col=5, wnd=attime_btn, expand=False)
      attime_btn.Bind(wx.EVT_BUTTON, partial(self.click_attend,para=list(row)))

      #leave on time
      ltime_btn=wx.Button(self.ultimateList, wx.ID_ANY, unicode(leave_ot), pos=(0, 0),size=(73,30));
      self.ultimateList.SetItemWindow(idx, col=6, wnd=ltime_btn, expand=False)
      ltime_btn.Bind(wx.EVT_BUTTON, partial(self.click_leave,para=list(row)))

      #remarks
      remarks_txt = wx.TextCtrl(self.ultimateList,value=unicode(remarks),pos=(0,0),size=(80,25),style=wx.TE_RICH|wx.TE_PROCESS_ENTER);
      self.ultimateList.SetItemWindow(idx, col=8, wnd=remarks_txt, expand=True);
      # remarks_txt.Bind(wx.EVT_TEXT_ENTER, partial(self.change_remarks,para=list(row)))
      #EVT_SET_FOCUS:when focus on; EVT_KILL_FOCUS,when it is unfocused
      remarks_txt.Bind(wx.EVT_KILL_FOCUS, partial(self.change_remarks,para=list(row)))

      # Status
      status_list=[u"精进闻思",u"新增",u"退失边缘",u"退失",u"圆满"]
      self.status_choice=wx.Choice(self.ultimateList,wx.ID_ANY,choices=status_list,size=(100,-1),)
      self.status_choice.SetStringSelection(unicode(status))
      self.ultimateList.SetItemWindow(idx, 7, self.status_choice, expand=True);
      self.status_choice.Bind(wx.EVT_CHOICE, partial(self.status_change,para=list(row),rmk=remarks_txt))


      if disable_flag:
        report_btn.Disable()
        attime_btn.Disable()
        ltime_btn.Disable()
        remarks_txt.Disable()
        self.status_choice.Disable();

      idx += 1;

    self.ultimateList.Refresh()
    '''
    pass;

  def click_report(self,event,para):
    cb=event.GetEventObject();
    rp = para[4];
    if rp==u"圆满":
      para[4]=u"缺席"
    elif rp==u"缺席":
      para[4]=u"圆满"
    else:
      para[4] = u"圆满"
    param = [para[i] for i in range(9)];
    #update course name
    param[2] = self.course_choice.GetString(self.course_choice.GetCurrentSelection());
    #update insert_time
    if param[8]==None:
      param[8] = 0;
    param[-1]=int(time.time());#insert the update time
    self.mframe.zbc.db.update_attendence("attendance",param,report=para[4],course_name=param[2]);
    cb.SetLabel(para[4]);
    print para;
    print "click_report"

  def click_attend(self,event,para):
    cb=event.GetEventObject();
    rp = para[5];
    if rp==u"按时":
      para[5]=u"迟到"
    elif rp==u"迟到":
      para[5]=u"按时"
    else:
      para[5] = u"按时"
    param = [para[i] for i in range(9)];
    #update course name
    param[2] = self.course_choice.GetString(self.course_choice.GetCurrentSelection());
    #update insert_time
    if param[8]==None:
      param[8] = 0;
    # param[-1]=int(time.time())
    self.mframe.zbc.db.update_attendence("attendance",param,attend_ot=para[5],course_name=param[2]);
    cb.SetLabel(para[5]);
    print para;
    print "click_attend"

  def click_leave(self,event,para):
    cb=event.GetEventObject();
    rp = para[6];
    if rp==u"按时":
      para[6]=u"早退"
    elif rp==u"早退":
      para[6]=u"按时"
    else:
      para[6] = u"按时"
    param = [para[i] for i in range(9)];
    #update course name
    param[2] = self.course_choice.GetString(self.course_choice.GetCurrentSelection());
    #update insert_time
    if param[8]==None:
      param[8] = 0;
    self.mframe.zbc.db.update_attendence("attendance",param,leave_ot=para[6],course_name=param[2]);
    cb.SetLabel(para[6]);
    print para;
    print "click_leave"

  #上期应报人数，新增，退失，本期应保，退失边缘，闻思圆满，闻思为圆满，传承法本圆满，传承法本未圆满，累计滞后15课，
  #新增，精进闻思，退失，退失边缘
  def status_change(self,event,para,rmk):
    cb=event.GetEventObject();
    status = para[9];

    para[9] = cb.GetString(cb.GetCurrentSelection());

    student_id = para[0]
    jiebie = para[1]
    status = para[9];
    class_room=para[3]

    ap=self.mframe.zbc.db.get_student_latest(jiebie=jiebie,student_id=student_id,class_room=class_room);
    if len(ap)==0:
      print jiebie,student_id,class_room," dont exist"
      return;
    tparam=[t for t in ap[0]]
    tparam[-3]=status;
    tparam[-2]=rmk.GetValue();#remark_text
    tparam[-1]=self.mframe.zbc.student_id;
    tparam.append(int(time.time()))
    if ap[0][6]==u"" or ap[0][6]==None:
      self.mframe.zbc.db.update_student_status(tparam);
    else:
      self.mframe.zbc.db.replace_into("student",tparam);

    cb.SetLabel(para[9]);
    print para;
    print "status_change"

  def change_remarks(self,event,para):
    cb=event.GetEventObject();
    if para[7] == cb.GetValue() or cb.GetValue()<3:
      return;
    else:
      para[7]=cb.GetValue();

    param = [para[i] for i in range(9)];
    #update course name
    param[2] = self.course_choice.GetString(self.course_choice.GetCurrentSelection());
    #update insert_time
    if param[8]==None:
      param[8] = int(time.time());
    if param[7]==None:
      param[7]='';
    self.mframe.zbc.db.update_attendence("attendance",param,remarks=para[7],course_name=param[2]);
    cb.SetLabel(para[7]);
    print para;
    print "change_remarks"

  def get_student_info(self):
    pass;

  def student_change(self,inst):
    pass

  def course_change(self,inst):
    self.update_page()
    pass

  def test_update(self):
    self.jiebie_choice.Clear();
    self.jiebie_choice.AppendItems(["abcd","dddd","ooo"])
    self.jiebie_choice.SetStringSelection("ooo")
    self.jiebie_choice.Refresh();
    print "---"


class zbc_attendance_statistic(wx.Panel):
  def __init__(self, parent , mframe):
    self.mframe = mframe;
    self.mframe = mframe;
    wx.Panel.__init__(self, parent,size=(3000,3000))
    self.SetBackgroundColour((255,255,255));

    self.__init_stat();

    #check box list
    #major
    self.major_cb = wx.CheckBox(self, -1, u'按主修统计', (10, 30))
    self.jiebie_cb = wx.CheckBox(self, -1, u'按届别统计', (10, 30))
    self.department_cb = wx.CheckBox(self, -1, u'按大组统计', (10, 30))
    self.subdpt_cb = wx.CheckBox(self, -1, u'按中组统计', (10, 30))
    self.class_room_cb = wx.CheckBox(self, -1, u'按小组统计', (10, 30))
    self.student_cb = wx.CheckBox(self, -1, u'按个人统计', (10, 30))

    box = wx.BoxSizer(wx.VERTICAL);
    box1 = wx.BoxSizer(wx.HORIZONTAL);
    box1.Add(self.major_cb,0, wx.ALL|wx.LEFT|wx.TOP, 5)
    box1.Add(self.jiebie_cb,0, wx.ALL|wx.LEFT|wx.TOP, 5)
    box1.Add(self.department_cb,0, wx.ALL|wx.LEFT|wx.TOP, 5)
    box1.Add(self.subdpt_cb,0, wx.ALL|wx.LEFT|wx.TOP, 5)
    box1.Add(self.class_room_cb,0, wx.ALL|wx.LEFT|wx.TOP, 5)
    box1.Add(self.student_cb,0, wx.ALL|wx.LEFT|wx.TOP, 5)

    box_time = wx.BoxSizer(wx.HORIZONTAL);
    box_button = wx.BoxSizer(wx.HORIZONTAL);
    self.gen_stat =  wx.Button(self, wx.ID_ANY, u"汇总统计", pos=(0, 3));
    self.Bind(wx.EVT_BUTTON, partial(self.click_gen_stat, ),self.gen_stat,);
    box_button.Add(self.gen_stat, 0, wx.ALL|wx.LEFT|wx.TOP, 0)

    #this is for the
    self.save_stat =  wx.Button(self, wx.ID_ANY, u"导出汇总统计excel", pos=(0, 0));
    self.Bind(wx.EVT_BUTTON, partial(self.output_stat, ),self.save_stat,);
    box_button.Add(self.save_stat, 0, wx.ALL|wx.LEFT|wx.TOP, 0)

    #this is for the 各项具体数据
    self.save_detail_stat =  wx.Button(self, wx.ID_ANY, u"生成并导出各项修行统计excel", pos=(0, 0));
    self.Bind(wx.EVT_BUTTON, partial(self.output_detail_stat, ),self.save_detail_stat,);
    box_button.Add(self.save_detail_stat, 0, wx.ALL|wx.LEFT|wx.TOP, 0)

    stat_range=[u"",u"所有时间段",u"今年上学期",u"今年下学期",u"今年上学期期中",
                u"今年上学期期末",u"今年下学期期中",u"今年下学期期末",]

    xpos=[0,3]
    self.sr_choice = wx.Choice(self,wx.ID_ANY,choices=stat_range,size=(150,-1),)
    self.sr_choice.SetStringSelection(u"所有时间段")
    self.sr_choice.Bind(wx.EVT_CHOICE, self.stat_range_change)

    self.labels = pkc_create_static_text(self,xpos,size=(37,-1), value=u"从");
    self.stime_range=pkc_create_text(self,xpos,value=time_int_str_day(time.time()-365*24*3600),style=wx.BORDER);
    self.labele = pkc_create_static_text(self,xpos,size=(37,-1), value=u"到");
    self.etime_range=pkc_create_text(self,xpos,value=time_int_str_day(time.time()),style=wx.BORDER);

    box_time.Add(self.sr_choice)
    box_time.Add(self.labels)
    box_time.Add(self.stime_range)
    box_time.Add(self.labele)
    box_time.Add(self.etime_range)

    # lists
    font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    boldfont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    boldfont.SetWeight(wx.BOLD)
    boldfont.SetPointSize(12)

    #this is for the final statistic
    self.ultimateList = ULC.UltimateListCtrl(self, agwStyle = wx.LC_REPORT
                                     | wx.LC_VRULES
                                     | wx.LC_HRULES
                                     |ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
                                     |ULC.ULC_NO_HIGHLIGHT)

    if self.mframe.type=="group":
      self.title_list=[u"分类/学号",u"专业/届别",u"上期应报人数",u"新增",u"退失",u"本期应报人数",u"精进闻思",
                u"已报数人数",u"未报数人数",u"退失边缘",u"闻思圆满",u"闻思未圆满",
                u"传承法本圆满",u"传承法本未圆满",u"累计滞后15课以上",u"限制性课程圆满",u"限制性课程未圆满",
                u"出勤率>=50%",u"出勤率<50%",u"观修跟上进度",u"观修落后进度"]
    elif self.mframe.type=="personal":
      self.title_list=[u"分类/学号",u"专业/届别",u"闻思圆满",u"闻思未圆满",
                u"传承法本圆满",u"传承法本未圆满",u"累计滞后15课以上",u"限制性课程圆满",u"限制性课程未圆满",
                u"出勤率>=50%",u"出勤率<50%",u"观修跟上进度",u"观修落后进度"]
    idx = 0;
    for title in self.title_list:
      info = ULC.UltimateListItem()
      info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
      info._image = []
      info._format = wx.LIST_FORMAT_LEFT
      info._kind = 1
      info._text = title;
      self.ultimateList.InsertColumnInfo(idx, info)
      self.ultimateList.SetColumnWidth(idx, max(87,len(title)*19));
      idx += 1;

    box.Add(box1, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=5)
    box.Add(box_time, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=5)
    box.Add(box_button, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=5)
    box.Add(self.ultimateList, 1, wx.EXPAND)
    self.SetSizer(box)
    box.Fit(self)

  def __init_stat(self):
    self.st_summary = [
                           u'主修缺听传承课数',
                           u'主修缺看法本课数',
                           u'个人实际共修出勤累计总次数',
                           u'限制性课程缺听光碟数',
                           u'限制性课程缺看法本数',
                           u'累计观修座次',
                           u'累计观修时间(分钟)',
                           ];
    self.st_course = [
                           u'听传承',
                           u'看法本',
                           u'参加共修',
                           ];
    self.st_xianzhi_course = [
                           u'听传承',
                           u'看法本',
                           ];
    self.st_guanxiu = [
                           u'观修座次',
                           u'观修时间',
                           ];
    self.st_teshu = [   ];
    self.st_semester = [
                           u'本学期主修听传承数',
                           u'本学期主修看法本数',
                           u'本学期个人实际共修出勤累计总次数',
                           u'本学期限制性课程听传承数',
                           u'本学期限制性课程看法本数',
                           u'本学期观修总圆满座次',
                           u'本学期观修总时间(分钟)',
                           ];

  def stat_range_change(self,event=None):
    ctime = time.time();
    val = self.sr_choice.GetString(self.sr_choice.GetCurrentSelection());

    fyear = str(time.localtime().tm_year);
    stime = fyear+"-01-01";
    shtime = fyear+"-03-08";
    mtime = fyear+"-05-31";
    mhtime = fyear+"-09-30";
    etime = fyear+"-12-31";

    if val == u"所有时间段":
      self.stime_range.SetValue("")
      self.etime_range.SetValue("")
    if val == u"今年上学期":
      self.stime_range.SetValue(stime)
      self.etime_range.SetValue(mtime)
    if val == u"今年下学期":
      self.stime_range.SetValue(mtime)
      self.etime_range.SetValue(etime)
    if val == u"今年上学期期中":
      self.stime_range.SetValue(stime)
      self.etime_range.SetValue(shtime)
    if val == u"今年上学期期末":
      self.stime_range.SetValue(shtime)
      self.etime_range.SetValue(mhtime)
    if val == u"今年下学期期中":
      self.stime_range.SetValue(mtime)
      self.etime_range.SetValue(mhtime)
    if val == u"今年下学期期末":
      self.stime_range.SetValue(mhtime)
      self.etime_range.SetValue(etime)


  def prepare_gen_stat(self,inst=None):
    #Update the UltimateList
    stime = time_str_int(self.stime_range.GetValue());
    etime = time_str_int(self.etime_range.GetValue());
    if etime != None:
      etime += 24*3600
    #-----------------------------------------------------------------------------
    #prepare for all student
    row_all_std = self.mframe.zbc.db.get_student_min(op="max");
    all_student={}
    all_student_sdt={}
    for row in row_all_std:
      jiebie = row[2]
      student_id = row[0]
      # status = row[6]
      # if status==None:
      #   continue;
      if jiebie not in all_student:
        all_student[jiebie] = {}
      all_student[jiebie][student_id]=row;
      if student_id not in all_student_sdt:
        all_student_sdt[student_id] = {};
      all_student_sdt[student_id][jiebie]=row;

    row_all_std = self.mframe.zbc.db.get_student_min();
    all_student_s={}
    all_student_s_sdt={};
    for row in row_all_std:
      jiebie = row[2]
      student_id = row[0]
      # status = row[6]
      # if status==None:
      #   continue;
      if jiebie not in all_student_s:
        all_student_s[jiebie] = {}
      all_student_s[jiebie][student_id]=row;
      if student_id not in all_student_s_sdt:
        all_student_s_sdt[student_id] = {};
      all_student_s_sdt[student_id][jiebie]=row;

    #prepare for all class_require
    row_all_class = self.mframe.zbc.db.get_all_r_class(stime=stime,etime=etime,);
    all_r_class = {}
    all_r_class_stat={}
    for row in row_all_class:
      jiebie = row[0]
      course_name = row[1]
      if jiebie not in all_r_class:
        all_r_class[jiebie]={}
        all_r_class_stat[jiebie]={}
      all_r_class[jiebie][course_name] = row;
      type = row[2];
      if type not in all_r_class_stat[jiebie]:
        all_r_class_stat[jiebie][type]=0;
      all_r_class_stat[jiebie][type] +=1;

    #prepare for all attendance all_attendance_sdt
    row_all_attendance = self.mframe.zbc.db.get_all_attendance(stime=stime,etime=etime,);
    all_attendance = {};
    all_attendance_sdt = {};
    for row in row_all_attendance:
      jiebie = row[1];
      student_id = row[0]
      course_name = row[2];
      if jiebie not in all_attendance:
        all_attendance[jiebie]={}
      if course_name not in all_attendance[jiebie]:
        all_attendance[jiebie][course_name]={};
      all_attendance[jiebie][course_name][student_id]=row;

      if student_id not in all_attendance_sdt:
        all_attendance_sdt[student_id]={}
      if jiebie not in all_attendance_sdt[student_id]:
        all_attendance_sdt[student_id][jiebie]={};
      all_attendance_sdt[student_id][jiebie][course_name]=row;

    #prepare for all records
    row_all_records = self.mframe.zbc.db.get_all_records(stime=stime,etime=etime,);
    all_records = {};
    all_records_sdt = {};
    for row in row_all_records:
      jiebie = row[1];
      student_id = row[0]
      course_name = row[2];
      if jiebie not in all_records:
        all_records[jiebie]={}
      if course_name not in all_records[jiebie]:
        all_records[jiebie][course_name]={};
      all_records[jiebie][course_name][student_id]=row;

      if student_id not in all_records_sdt:
        all_records_sdt[student_id]={}
      if jiebie not in all_records_sdt[student_id]:
        all_records_sdt[student_id][jiebie]={};

      all_records_sdt[student_id][jiebie][course_name]=row;

    return all_student,all_student_sdt,all_student_s,all_student_s_sdt\
            ,all_r_class,all_r_class_stat,all_attendance,all_attendance_sdt\
            ,all_records,all_records_sdt


  def statistic(self,all_student,all_semester,all_class_require,all_records,stat_only=False):
    #prepare for jiebie + semester
    # sitem=self.mframe.zbc.sitem;
    rr_jiebie={};
    r_semester={};
    r_jiebie={};
    name_map={}
    #prepare for student_id + jiebie + semester
    for row in all_student:
      name=row[0]
      jiebie=row[2]
      if name not in name_map:
        name_map[name]=1;
      if jiebie not in all_semester:
        continue;
      if jiebie not in rr_jiebie:
        rr_jiebie[jiebie]=["all"];#deepcopy({jiebie:r_jiebie[jiebie]});# name->jiebie
      rr_jiebie[jiebie].append(name);

    for jiebie in rr_jiebie:
      #statistic record
      if jiebie not in r_jiebie:
        r_jiebie[jiebie]={};
      for name in rr_jiebie[jiebie]:
        r_jiebie[jiebie][name]=deepcopy(self.mframe.zbc.stat_item);# name->jiebie

      if jiebie not in r_semester:
        r_semester[jiebie]={}
        for semester in all_semester[jiebie]:
          r_semester[jiebie][semester]={}
          for name in rr_jiebie[jiebie]:
            r_semester[jiebie][semester][name]=deepcopy(self.mframe.zbc.stat_item); #name->jiebie->semester

    real_data_jiebie={} #requirement for this jiebie
    real_data_semester={} #requirement for this semester
    for jiebie in rr_jiebie:
      #make sure there are at least one user in this jiebie
      # if jiebie in rr_jiebie:#can be deleted
        if jiebie not in real_data_jiebie:
          real_data_jiebie[jiebie]={}
          for name in rr_jiebie[jiebie]:
            real_data_jiebie[jiebie][name]= deepcopy(self.mframe.zbc.stat_item);

        for semester in all_semester[jiebie]:
          if jiebie not in real_data_semester:
            real_data_semester[jiebie] = {}
          if semester not in real_data_semester[jiebie]:
            real_data_semester[jiebie][semester]={};
          for name in rr_jiebie[jiebie]:
            real_data_semester[jiebie][semester][name]= deepcopy(self.mframe.zbc.stat_item);

    display_class={}
    for row in all_class_require:
      semester=row[0];
      jiebie=row[1]
      type = row[3]
      stat_type = row[4]
      course_name = row[2]

      if jiebie not in rr_jiebie: #we don't need to display jiebie without user apply for it.
        continue;

      #jiebie,semester,course_name
      if jiebie not in display_class:
        display_class[jiebie]={};
      if semester not in display_class[jiebie]:
        display_class[jiebie][semester]={};
      if type not in display_class[jiebie][semester]:
        display_class[jiebie][semester][type]={};
      display_class[jiebie][semester][type][course_name]=row;

      if type==u"主修":
        r_jiebie[jiebie]["all"][0] += get_int(row[5])
        r_jiebie[jiebie]["all"][1] += get_int(row[6])
        r_jiebie[jiebie]["all"][2] += get_int(row[7])

        r_semester[jiebie][semester]["all"][0] += get_int(row[5])
        r_semester[jiebie][semester]["all"][1] += get_int(row[6])
        r_semester[jiebie][semester]["all"][2] += get_int(row[7])

      elif type==u"限制性课程":
        r_jiebie[jiebie]["all"][3] += get_int(row[5])
        r_jiebie[jiebie]["all"][4] += get_int(row[6])

        r_semester[jiebie][semester]["all"][3] += get_int(row[5])
        r_semester[jiebie][semester]["all"][4] += get_int(row[6])

      elif type==u"观修":
        r_jiebie[jiebie]["all"][5] += get_int(row[8])
        r_jiebie[jiebie]["all"][6] += get_int(row[10])

        r_semester[jiebie][semester]["all"][5] += get_int(row[8])
        r_semester[jiebie][semester]["all"][6] += get_int(row[10])

      elif type==u"顶礼":
        r_jiebie[jiebie]["all"][7] += get_int(row[10])
        r_semester[jiebie][semester]["all"][7] += get_int(row[10])

    #do statistication for all the records.
    #name,jiebie,semester: statistical
    all_course={} # all records for each records

    #do statistic
    for row in all_records:
      name = row[11];
      jiebie = row[1]
      semester = row[0]
      type = row[3]
      st_type=row[17]
      course_name = row[2]
      #initial index for records
      if name==None:
        continue;
      if jiebie not in all_course:
        all_course[jiebie]={}
      if semester not in all_course[jiebie]:
        all_course[jiebie][semester]={}
      if type not in all_course[jiebie][semester]:
        all_course[jiebie][semester][type]={};
      if course_name not in all_course[jiebie][semester][type]:
        all_course[jiebie][semester][type][course_name]={}
      all_course[jiebie][semester][type][course_name][name]=row;#course name
      # try:
      if name in name_map and jiebie in r_jiebie and name in r_jiebie[jiebie]:
        if type==u"主修":
            r_jiebie[jiebie][name][0]+=get_int(row[12]);
            r_jiebie[jiebie][name][1]+=get_int(row[13]);
            r_jiebie[jiebie][name][2]+=get_int(row[14]);
            r_semester[jiebie][semester][name][0]+=get_int(row[12]);
            r_semester[jiebie][semester][name][1]+=get_int(row[13]);
            r_semester[jiebie][semester][name][2]+=get_int(row[14]);
        elif type==u"限制性课程":
            r_jiebie[jiebie][name][3]+=get_int(row[12]);
            r_jiebie[jiebie][name][4]+=get_int(row[13]);
            r_semester[jiebie][semester][name][3]+=get_int(row[12]);
            r_semester[jiebie][semester][name][4]+=get_int(row[13]);
        elif type==u"观修":
            r_jiebie[jiebie][name][5]+=get_int(row[15]);
            r_jiebie[jiebie][name][6]+=get_int(row[16]);
            r_semester[jiebie][semester][name][5]+=get_int(row[15]);
            r_semester[jiebie][semester][name][6]+=get_int(row[16]);
        elif type==u"顶礼":
            r_jiebie[jiebie][name][7]+=get_int(row[16]);
            r_semester[jiebie][semester][name][7]+=get_int(row[16]);
        else:
          pass;
      # except:
      #   continue;
    #
    try:
      import os;
      fname = self.save_file(u"南无阿弥陀佛，请您选择另存为文件名: statistic.csv",default_name=os.getcwd()+"/statistic.csv");
      self.mframe.zbc.store_into_csv(all_course,display_class,rr_jiebie,\
           r_jiebie,r_semester,fname,stat_only);

    except:
      pass;
    # print sd;
    pass;

  def output_detail_stat(self,inst=None):
    try:
      fname = self.save_file(u"南无阿弥陀佛，请您选择另存为文件名: report.csv",default_name=os.getcwd()+"/report_"+str(time.time())+".csv");
      # fname = "test.csv"
      f = open(fname,"w");
      w=csv.writer(f,lineterminator='\n');
    except:
      f.close()
      return;

    #prepare for all student
    row_all_std = self.mframe.zbc.db.get_student_min(op="max");
    all_student={}
    # all_student_sdt={}
    for row in row_all_std:
      jiebie = row[2]
      student_id = row[0]
      if jiebie not in all_student:
        all_student[jiebie] = {}
      all_student[jiebie][student_id]=row;

    #prepare for all class_require
    row_all_class = self.mframe.zbc.db.get_all_r_class();
    all_r_class = {}
    for row in row_all_class:
      jiebie = row[0]
      course_name = row[1]
      if jiebie not in all_r_class:
        all_r_class[jiebie]={}
      all_r_class[jiebie][course_name] = row;
      # type = row[2];

    #prepare for all records
    row_all_records = self.mframe.zbc.db.get_all_records();
    all_records = {};
    for row in row_all_records:
      jiebie = row[1];
      student_id = row[0]
      course_name = row[2];
      if jiebie not in all_records:
        all_records[jiebie]={}
      if course_name not in all_records[jiebie]:
        all_records[jiebie][course_name]={};
      all_records[jiebie][course_name][student_id]=row;

    #prepare for all semester
    all_semester={};#{jiebie:{semester1:[stime,etime]}}
    row_all_semester=self.mframe.zbc.db.get_semester();
    for row in row_all_semester:
      jiebie=row[0];seme=row[1];stime=row[2];etime=row[3];
      if jiebie not in all_semester:
        all_semester[jiebie]={}
      all_semester[jiebie][seme]=[stime,etime];

    #all_r_class {jiebie:{classname:[]}}
    # jiebie, student_id : statistics
    #all_student[jiebie][student_id]
    #all records:all_records[jiebie][course_name][student_id]=row
    #prepare for header
    for jiebie in all_r_class:
      #add header of jiebie
      total=[0 for i in self.st_summary];r_total={};
      teshu={};r_teshu={}
      course_zhuxiu={};r_course_zhuxiu={};
      course_xianzhi={};r_course_xianzhi={};
      course_guanxiu={};r_course_guanxiu={};
      semester_section={};r_semester_section={};

      seme_list=[];zhuxiu_list=[];xianzhi_list=[];guanxiu_list=[];

      if jiebie not in all_student:
        continue; #at least this jiebie has one student regestered

      for sid in all_student[jiebie]:
        r_teshu[sid]={} #teshu
        r_course_zhuxiu[sid]={}#zhuxiu
        r_course_xianzhi[sid]={}#xianzhi
        r_course_guanxiu[sid]={}#guanxiu
        r_semester_section[sid]={}
        r_total[sid]=[0 for i in self.st_summary]

      for semester in all_semester[jiebie]:
        seme_list.append([all_semester[jiebie][semester][1],semester,]);
        semester_section[semester]=[0 for i in self.st_semester];
        for sid in all_student[jiebie]:r_semester_section[sid][semester]=[0 for i in self.st_semester];
      #prepare for the required_data
      for course_name,row in all_r_class[jiebie].iteritems():
        type=row[2];
        stat_type=row[3]
        if row[10]==None:
          gl=0
        else:
          gl=int(row[10]);
        semester = None;
        for seme in all_semester[jiebie]:
          if int(all_semester[jiebie][seme][0])<=gl and int(all_semester[jiebie][seme][1])>=gl:
            semester = seme;
            break;
        if type==u"特殊修法":
          if stat_type==u"总数量":
            teshu[course_name]=int(row[9]);
            for sid in all_student[jiebie]:r_teshu[sid][course_name]=0;
          else:
            teshu[course_name]=[int(row[7]),int(row[9])];
            for sid in all_student[jiebie]:r_teshu[sid][course_name]=[0,0];

        elif type==u"主修":
          course_zhuxiu[course_name]=[1,1,1,semester]; #time
          zhuxiu_list.append([gl,course_name]);
          for sid in all_student[jiebie]:r_course_zhuxiu[sid][course_name]=[0,0,0,semester]; #time
          total[0] +=1; total[1]+=1; total[2]+=1;
          if semester!=None:
            semester_section[semester][0] +=1;semester_section[semester][1]+=1;semester_section[semester][2] +=1;
            for sid in all_student[jiebie]:r_semester_section[sid][semester][0] =0;r_semester_section[sid][semester][1]=0;r_semester_section[sid][semester][2] =0;
        elif type==u"限制性课程":
          course_xianzhi[course_name]=[1,1,semester]; #time
          xianzhi_list.append([gl,course_name]);
          for sid in all_student[jiebie]:r_course_xianzhi[sid][course_name]=[0,0,semester]; #time
          total[3] +=1; total[4]+=1;
          if semester!=None:
            semester_section[semester][3] +=1;semester_section[semester][4]+=1;
            for sid in all_student[jiebie]:r_semester_section[sid][semester][3] =0;r_semester_section[sid][semester][4] =0;
        elif type==u"观修":
          course_guanxiu[course_name]=[int(row[7]),int(row[9]),semester]; #time
          guanxiu_list.append([gl,course_name]);
          for sid in all_student[jiebie]:r_course_guanxiu[sid][course_name]=[0,0,semester]; #time
          total[5] +=int(row[7]); total[6]+=int(row[9]);
          if semester!=None:
            semester_section[semester][5] +=int(row[7]);semester_section[semester][6] +=int(row[9]);
            for sid in all_student[jiebie]:r_semester_section[sid][semester][5] =0;r_semester_section[sid][semester][6] =0;
      #count for statistics

      #count all statistical data per student, per row.
      #all_records[jiebie][course_name][student_id]=row
      if jiebie not in all_records:
        continue;
      for course_name in all_records[jiebie]:
        for sid in all_records[jiebie][course_name]:
          row = all_records[jiebie][course_name][sid];
          type = row[3];stat_type=row[4];gl=int(row[10]);
          if type==u"特殊修法":
            if sid not in r_teshu or course_name not in r_teshu[sid]:
              continue;
            if stat_type==u"总数量":
              r_teshu[sid][course_name] += int(row[9]);
            else:
              r_teshu[sid][course_name][0] += int(row[8]);
              r_teshu[sid][course_name][1] += int(row[9]);
          elif type==u"主修":
            if sid not in r_course_zhuxiu or course_name not in r_course_zhuxiu[sid]:
              continue;
            r_course_zhuxiu[sid][course_name][0] +=int(row[5]);
            r_course_zhuxiu[sid][course_name][1] +=int(row[6]);
            r_course_zhuxiu[sid][course_name][2] +=int(row[7]);
            seme=r_course_zhuxiu[sid][course_name][3];
            if sid in r_semester_section and seme in r_semester_section[sid]:
              r_semester_section[sid][seme][0]+=int(row[5]);
              r_semester_section[sid][seme][1]+=int(row[6]);
              r_semester_section[sid][seme][2]+=int(row[7]);
              r_total[sid][0]+=int(row[5]);
              r_total[sid][1]+=int(row[6]);
              r_total[sid][2]+=int(row[7]);
          elif type==u"限制性课程":
            if sid not in r_course_xianzhi or course_name not in r_course_xianzhi[sid]:
              continue;
            r_course_xianzhi[sid][course_name][0] +=int(row[5]);
            r_course_xianzhi[sid][course_name][1] +=int(row[6]);
            seme=r_course_xianzhi[sid][course_name][2];
            if sid in r_semester_section and seme in r_semester_section[sid]:
              r_semester_section[sid][seme][3]+=int(row[5]);r_semester_section[sid][seme][4]+=int(row[6]);
              r_total[sid][3]+=int(row[5]);r_total[sid][4]+=int(row[6]);

          elif type==u"观修":
            if sid not in r_course_guanxiu or course_name not in r_course_guanxiu[sid]:
              continue;
            r_course_guanxiu[sid][course_name][0] +=int(row[8]);
            r_course_guanxiu[sid][course_name][1] +=int(row[9]);
            seme=r_course_guanxiu[sid][course_name][2];
            if sid in r_semester_section and seme in r_semester_section[sid]:
              r_semester_section[sid][seme][5]+=int(row[8]);r_semester_section[sid][seme][6]+=int(row[9]);
              r_total[sid][5]+=int(row[8]);r_total[sid][6]+=int(row[9]);

      seme_list.sort();
      zhuxiu_list.sort();
      xianzhi_list.sort();
      guanxiu_list.sort();
      #generate and store statisticals
      title_1=[''];title_2=[u'昵称'];title_3=[];
      #generate tags;
      title_1.extend(['' for i in self.st_summary]);title_1[0]=jiebie+" total";
      title_2.extend(self.st_summary)
      # title_3.extend(['' for i in self.st_summary])
      for cn in teshu:
        title_1.extend(['']);
        title_2.extend([cn]);
        # title_3.append('');
      for xxx in seme_list:
        seme = xxx[1]
        title_1.extend(['' for i in self.st_summary]);title_1[-1]=seme;
        title_2.extend(self.st_semester);
        # title_3.append('');
      for xxx in zhuxiu_list:
        cn=xxx[1]
        title_1.extend([u'主修',cn,'']);
        title_2.extend([u'传承',u'法本',u'共修']);
        # title_3.append('');
      for xxx in xianzhi_list:
        cn = xxx[1]
        title_1.extend([u'限制性课程',cn]);
        title_2.extend([u'传承',u'法本']);
        # title_3.append('');
      for xxx in guanxiu_list:
        cn=xxx[1]
        title_1.extend([u'观修',cn]);
        title_2.extend([u'座次',u'数量']);
        # title_3.append('');
      #write title
      w.writerow([get_val_unicode(item,self.mframe.zbc.codetype) for item in title_1])
      w.writerow([get_val_unicode(item,self.mframe.zbc.codetype) for item in title_2])
      w.writerow([get_val_unicode(item,self.mframe.zbc.codetype) for item in title_3])

      wrow = [];
      for sid in r_total:
        wrow = [];
        nickname="";
        if self.mframe.zbc.dict_all_student:
          nickname = self.mframe.zbc.dict_all_student[sid][0][1];
        wrow.append(nickname); #
        wrow.append( total[0]-r_total[sid][0])
        wrow.append( total[1]-r_total[sid][1])
        wrow.append( r_total[sid][2])
        wrow.append( total[3]-r_total[sid][3])
        wrow.append( total[4]-r_total[sid][4])
        wrow.append( r_total[sid][5])
        wrow.append( r_total[sid][6])
        idx = 8;
        # title_3.extend(['' for i in self.st_summary])
        for cn in teshu:
          wrow.append( r_teshu[sid][cn]);idx+=1; # please pay attention, current only support 总数量

        seme_list.sort();
        for xxx in seme_list:
          seme = xxx[1]
          wrow.append( r_semester_section[sid][seme][0])
          wrow.append( r_semester_section[sid][seme][1])
          wrow.append( r_semester_section[sid][seme][2])
          wrow.append( r_semester_section[sid][seme][3])
          wrow.append( r_semester_section[sid][seme][4])
          wrow.append( r_semester_section[sid][seme][5])
          wrow.append( r_semester_section[sid][seme][6])
          idx += 7;
        zhuxiu_list.sort()
        for xxx in zhuxiu_list:
          cn=xxx[1];
          wrow.append( r_course_zhuxiu[sid][cn][0]);
          wrow.append( r_course_zhuxiu[sid][cn][1]);
          wrow.append( r_course_zhuxiu[sid][cn][2]);
          idx+=3;

        xianzhi_list.sort();
        for xxx in xianzhi_list:
          cn=xxx[1]
          wrow.append( r_course_xianzhi[sid][cn][0]);
          wrow.append( r_course_xianzhi[sid][cn][1]);
          idx+=2;
        guanxiu_list.sort();
        for xxx in guanxiu_list:
          cn=xxx[1];
          wrow.append( r_course_guanxiu[sid][cn][0]);
          wrow.append( r_course_guanxiu[sid][cn][1]);
          idx+=2;
        w.writerow([get_val_unicode(item,self.mframe.zbc.codetype) for item in wrow]);

    f.close()
    print "generate/out put detail stat"

  #generate gen 汇总统计
  def click_gen_stat(self,inst=None):
    all_student,all_student_sdt,all_student_s,all_student_s_sdt\
            ,all_r_class,all_r_class_stat,all_attendance,all_attendance_sdt\
            ,all_records,all_records_sdt = self.prepare_gen_stat();
    #overall statistics first:
    stat_all=[];
    t_jiebie = [x for x in all_r_class];
    stat_all.append(\
      self.get_stat_items(all_student,all_student_s,all_attendance,all_attendance_sdt,\
                     all_r_class,all_r_class_stat,all_records_sdt,\
                     fenglei=u"总汇总",stat_title=u"总汇总",jiebie_list=t_jiebie));

    #按主修统计
    if self.major_cb.IsChecked():
      mj = self.mframe.zbc.db.get_major();
      major_jiebie={} #major:jiebie list
      for row in mj:
        if row[0] not in major_jiebie:
          major_jiebie[row[0]] = [];
        if row[1] not in major_jiebie[row[0]]:
          major_jiebie[row[0]].append(row[1]);
      for major in major_jiebie:
        stat_all.append(self.get_stat_items(all_student,all_student_s,all_attendance,all_attendance_sdt,\
                     all_r_class,all_r_class_stat,all_records_sdt,\
                     fenglei=u"按主修统计",stat_title=major,jiebie_list=major_jiebie[major]));

    if self.department_cb.IsChecked():
      cj = self.mframe.zbc.db.get_department_jiebie();
      c_jiebie={} #major:jiebie list
      for row in cj:
        if row[0] not in c_jiebie:
          c_jiebie[row[0]] = [];
        if row[1] not in c_jiebie[row[0]]:
          c_jiebie[row[0]].append(row[1]);
      for c in c_jiebie:
        stat_all.append(self.get_stat_items(all_student,all_student_s,all_attendance,all_attendance_sdt,\
                     all_r_class,all_r_class_stat,all_records_sdt,\
                     fenglei=u"按大组统计",stat_title=c,jiebie_list=c_jiebie[c]));
      print "major checked"

    if self.subdpt_cb.IsChecked():
      cj = self.mframe.zbc.db.get_sub_department_jiebie();
      c_jiebie={} #major:jiebie list
      for row in cj:
        if row[0] not in c_jiebie:
          c_jiebie[row[0]] = [];
        if row[1] not in c_jiebie[row[0]]:
          c_jiebie[row[0]].append(row[1]);
      for c in c_jiebie:
        stat_all.append(self.get_stat_items(all_student,all_student_s,all_attendance,all_attendance_sdt,\
                     all_r_class,all_r_class_stat,all_records_sdt,\
                     fenglei=u"按中组统计",stat_title=c,jiebie_list=c_jiebie[c]));
      print "major checked"

    #按届别统计
    if self.jiebie_cb.IsChecked():
      cj = self.mframe.zbc.db.get_jiebie();
      c_jiebie={} #major:jiebie list
      for row in cj:
        if row[0] not in c_jiebie:
          c_jiebie[row[0]] = [row[0]];
      for c in c_jiebie:
        stat_all.append(self.get_stat_items(all_student,all_student_s,all_attendance,all_attendance_sdt,\
                     all_r_class,all_r_class_stat,all_records_sdt,\
                     fenglei=u"按届别统计",stat_title=c,jiebie_list=c_jiebie[c]));
      print "major checked"

    #class_room is small than a jiebie,we need prepare for a special all_student,and all_student_s
    if self.class_room_cb.IsChecked():
      cj = self.mframe.zbc.db.get_class_room_jiebie();
      c_jiebie={} #major:jiebie list
      for row in cj:
        if row[0] not in c_jiebie:
          c_jiebie[row[0]] = [];
        if row[1] not in c_jiebie[row[0]]:
          c_jiebie[row[0]].append(row[1]);

      for c in c_jiebie:
        #c is for the class room
        #get class's student
        if c==u"15-rxlclass5":
          print "do  some test"

        c_sdt=self.mframe.zbc.db.get_student_in_class(c);
        c_student={};
        c_student_s={};
        for row in c_sdt:
          student_id=row[0];
          if student_id in all_student_sdt:
            for jiebie in all_student_sdt[student_id]:
              if jiebie not in c_student:
                c_student[jiebie]={};
              c_student[jiebie][student_id] = all_student_sdt[student_id][jiebie]
          if student_id in all_student_s_sdt:
            for jiebie in all_student_s_sdt[student_id]:
              if jiebie not in c_student_s:
                c_student_s[jiebie]={};
              c_student_s[jiebie][student_id] = all_student_s_sdt[student_id][jiebie]

        stat_all.append(self.get_stat_items(c_student,c_student_s,all_attendance,all_attendance_sdt,\
                     all_r_class,all_r_class_stat,all_records_sdt,\
                     fenglei=u"按小组统计",stat_title=c,jiebie_list=c_jiebie[c]));
      print "major checked"

    #student is very trick; change c_student and c_student_s and make jiebie only contain the student.
    if self.student_cb.IsChecked():

      sdt_list=[];
      for sdt in all_student_sdt:
        sdt_list.append(sdt);
      sdt_list.sort();

      for sdt in sdt_list:
        for jiebie in all_student_sdt[sdt]:
          c_student={}
          c_student_s={}
          c_student[jiebie]={sdt:all_student_sdt[sdt][jiebie]}
          c_student_s[jiebie]={sdt:all_student_s_sdt[sdt][jiebie]}

          nick_name = "";
          if sdt in self.mframe.zbc.dict_all_student:
            nick_name = self.mframe.zbc.dict_all_student[sdt][0][1];

          stat_all.append(self.get_stat_items(c_student,c_student_s,all_attendance,all_attendance_sdt,\
                     all_r_class,all_r_class_stat,all_records_sdt,\
                     fenglei=nick_name,stat_title=jiebie,jiebie_list=[jiebie]));
      print "major checked"

    self.stat_final=stat_all;
    self.update_ultimateList(stat_all);
    # rows = self.mframe.zbc.db.get_attendence_of_student(jiebie=jiebie,class_room=class_room,course_name=course_name);
    # self.update_ultimateList(rows);
    pass;

  def get_stat_items(self,all_student,all_student_s,all_attendance,all_attendance_sdt,
                     all_r_class,all_r_class_stat,all_records_sdt,
                     fenglei=u"按主修分类",stat_title=None,jiebie_list=None):
    trec=[None for i in range(len(self.title_list))];
    trec[0]=fenglei;
    trec[1]=stat_title;
    #new add
    #Num_sdt is he number of student_id/jiebie pair
    Num_sdt=0;new_add=0;tuizhuan=0;wensi=0;edge=0;Num_total=0;
    Num_test=0
    for jiebie in jiebie_list:
      if jiebie not in all_student:
        continue;
      Num_test += len(all_student[jiebie]);
      for sdt in all_student[jiebie]:
        print jiebie,sdt
        if jiebie not in all_student_s:
          continue;
        Num_total += 1;
        status = all_student_s[jiebie][sdt][6];
        if status==u"新增":
          new_add += 1;
        status = all_student[jiebie][sdt][6];
        if status==u"精进闻思" or status==u"新增" or status==None:
          wensi += 1;
        elif status==u"退失边缘":
          edge += 1;
        elif status==u"退失":
          tuizhuan += 1;
    #本期应报 = wensi+edge
    #上期应报 = wensi+edge - new_add +tuizhuan
    Num_sdt = wensi + edge ; # current baoshu No.
    Num_prev = wensi + edge + tuizhuan - new_add;
    if self.mframe.type=="group":
      trec[2]=str(Num_prev);
      trec[3]=get_stat_str(Num_sdt,new_add);
      trec[4]=get_stat_str(Num_sdt,tuizhuan);
      trec[5]=str(Num_sdt);
      trec[6]=get_stat_str(Num_sdt,wensi);
      trec[9]=get_stat_str(Num_sdt,edge);
    elif self.mframe.type=="personal":
      pass
    # attendance
    # Num_sdt=0;
    attend=0;
    for jiebie in jiebie_list:
      if jiebie not in all_student:
        continue;
      for sdt in all_attendance_sdt:
        if jiebie in all_attendance_sdt[sdt]:

          if jiebie not in all_r_class:
            continue;
          cn = 0;
          if u"主修" in all_r_class_stat[jiebie]:
            tcourse = all_r_class_stat[jiebie][u"主修"];
          else:
            continue;
          for course_name in all_attendance_sdt[sdt][jiebie]:
            #is this course 主修？
            if course_name in all_r_class[jiebie]:
              type = all_r_class[jiebie][course_name][2];
            else:
              continue;
            if type!=u"主修":
              continue;
            report = all_attendance_sdt[sdt][jiebie][course_name][4];
            if report == u"圆满":
              cn += 1;
          if cn>=tcourse*0.5:
            attend+=1 #this student+jiebie > 50% attendance.
    if self.mframe.type=="group":
      trec[17]=get_stat_str(Num_sdt,attend);
      trec[18]=get_stat_str(Num_sdt,Num_sdt-attend);
    elif self.mframe.type=="personal":
      trec[9]=get_stat_str(Num_sdt,attend);
      trec[10]=get_stat_str(Num_sdt,Num_sdt-attend);
    #records
    # Num_sdt=0;
    s_zhuxiu_ym=0;s_zhuxiu_15=0;s_xianzhi=0;s_guanxiu=0;s_catch_jindu=0;s_baoshu=0;s_wensi_all=0;
    for jiebie in jiebie_list:
      if jiebie not in all_student:
        continue;
      for std in all_records_sdt:
        if jiebie in all_records_sdt[std]:
          if jiebie not in all_r_class_stat:
            continue;
          if u"主修" not in all_r_class_stat[jiebie]:
            tzhuxiu = 0;
          else:
            tzhuxiu=all_r_class_stat[jiebie][u"主修"];
          if u"限制性课程" not in all_r_class_stat[jiebie]:
            txianzhi = 0;
          else:
            txianzhi=all_r_class_stat[jiebie][u"限制性课程"];
          if u"观修" not in all_r_class_stat[jiebie]:
            tguanxiu = 0;
          else:
            tguanxiu=all_r_class_stat[jiebie][u"观修"];
          zhuxiu=0;xianzhi=0;guanxiu=0;
          zhuxiu15=0;
          for course_name in all_records_sdt[std][jiebie]:
            if course_name not in all_r_class[jiebie]:
              continue;
            row = all_records_sdt[std][jiebie][course_name];
            type = row[3];
            if type == u"主修" and row[5]>=all_r_class[jiebie][course_name][5]\
                and row[6]>=all_r_class[jiebie][course_name][6]:
              zhuxiu+=1;
            elif type == u"观修" and row[8]>=all_r_class[jiebie][course_name][8]\
                and row[9]>=all_r_class[jiebie][course_name][9]:
              guanxiu +=1;
            elif type == u"限制性课程" and row[5]>=all_r_class[jiebie][course_name][5]\
                and row[6]>=all_r_class[jiebie][course_name][6]:
              xianzhi +=1;
          if zhuxiu==tzhuxiu:
            s_zhuxiu_ym += 1;
          if zhuxiu+15 < tzhuxiu:
            s_zhuxiu_15 += 1;
          if xianzhi==txianzhi:
            s_xianzhi += 1;
          if guanxiu == tguanxiu:
            s_guanxiu += 1;
          if zhuxiu+guanxiu+xianzhi>0:
            s_baoshu += 1;
          if zhuxiu==tzhuxiu and xianzhi==txianzhi and guanxiu==tguanxiu:
            s_wensi_all += 1;
    #
    if self.mframe.type=="group":
      trec[7] = get_stat_str(Num_sdt,s_baoshu);
      trec[8] = get_stat_str(Num_sdt,Num_sdt - s_baoshu);
      trec[10] = get_stat_str(Num_sdt,s_wensi_all);
      trec[11] = get_stat_str(Num_sdt,Num_sdt - s_wensi_all);
      trec[12] = get_stat_str(Num_sdt,s_zhuxiu_ym);
      trec[13] = get_stat_str(Num_sdt,Num_sdt - s_zhuxiu_ym);
      trec[14] = get_stat_str(Num_sdt,s_zhuxiu_15);
      trec[15] = get_stat_str(Num_sdt,s_xianzhi);
      trec[16] = get_stat_str(Num_sdt,Num_sdt - s_xianzhi);
      trec[19] = get_stat_str(Num_sdt,s_guanxiu);
      trec[20] = get_stat_str(Num_sdt,Num_sdt-s_guanxiu);
    elif self.mframe.type=="personal":
      trec[2] = get_stat_str(Num_sdt,s_wensi_all);
      trec[3] = get_stat_str(Num_sdt,Num_sdt - s_wensi_all);
      trec[4] = get_stat_str(Num_sdt,s_zhuxiu_ym);
      trec[5] = get_stat_str(Num_sdt,Num_sdt - s_zhuxiu_ym);
      trec[6] = get_stat_str(Num_sdt,s_zhuxiu_15);
      trec[7] = get_stat_str(Num_sdt,s_xianzhi);
      trec[8] = get_stat_str(Num_sdt,Num_sdt - s_xianzhi);
      trec[11] = get_stat_str(Num_sdt,s_guanxiu);
      trec[12] = get_stat_str(Num_sdt,Num_sdt-s_guanxiu);

    return trec;

  def update_ultimateList(self,stat_rec):
    self.ultimateList.DeleteAllItems();
    idx = 0;

    print "delete all old items"

    for row in stat_rec:
      #0u"分类"
      self.ultimateList.InsertStringItem(idx,unicode(row[0]))
      for i in range(1,len(self.title_list)):
        self.ultimateList.SetStringItem(idx,i,unicode(row[i]));
      idx += 1;

    self.ultimateList.Refresh()
    pass;

  def output_stat(self,event=None):
    try:
      t=len(self.stat_final);
      fname = self.save_file(u"南无阿弥陀佛，请您选择另存为文件名: report.csv",default_name=os.getcwd()+"/report_"+str(time.time())+".csv");
      f = open(fname,"w");
      w=csv.writer(f,lineterminator='\n');
      #write title
      w.writerow([get_val_unicode(item,self.mframe.zbc.codetype) for item in self.title_list])
      for row in self.stat_final:
        w.writerow([get_val_unicode(item,self.mframe.zbc.codetype) for item in row]);
      f.close()
      # self.op_status.SetValue(u"南无阿弥陀佛，統計報表已经正确导出到csv文件，请您查收！")
    except:
      return;
    print "output stat"

  def save_file(self,title=u"csv file",file_type="*.csv",default_name="student_info.csv"):
    of  = wx.FileDialog(None,title,u"南无阿弥陀佛",default_name,file_type,wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT);
    if of.ShowModal() == wx.ID_CANCEL:
      print "cancel"
      # of.Destroy();
      return None;
    # of.Destroy();
    return of.GetPath();


class zbc_wensi(wx.Panel):
  def __init__(self, parent , mframe):
    self.mframe = mframe;
    wx.Panel.__init__(self, parent,size=(3000,3000))
    self.SetBackgroundColour((255,255,255));

    # self.bmpuf = mframe.bmpuf;
    # self.bmpf = mframe.bmpf;
    box_title =wx.BoxSizer(wx.HORIZONTAL);
    xpos=[0,3];self.jiebie_text = pkc_create_static_text(self,xpos,size=(213,-1), value=u"当前届别："+unicode(self.mframe.zbc.jiebie));
    self.semester_text = pkc_create_static_text(self,xpos,size=(213,-1), value=u"当前学期："+unicode(self.mframe.zbc.default_semester));
    box_title.Add(self.jiebie_text, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=2)
    box_title.Add(self.semester_text, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=2)

    font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    boldfont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    boldfont.SetWeight(wx.BOLD)
    boldfont.SetPointSize(12)

    self.ultimateList = ULC.UltimateListCtrl(self, agwStyle = wx.LC_REPORT
                                     | wx.LC_VRULES
                                     | wx.LC_HRULES
                                     |ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
                                     |ULC.ULC_NO_HIGHLIGHT)

    info = ULC.UltimateListItem()
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
    info._image = []
    info._format = wx.LIST_FORMAT_LEFT
    info._kind = 1
    info._text = u'课程'
    self.ultimateList.InsertColumnInfo(0, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT
    info._image = []
    info._text =  u'听传承'
    info._font =  font
    self.ultimateList.InsertColumnInfo(1, info)

    info = ULC.UltimateListItem()
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
    info._format = wx.LIST_FORMAT_LEFT
    info._text = u'看法本'
    info._font = font
    info._image = []
    self.ultimateList.InsertColumnInfo(2, info)

    # info = ULC.UltimateListItem()
    # info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
    # info._format = wx.LIST_FORMAT_LEFT
    # info._text = u'参加共修'
    # info._font = font
    # info._image = []
    # self.ultimateList.InsertColumnInfo(3, info)

    # info = ULC.UltimateListItem()
    # info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
    # info._format = wx.LIST_FORMAT_LEFT
    # info._text = u'修行时间(可修改)'
    # info._font = font
    # info._image = []
    # self.ultimateList.InsertColumnInfo(3, info)

    info = ULC.UltimateListItem()
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
    info._format = wx.LIST_FORMAT_LEFT
    info._text = u'撤销上一次记录'
    info._font = font
    info._image = []
    self.ultimateList.InsertColumnInfo(3, info)

    self.ultimateList.SetColumnWidth(0, 157)
    self.ultimateList.SetColumnWidth(1, 93)
    self.ultimateList.SetColumnWidth(2, 93)
    # self.ultimateList.SetColumnWidth(3, 80)
    # self.ultimateList.SetColumnWidth(3, 157)
    self.ultimateList.SetColumnWidth(3, 80)


    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(box_title,proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=1)
    sizer.Add(self.ultimateList, 1, wx.EXPAND)
    self.SetSizer(sizer)


  def update_ultimateList(self,trecords):
    idx = 0;
    i=0;
    self.jiebie_text.SetValue(self.mframe.zbc.jiebie)
    self.semester_text.SetValue(self.mframe.zbc.default_semester)
    self.ultimateList.DeleteAllItems();
    for row in trecords:
      #
      if row[3]==u'主修':

        self.ultimateList.InsertStringItem(idx, row[2])

        #current time
        ctime = time_int_str_min(time.time());
        time_but = wx.TextCtrl(self.ultimateList,value=ctime,pos=(0,0),size=(80,25),style=wx.TE_RICH);
        time_but.Hide();
        # self.ultimateList.SetItemWindow(idx, col=3, wnd=time_but, expand=True);

        chuanchen = wx.Button(self.ultimateList, wx.ID_ANY, u"已听 "+unicode(get_value(row[12])), pos=(0, 0),size=(93,30));
        if row[4]<=get_value(row[12]):
          # chuanchen = wx.BitmapButton(self.ultimateList, -1, self.bmpf, pos=(0, 0))
          chuanchen.SetBitmap(self.mframe.flower);
        else: #finished
          # chuanchen.SetBitmap(self.mframe.jiayou);
          pass;
          # chuanchen = wx.BitmapButton(self.ultimateList, -1, self.bmpuf, pos=(0, 0))

        self.ultimateList.SetItemWindow(idx, col=1, wnd=chuanchen, expand=False)
        chuanchen.Bind(wx.EVT_BUTTON, partial(self.left_click,para=[i,5,12,time_but]));

        faben = wx.Button(self.ultimateList, wx.ID_ANY, u"已看 "+unicode(get_value(row[13])), pos=(0, 0),size=(93,30));
        if row[5]<=get_value(row[13]):
          # faben = wx.BitmapButton(self.ultimateList, -1, self.bmpf, pos=(0, 0))
          faben.SetBitmap(self.mframe.flower)
          pass
        else: #finished
          # faben.SetBitmap(self.mframe.jiayou)
          pass
        #   faben = wx.BitmapButton(self.ultimateList, -1, self.bmpuf, pos=(0, 0))
        self.ultimateList.SetItemWindow(idx, col=2, wnd=faben, expand=False)
        faben.Bind(wx.EVT_BUTTON, partial(self.left_click,para=[i,6,13,time_but]));

        # gongxiu = wx.Button(self.ultimateList, wx.ID_ANY, str(get_value(row[14])), pos=(0, 0),size=(73,30));
        # if row[6]<=get_value(row[14]):
        #   gongxiu.SetBitmap(self.mframe.flower)
        # #   gongxiu = wx.BitmapButton(self.ultimateList, -1, self.bmpf, pos=(0, 0))
        # else: #finished
        #   gongxiu.SetBitmap(self.mframe.jiayou)
        # #   gongxiu = wx.BitmapButton(self.ultimateList, -1, self.bmpuf, pos=(0, 0))
        # self.ultimateList.SetItemWindow(idx, col=3, wnd=gongxiu, expand=False)
        # gongxiu.Bind(wx.EVT_BUTTON, partial(self.left_click,para=[i,7,14,time_but]));


        #undo function
        undo_records = wx.Button(self.ultimateList, wx.ID_ANY, u"撤销", pos=(0, 0),);
        self.ultimateList.SetItemWindow(idx, col=3, wnd=undo_records, expand=True)
        undo_records.Bind(wx.EVT_BUTTON, partial(self.undo_records,para=[i,chuanchen,faben,None,time_but]));

        idx +=1;
      i+=1;
    self.ultimateList.Refresh();
    pass;

  def undo_records(self,event,para):
    row = self.mframe.zbc.records[para[0]];
    v = self.mframe.zbc.db.get_latest_done_history(student_id=row[11],
                                     jiebie=row[1],
                                     course_name=row[2]);

    if v == None:
      return;

    #undo it.
    stat_type=v[0];
    chuancheng = para[1];
    faben = para[2]
    # gongxiu=para[3]
    time_but=para[4]
    if stat_type==u"传承法本":
      row[12] -=v[1];
      row[13] -=v[2];
      chuancheng.SetLabel(u'已听'+unicode(row[12]))
      faben.SetLabel(u'已看'+unicode(row[13]))
      if row[12]>=1:
        chuancheng.SetBitmap(self.mframe.flower)
      else:
        # chuancheng.SetBitmap(self.mframe.jiayou)
        pass;
      if row[13]>=1:
        faben.SetBitmap(self.mframe.flower)
      else:
        # faben.SetBitmap(self.mframe.jiayou)
        pass;
    elif stat_type==u"共修":
      row[12] -=v[1];
      row[13] -=v[2];
      row[14] -=v[3];
      chuancheng.SetLabel(u'已听'+unicode(row[12]))
      faben.SetLabel(u'已看'+unicode(row[13]))
      # gongxiu.SetLabel(str(row[14]))
      #
      if row[12]>=1:
        chuancheng.SetBitmap(self.mframe.flower)
      else:
        # chuancheng.SetBitmap(self.mframe.jiayou)
        pass;
      if row[13]>=1:
        faben.SetBitmap(self.mframe.flower)
      else:
        # faben.SetBitmap(self.mframe.jiayou)
        pass;
      # if row[14]>=1:
      #   gongxiu.SetBitmap(self.mframe.flower)
      # else:
      #   gongxiu.SetBitmap(self.mframe.jiayou)
    elif stat_type==u"次数时长":
      row[15] -=v[4];
      row[16] -=v[5];
    elif stat_type==u"总数量":
      row[16] -=v[5];

    param=[row[11],row[1],row[2],row[3],row[17],row[12],row[13],row[14],row[15],row[16],row[0]]
    self.mframe.zbc.db.replace_into("records",param);


  def left_click(self,event,para):
    cb = event.GetEventObject()
    time_but = para[3]
    #update the date
    r=self.mframe.zbc.records[para[0]];
    change_index = para[2]

    #write into the database;
    for i in range(len(r)):
      if r[i] == None:
        r[i] = 0;
    r[change_index] += 1;
    if change_index == 12:
      cb.SetLabel(u'已听'+unicode(r[change_index]));
    else:
      cb.SetLabel(u'已看'+unicode(r[change_index]));

    if r[change_index] >= r[para[1]]:
      cb.SetBitmap(self.mframe.flower); #change the img of the button

    r[11]=self.mframe.zbc.student_id;
    param = [r[11],r[1],r[2],r[3],r[17],r[12],r[13],r[14],r[15],r[16],r[0]]
    self.mframe.zbc.db.replace_into("records",param);

    paramh = [r[11],r[1],r[2],r[3],r[17],0,0,0,0,0,r[0],time.time(),0]
    paramh[int(para[1])]=1;
    self.mframe.zbc.db.replace_into("records_history",paramh);
    # cb.SetWindowStyleFlag(wx.SIMPLE_BORDER);
    print "---"


class zbc_wensi_xianzhi(wx.Panel):
  def __init__(self, parent , mframe):
    self.mframe = mframe;
    wx.Panel.__init__(self, parent,size=(3000,3000))
    self.SetBackgroundColour((255,255,255));

    # self.bmpuf = mframe.bmpuf;
    # self.bmpf = mframe.bmpf;
    #jiebie and 学期选择:
    box_title =wx.BoxSizer(wx.HORIZONTAL);
    xpos=[0,3];self.jiebie_text = pkc_create_static_text(self,xpos,size=(213,-1), value=u"当前届别："+unicode(self.mframe.zbc.jiebie));
    self.semester_text = pkc_create_static_text(self,xpos,size=(213,-1), value=u"当前学期："+unicode(self.mframe.zbc.default_semester));
    box_title.Add(self.jiebie_text, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=2)
    box_title.Add(self.semester_text, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=2)

    font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    boldfont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    boldfont.SetWeight(wx.BOLD)
    boldfont.SetPointSize(12)

    self.ultimateList = ULC.UltimateListCtrl(self, agwStyle = wx.LC_REPORT
                                     | wx.LC_VRULES
                                     | wx.LC_HRULES
                                     |ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
                                     |ULC.ULC_NO_HIGHLIGHT)

    info = ULC.UltimateListItem()
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
    info._image = []
    info._format = wx.LIST_FORMAT_LEFT
    info._kind = 1
    info._text = u'课程'
    self.ultimateList.InsertColumnInfo(0, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT
    info._image = []
    info._text =  u'听传承'
    info._font =  font
    self.ultimateList.InsertColumnInfo(1, info)

    info = ULC.UltimateListItem()
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
    info._format = wx.LIST_FORMAT_LEFT
    info._text = u'看法本'
    info._font = font
    info._image = []
    self.ultimateList.InsertColumnInfo(2, info)

    # info = ULC.UltimateListItem()
    # info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
    # info._format = wx.LIST_FORMAT_LEFT
    # info._text = u'修行时间(可修改)'
    # info._font = font
    # info._image = []
    # self.ultimateList.InsertColumnInfo(3, info)

    info = ULC.UltimateListItem()
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
    info._format = wx.LIST_FORMAT_LEFT
    info._text = u'撤销上一次记录'
    info._font = font
    info._image = []
    self.ultimateList.InsertColumnInfo(3, info)

    self.ultimateList.SetColumnWidth(0, 157)
    self.ultimateList.SetColumnWidth(1, 137)
    self.ultimateList.SetColumnWidth(2, 137)
    # self.ultimateList.SetColumnWidth(3, 157)
    self.ultimateList.SetColumnWidth(3, 137)

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(box_title,proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=1)
    sizer.Add(self.ultimateList, 1, wx.EXPAND)
    self.SetSizer(sizer)


  def update_ultimateList(self,trecords):
    idx = 0;
    i=0;
    self.jiebie_text.SetValue(self.mframe.zbc.jiebie)
    self.semester_text.SetValue(self.mframe.zbc.default_semester)
    self.ultimateList.DeleteAllItems();
    for row in trecords:
      #
      if row[3]==u"限制性课程":

        self.ultimateList.InsertStringItem(idx, row[2])

        ctime = time_int_str_min(time.time());
        time_but = wx.TextCtrl(self.ultimateList,value=ctime,pos=(0,0),size=(80,25),style=wx.TE_RICH);
        time_but.Hide();
        # self.ultimateList.SetItemWindow(idx, col=3, wnd=time_but, expand=True);

        chuanchen = wx.Button(self.ultimateList, wx.ID_ANY, u"已听 "+unicode(get_value(row[12])), pos=(0, 0),size=(137,30));
        if row[4]<=get_value(row[12]):
          # chuanchen = wx.BitmapButton(self.ultimateList, -1, self.bmpf, pos=(0, 0))
          chuanchen.SetBitmap(self.mframe.flower);
        else: #finished
          # chuanchen.SetBitmap(self.mframe.jiayou);
          pass;
          # chuanchen = wx.BitmapButton(self.ultimateList, -1, self.bmpuf, pos=(0, 0))

        self.ultimateList.SetItemWindow(idx, col=1, wnd=chuanchen, expand=False)
        chuanchen.Bind(wx.EVT_BUTTON, partial(self.left_click,para=[i,5,12,time_but]));

        faben = wx.Button(self.ultimateList, wx.ID_ANY, u"已看 "+unicode(get_value(row[13])), pos=(0, 0),size=(137,30));
        if row[5]<=get_value(row[13]):
          # faben = wx.BitmapButton(self.ultimateList, -1, self.bmpf, pos=(0, 0))
          faben.SetBitmap(self.mframe.flower)
        else: #finished
          # faben.SetBitmap(self.mframe.jiayou)
          pass
        #   faben = wx.BitmapButton(self.ultimateList, -1, self.bmpuf, pos=(0, 0))
        self.ultimateList.SetItemWindow(idx, col=2, wnd=faben, expand=False)
        faben.Bind(wx.EVT_BUTTON, partial(self.left_click,para=[i,6,13,time_but]));


        #undo function
        undo_records = wx.Button(self.ultimateList, wx.ID_ANY, u"撤销", pos=(0, 0),);
        self.ultimateList.SetItemWindow(idx, col=3, wnd=undo_records, expand=True)
        undo_records.Bind(wx.EVT_BUTTON, partial(self.undo_records,para=[i,chuanchen,faben,faben,time_but]));

        idx +=1;
      i+=1;
    self.ultimateList.Refresh();
    pass;

  def undo_records(self,event,para):
    row = self.mframe.zbc.records[para[0]];
    v = self.mframe.zbc.db.get_latest_done_history(student_id=row[11],
                                     jiebie=row[1],
                                     course_name=row[2]);

    if v == None:
      return;

    #undo it.
    stat_type=v[0];
    chuancheng = para[1];
    faben = para[2]
    gongxiu=para[3]
    time_but=para[4]
    if stat_type==u"传承法本":
      row[12] -=v[1];
      row[13] -=v[2];
      chuancheng.SetLabel(u"已听 "+unicode(row[12]))
      faben.SetLabel(u"已看 "+unicode(row[13]))
      if row[12]>=1:
        chuancheng.SetBitmap(self.mframe.flower)
      else:
        # chuancheng.SetBitmap(self.mframe.jiayou)
        pass;
      if row[13]>=1:
        faben.SetBitmap(self.mframe.flower)
      else:
        # faben.SetBitmap(self.mframe.jiayou)
        pass;
    elif stat_type==u"共修":
      pass;
    elif stat_type==u"次数时长":
      pass;
    elif stat_type==u"总数量":
      pass;

    param=[row[11],row[1],row[2],row[3],row[17],row[12],row[13],row[14],row[15],row[16],r[0]]
    self.mframe.zbc.db.replace_into("records",param);


  def left_click(self,event,para):
    cb = event.GetEventObject()
    time_but = para[3]
    #update the date
    r=self.mframe.zbc.records[para[0]];
    change_index = para[2]

    #write into the database;
    for i in range(len(r)):
      if r[i] == None:
        r[i] = 0;
    r[change_index] += 1;

    if change_index==12:
      cb.SetLabel(u"已听 "+unicode(r[change_index]));
    else:
      cb.SetLabel(u"已看 "+unicode(r[change_index]));

    if r[change_index] >= r[para[1]]:
      cb.SetBitmap(self.mframe.flower); #change the img of the button

    r[11]=self.mframe.zbc.student_id;
    param = [r[11],r[1],r[2],r[3],r[17],r[12],r[13],r[14],r[15],r[16],r[0]]
    self.mframe.zbc.db.replace_into("records",param);

    paramh = [r[11],r[1],r[2],r[3],r[17],0,0,0,0,0,r[0],time.time(),0]
    paramh[int(para[1])]=1;
    self.mframe.zbc.db.replace_into("records_history",paramh);
    # cb.SetWindowStyleFlag(wx.SIMPLE_BORDER);
    print "---"


class zbc_xiu_guanxiu(wx.Panel):
  def __init__(self, parent , mframe):
    self.mframe = mframe;
    wx.Panel.__init__(self, parent,size=(3000,3000))
    self.SetBackgroundColour((255,255,255));

    # self.bmpuf = mframe.bmpuf;
    # self.bmpf = mframe.bmpf;
    #jiebie and 学期选择:
    box_title =wx.BoxSizer(wx.HORIZONTAL);
    xpos=[0,3];self.jiebie_text = pkc_create_static_text(self,xpos,size=(213,-1), value=u"当前届别："+unicode(self.mframe.zbc.jiebie));
    self.semester_text = pkc_create_static_text(self,xpos,size=(213,-1), value=u"当前学期："+unicode(self.mframe.zbc.default_semester));
    box_title.Add(self.jiebie_text, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=2)
    box_title.Add(self.semester_text, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=2)

    font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    boldfont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    boldfont.SetWeight(wx.BOLD)
    boldfont.SetPointSize(12)

    self.ultimateList = ULC.UltimateListCtrl(self, agwStyle = wx.LC_REPORT
                                     | wx.LC_VRULES
                                     | wx.LC_HRULES
                                     |ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
                                     |ULC.ULC_NO_HIGHLIGHT)

    info = ULC.UltimateListItem()
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
    info._image = []
    info._format = wx.LIST_FORMAT_LEFT
    info._kind = 1
    info._text = u'修法名称'
    self.ultimateList.InsertColumnInfo(0, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text =  u'观修次数'
    info._font =  font
    self.ultimateList.InsertColumnInfo(1, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text =  u'观修总时间'
    info._font =  font
    self.ultimateList.InsertColumnInfo(2, info)

    info = ULC.UltimateListItem()
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._format = wx.LIST_FORMAT_LEFT
    info._text = u'本次观修时间'
    info._font = font
    info._image = []
    self.ultimateList.InsertColumnInfo(3, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text =  u'确认本次输入'
    info._font =  font
    self.ultimateList.InsertColumnInfo(4, info)

    # info = ULC.UltimateListItem()
    # info._format = wx.LIST_FORMAT_LEFT
    # info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    # info._image = []
    # info._text =  u'填入修行时间'
    # info._font =  font
    # self.ultimateList.InsertColumnInfo(5, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text = u'撤销'
    info._font = font
    self.ultimateList.InsertColumnInfo(5, info)

    self.ultimateList.SetColumnWidth(0, 157)
    self.ultimateList.SetColumnWidth(1, 80)
    self.ultimateList.SetColumnWidth(2, 80)
    self.ultimateList.SetColumnWidth(3, 80)
    self.ultimateList.SetColumnWidth(4, 75)
    # self.ultimateList.SetColumnWidth(5, 150)
    self.ultimateList.SetColumnWidth(5, 80)
    # self.ultimateList.SetBackgroundColour((100,100,100))

    sizer = wx.BoxSizer(wx.VERTICAL)
    c_sizer = wx.BoxSizer(wx.HORIZONTAL)

    sizer.Add(box_title,proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=1)
    sizer.Add(self.ultimateList, 1, wx.EXPAND)
    sizer.Add(c_sizer)
    self.SetSizer(sizer)

  def clean_ultimateList(self):
    self.ultimateList.DeleteAllItems();

  def update_ultimateList(self,trecords):
    idx=0;
    i=0;
    self.jiebie_text.SetValue(self.mframe.zbc.jiebie)
    self.semester_text.SetValue(self.mframe.zbc.default_semester)
    self.ultimateList.DeleteAllItems();
    for row in trecords:
      if row[3]==u'观修':
        self.ultimateList.InsertStringItem(idx, row[2])
        # self.ultimateList.SetStringItem(0, 1, "Go")
        # button = wx.BitmapButton(self.ultimateList, -1, self.bmpuf, pos=(10, 20))
        number = wx.TextCtrl(self.ultimateList,value=str(row[15]),pos=(0,0),size=(80,25),style=wx.TE_READONLY|wx.NO_BORDER|wx.TE_RICH);
        self.ultimateList.SetItemWindow(idx, col=1, wnd=number, expand=True);
        # button.Bind(wx.EVT_BUTTON, partial(self.left_click_1,para=[i,15]));

        dval = str(row[16]);
        total = wx.TextCtrl(self.ultimateList,value=dval,pos=(0,0),size=(80,25),style=wx.TE_READONLY|wx.NO_BORDER|wx.TE_RICH);
        self.ultimateList.SetItemWindow(idx, col=2, wnd=total, expand=True);
        # button.Bind(wx.EVT_BUTTON, partial(self.left_click_inc,para=[i,16]));

        cur_vol = wx.TextCtrl(self.ultimateList,value=str(row[8]),pos=(0,0),size=(80,25),style=wx.TE_RICH);
        self.ultimateList.SetItemWindow(idx, col=3, wnd=cur_vol, expand=True);
        # button.Bind(wx.EVT_TEXT, partial(self.left_click_vol,para=[i,17]));

        ctime = time_int_str_min(time.time());
        time_but = wx.TextCtrl(self.ultimateList,value=ctime,pos=(0,0),size=(80,25),style=wx.TE_RICH);
        time_but.Hide();
        # self.ultimateList.SetItemWindow(idx, col=5, wnd=time_but, expand=True);


        if row[17]==u'次数时长':
          button=wx.Button(self.ultimateList, wx.ID_ANY, str(get_value(row[15])), pos=(0, 0),size=(73,30));
        elif row[17]==u'总数量':
          button=wx.Button(self.ultimateList, wx.ID_ANY, str(get_value(row[16])), pos=(0, 0),size=(73,30));
        if (row[17]==u'次数时长' and row[7]<=row[15]) or \
           (row[17]==u'总数量' and row[9]<=row[16]):
          button.SetBitmap(self.mframe.flower)
        else:
          # button.SetBitmap(self.mframe.jiayou)
          pass;
        self.ultimateList.SetItemWindow(idx, col=4, wnd=button, expand=False);
                                                                    #0  1  2  3  4      5     6     7
        button.Bind(wx.EVT_BUTTON, partial(self.left_click_add,para=[i,cur_vol,number,total,time_but]));


        undo = wx.Button(self.ultimateList, wx.ID_ANY, u"撤销", pos=(0, 0),);
        # undo.SetBitmap(self.mframe.jiayou)
        self.ultimateList.SetItemWindow(idx, col=5, wnd=undo, expand=True);
        undo.Bind(wx.EVT_BUTTON, partial(self.undo_records,para=[i,cur_vol,number,total,button]));
        # self.ultimateList.SetStringItem(0, 2, "Rock")
        idx +=1;
      i+=1;

    self.ultimateList.Refresh();
	


  def undo_records(self,event,para):
    row = self.mframe.zbc.records[para[0]];
    v = self.mframe.zbc.db.get_latest_done_history(student_id=row[11],
                                     jiebie=row[1],
                                     course_name=row[2]);

    if v == None:
      return;

    #undo it.
    stat_type=v[0];
    cur_vol=para[1]
    number = para[2];
    total = para[3]
    button=para[4]
    if stat_type==u"传承法本":
      pass;
    elif stat_type==u"共修":
      pass;

    elif stat_type==u"次数时长":
      row[15] -=v[4];
      row[16] -=v[5];
      number.SetValue(str(row[15]))
      total.SetValue(str(row[16]))

      button.SetLabel(str(row[15]))
      if row[15]>=row[7]:
        button.SetBitmap(self.mframe.flower);
      else:
        # button.SetBitmap(self.mframe.jiayou);
        pass;

    elif stat_type==u"总数量":
      row[16] -=v[5];
      total.SetValue(str(row[16]));

      button.SetLabel(str(row[16]))
      if row[16]>=row[9]:
        button.SetBitmap(self.mframe.flower);
      else:
        # button.SetBitmap(self.mframe.jiayou);
        pass;

    param=[row[11],row[1],row[2],row[3],row[17],row[12],row[13],row[14],row[15],row[16],row[0]]

    self.mframe.zbc.db.replace_into("records",param);

  def left_click_add(self,event,para):
    cb = event.GetEventObject()
    r = self.mframe.zbc.records[para[0]];
    type = r[3];
    stat_type = r[17];
    cur_vol = para[1];
    number = para[2];
    total = para[3];
    time_but = para[4]
    require_number = r[7];
    require_duration = r[8];
    cur_number = 1;
    real_duration = int(cur_vol.GetValue());

    for i in range(len(r)):
      if r[i] == None:
        r[i] = 0;

    flag = True;
    if stat_type == u'总数量':
      r[16] += real_duration;
      total.SetValue(str(r[16]));
      cb.SetLabel(str(r[16]))
      if r[9]<=r[16]:
        cb.SetBitmap(self.mframe.flower);
    else:
      if require_duration <= real_duration:
        r[15] += 1;
        r[16] += real_duration;
        number.SetValue(str(r[15]));
        total.SetValue(str(r[16]));

        cb.SetLabel(str(r[15]))
        if r[7] <= r[15]:
          cb.SetBitmap(self.mframe.flower);
      else:
        flag = False;

    if flag==True:
      r[11] = self.mframe.zbc.student_id
      param = [r[11],r[1],r[2],r[3],r[17],r[12],r[13],r[14],r[15],r[16],r[0]]
      self.mframe.zbc.db.replace_into("records",param);

      paramh = [r[11],r[1],r[2],r[3],r[17],0,0,0,1,cur_vol.GetValue(),r[0],time.time(),0]
      self.mframe.zbc.db.replace_into("records_history",paramh);

    print para;


class zbc_xiu_teshu(wx.Panel):
  def __init__(self, parent , mframe,ttype=u"特殊修法"):
    self.mframe = mframe;
    self.ttype = ttype;
    wx.Panel.__init__(self, parent,size=(3000,3000))
    self.SetBackgroundColour((255,255,255));

    # self.bmpuf = mframe.bmpuf;
    # self.bmpf = mframe.bmpf;

    #jiebie and 学期选择:
    box_title =wx.BoxSizer(wx.HORIZONTAL);
    xpos=[0,3];self.jiebie_text = pkc_create_static_text(self,xpos,size=(213,-1), value=u"当前届别："+unicode(self.mframe.zbc.jiebie));
    self.semester_text = pkc_create_static_text(self,xpos,size=(213,-1), value=u"当前学期："+unicode(self.mframe.zbc.default_semester));
    box_title.Add(self.jiebie_text, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=2)
    box_title.Add(self.semester_text, proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=2)

    font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    boldfont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    boldfont.SetWeight(wx.BOLD)
    boldfont.SetPointSize(12)

    self.ultimateList = ULC.UltimateListCtrl(self, agwStyle = wx.LC_REPORT
                                     | wx.LC_VRULES
                                     | wx.LC_HRULES
                                     |ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
                                     |ULC.ULC_NO_HIGHLIGHT)

    info = ULC.UltimateListItem()
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
    info._image = []
    info._format = wx.LIST_FORMAT_LEFT
    info._kind = 1
    info._text = u'实修描述'
    self.ultimateList.InsertColumnInfo(0, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text =  u'累计修行座次'
    info._font =  font
    self.ultimateList.InsertColumnInfo(1, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text =  u'累计修行数量'
    info._font =  font
    self.ultimateList.InsertColumnInfo(2, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text =  u'本学期累计座次'
    info._font =  font
    self.ultimateList.InsertColumnInfo(3, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text =  u'本学期累计数量'
    info._font =  font
    self.ultimateList.InsertColumnInfo(4, info)

    info = ULC.UltimateListItem()
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._format = wx.LIST_FORMAT_LEFT
    info._text = u'本次修量'
    info._font = font
    info._image = []
    self.ultimateList.InsertColumnInfo(5, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text =  u'确认本次输入'
    info._font =  font
    self.ultimateList.InsertColumnInfo(6, info)

    # info = ULC.UltimateListItem()
    # info._format = wx.LIST_FORMAT_LEFT
    # info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    # info._image = []
    # info._text =  u'填入修行时间'
    # info._font =  font
    # self.ultimateList.InsertColumnInfo(5, info)

    info = ULC.UltimateListItem()
    info._format = wx.LIST_FORMAT_LEFT
    info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
    info._image = []
    info._text = u'撤销'
    info._font = font
    self.ultimateList.InsertColumnInfo(7, info)

    self.ultimateList.SetColumnWidth(0, 137)
    # self.ultimateList.SetColumnWidth(1, 80)
    self.ultimateList.SetColumnWidth(1, 108)
    self.ultimateList.SetColumnWidth(2, 108)
    self.ultimateList.SetColumnWidth(3, 108)
    self.ultimateList.SetColumnWidth(4, 87)
    self.ultimateList.SetColumnWidth(5, 87)
    self.ultimateList.SetColumnWidth(6, 117)
    self.ultimateList.SetColumnWidth(7, 87)
    # self.ultimateList.SetBackgroundColour((100,100,100))

    #
    # ult = wx.BoxSizer(wx.HORIZONTAL)
    # ult.Add(self.ultimateList, 1, wx.EXPAND)

    box = wx.BoxSizer(wx.VERTICAL)
    box.Add(box_title,proportion=0, flag= wx.ALL|wx.LEFT|wx.TOP, border=1)
    box.Add(self.ultimateList, 1, wx.EXPAND)
    self.SetSizer(box)
    box.Fit(self);

  def clean_ultimateList(self):
    self.ultimateList.DeleteAllItems();

  def update_ultimateList(self,trecords=None):
    idx=0;
    i=0;
    self.jiebie_text.SetValue(self.mframe.zbc.jiebie)
    self.semester_text.SetValue(self.mframe.zbc.default_semester)
    self.ultimateList.DeleteAllItems();
    stime = self.mframe.zbc.stime;
    etime = self.mframe.zbc.etime;
    #get all records for this teshu xiu.
    cr = self.mframe.zbc.db.get_courses_required(
      jiebie = self.mframe.zbc.jiebie,
      type = self.ttype,
      # stime = self.mframe.zbc.stime,
      # etime = self.mframe.zbc.etime,
    );
    cr_dict={}
    for row in cr:
      if row[0] not in cr_dict:
        # all zuoci,all times,semester zuoci,semester times,cr_row
        cr_dict[row[0]]=[0,0,0,0,row];

    #get all trecords
    trecords = self.mframe.zbc.db.get_sole_records(
      jiebie = self.mframe.zbc.jiebie,
      student_id = self.mframe.zbc.student_id,
      type = self.ttype,
    )

    for row in trecords:
      rtime = row[10]
      jiebie = row[1]
      course_name=row[2]
      type = row[3]
      if course_name not in cr_dict:
        continue;
      cr_dict[course_name][0] += get_int(row[8]);
      cr_dict[course_name][1] += get_int(row[9]);
      if rtime>=stime and rtime<=etime: #this time range(semester)
        cr_dict[course_name][2] += get_int(row[8]);
        cr_dict[course_name][3] += get_int(row[9]);

    for row in cr:
      course_name = row[0];
      if course_name not in cr_dict:
        continue;
      t = cr_dict[course_name];
      stat_type = t[4][2]
      if True:
        self.ultimateList.InsertStringItem(idx, course_name)

        #累计总座次
        dval = t[0];
        total_zuoci = wx.TextCtrl(self.ultimateList,value=str(dval),pos=(0,0),size=(80,25),style=wx.TE_READONLY|wx.NO_BORDER|wx.TE_RICH);
        self.ultimateList.SetItemWindow(idx, col=1, wnd=total_zuoci, expand=True);

        #累计修行数量
        dval = t[1]
        total_vol = wx.TextCtrl(self.ultimateList,value=str(dval),pos=(0,0),size=(80,25),style=wx.TE_READONLY|wx.NO_BORDER|wx.TE_RICH);
        self.ultimateList.SetItemWindow(idx, col=2, wnd=total_vol, expand=True);

        #本学期累计座次
        dval= t[2]
        seme_zuoci = wx.TextCtrl(self.ultimateList,value=str(dval),pos=(0,0),size=(80,25),style=wx.TE_READONLY|wx.NO_BORDER|wx.TE_RICH);
        self.ultimateList.SetItemWindow(idx, col=3, wnd=seme_zuoci, expand=True);

        #本学期累计数量
        dval = t[3]
        seme_vol = wx.TextCtrl(self.ultimateList,value=str(dval),pos=(0,0),size=(80,25),style=wx.TE_READONLY|wx.NO_BORDER|wx.TE_RICH);
        self.ultimateList.SetItemWindow(idx, col=4, wnd=seme_vol, expand=True);

        #本次修量
        self.cur_vol = wx.TextCtrl(self.ultimateList,value=str(30),pos=(0,0),size=(80,25),style=wx.TE_RICH);
        self.ultimateList.SetItemWindow(idx, col=5, wnd=self.cur_vol, expand=True);

        #确认本次修量
        button=wx.Button(self.ultimateList, wx.ID_ANY, u"记录本次修量", pos=(0, 0),size=(108,30));
        if stat_type==u'次数时长':
          button=wx.Button(self.ultimateList, wx.ID_ANY, u"记录一座修量", pos=(0, 0),size=(108,30));
        elif stat_type==u'总数量':
          pass;
        self.ultimateList.SetItemWindow(idx, col=6, wnd=button, expand=False);
        button.Bind(wx.EVT_BUTTON, partial(self.left_click_add,para=[course_name,cr_dict[course_name][4],self.cur_vol,
                                                                     total_zuoci,total_vol,seme_zuoci,seme_vol]));

        #撤销
        undo = wx.Button(self.ultimateList, wx.ID_ANY, u"撤销", pos=(0, 0),);
        # undo.SetBitmap(self.mframe.jiayou)
        self.ultimateList.SetItemWindow(idx, col=7, wnd=undo, expand=True);
        undo.Bind(wx.EVT_BUTTON, partial(self.undo_records,para=[course_name,cr_dict[course_name][4],self.cur_vol,
                                                                     total_zuoci,total_vol,seme_zuoci,seme_vol]));
        # self.ultimateList.SetStringItem(0, 2, "Rock")
        idx +=1;
      i+=1;

    if self.ttype==u"个人实修":
      #add a row for insert a new teshu meditation
      self.ultimateList.InsertStringItem(idx, "")
      add_xf = wx.TextCtrl(self.ultimateList,value=u"",pos=(0,0),size=(80,25),style=wx.BORDER|wx.TE_RICH);
      self.ultimateList.SetItemWindow(idx, col=0, wnd=add_xf, expand=True);

      # cjiebie = self.mframe.zbc.jiebie;
      # seme_list = [];
      # if cjiebie in self.mframe.zbc.jiebie_semester:
      #   for seme in self.mframe.zbc.jiebie_semester[cjiebie]:
      #     seme_list.append(seme[0]);
      # seme_list.sort();
      # fseme = wx.Choice(self.ultimateList,wx.ID_ANY,choices=seme_list,size=(150,-1),)
      # fseme.SetStringSelection(self.mframe.zbc.default_semester);
      # self.ultimateList.SetItemWindow(idx, col=1, wnd=fseme, expand=True);

      add_method = wx.Choice(self.ultimateList,wx.ID_ANY,choices=[u"只统计数量",u"按座次统计"],size=(150,-1),)
      add_method.SetStringSelection(u"只统计数量");
      self.ultimateList.SetItemWindow(idx, col=1, wnd=add_method, expand=True);

      btn_new = wx.Button(self.ultimateList, wx.ID_ANY, u"增加特殊修法", pos=(0, 0),);
      self.ultimateList.SetItemWindow(idx, col=2, wnd=btn_new, expand=True);
      btn_new.Bind(wx.EVT_BUTTON, partial(self.add_teshu_records,para=[add_xf,add_method]));

      # btn_del = wx.Button(self.ultimateList, wx.ID_ANY, u"删除特殊修法", pos=(0, 0),);
      # self.ultimateList.SetItemWindow(idx, col=4, wnd=btn_del, expand=True);
      # btn_del.Bind(wx.EVT_BUTTON, partial(self.del_teshu_records,para=[add_xf,add_method,fseme]));

    self.ultimateList.Refresh();

  #student_id,jiebie,course_name
  def undo_records(self,event=None,para=None):
    student_id=self.mframe.zbc.student_id;
    jiebie=self.mframe.zbc.jiebie;
    course_name=para[0];
    r = para[1] #cr
    stat_type = r[2];

    total_zuoci=para[3]
    total_vol = para[4]
    seme_zuoci = para[5]
    seme_vol = para[6]

    v = self.mframe.zbc.db.get_sole_records(
      jiebie = self.mframe.zbc.jiebie,
      student_id = self.mframe.zbc.student_id,
      course_name=para[0],
      con = " limit 1"
    )

    if len(v) <= 0:
      return;

    total_vol.SetValue(sum_val_str(total_vol.GetValue(),-v[0][9]));
    seme_vol.SetValue( sum_val_str(seme_vol.GetValue(),-v[0][9]))
    if stat_type == u"总数量":
      pass;
    elif stat_type == u"次数时长":
      total_zuoci.SetValue( sum_val_str(total_zuoci.GetValue(),-1))
      seme_zuoci.SetValue( sum_val_str(seme_zuoci.GetValue(),-1))


    #undo it.
    self.mframe.zbc.db.remove_records(
        student_id=student_id,jiebie=jiebie,course_name=course_name,
        ftime = v[0][10],
      )

  #course
  #  [course_name,cr_dict[course_name],self.cur_vol,total_zuoci,total_vol,seme_zuoci,seme_vol]));
  def left_click_add(self,event,para):
    cb = event.GetEventObject()
    course_name = para[0];
    r = para[1] #cr
    stat_type = r[2];

    cur_vol = para[2];
    total_zuoci=para[3]
    total_vol = para[4]
    seme_zuoci = para[5]
    seme_vol = para[6]

    cur_value=cur_vol.GetValue()
    if total_vol.GetValue()!='None':
      total_vol.SetValue(sum_val_str(total_vol.GetValue(),cur_value));
    else:
      total_vol.SetValue(str(cur_value));
    if seme_vol.GetValue()!='None':
      seme_vol.SetValue(sum_val_str(seme_vol.GetValue(),cur_value))
    else:
      seme_vol.SetValue(str(cur_value));
    number = None;
    if stat_type == u'次数时长':
      number = 1;
      if total_zuoci.GetValue!='None':
        total_zuoci.SetValue(sum_val_str(total_zuoci.GetValue(),1));
      else:
        total_zuoci.SetValue(str(1));
      if total_zuoci.GetValue!='None':
        seme_zuoci.SetValue(sum_val_str(seme_zuoci.GetValue(),1));
      else:
        seme_zuoci.SetValue(str(1));
    elif stat_type == u"总数量":
      number = None;

    param = [self.mframe.zbc.student_id,
             self.mframe.zbc.jiebie,
             course_name,
             r[1], #type
             stat_type,
             0,0,0,
             number,
             cur_value,
             time.time()]
    self.mframe.zbc.db.replace_into("records",param);

    # print para;

  def add_teshu_records(self,event,para):
    if len(para)<=1:
      return;
    xfname=para[0].GetValue();
    xfmethod=para[1].GetSelection();
    # xseme=para[2].GetStringSelection();
    etime = self.mframe.zbc.stime;
    # for x in self.mframe.zbc.jiebie_semester[self.mframe.zbc.jiebie]:
    #   if x[0] == xseme:
    #     etime = x[2]
    #     break;

    number=0;
    duration = 30
    total_duration=10000

    if xfmethod == 0:
      method = u"总数量";
    else:
      method = u"次数时长";
      number = 1;
    param=[
      self.mframe.zbc.jiebie,
      xfname,
      self.ttype, #u"特殊修法"
      method,
      0,
      0,
      0,
      number,
      duration,
      total_duration,
      etime
    ]
    self.mframe.zbc.db.replace_into("class_require",param);
    self.mframe.refresh_tables();
    return;

import StringIO
def get_wx_img_string(str):
  sbuf = StringIO.StringIO(str.decode('base64'))
  return wx.ImageFromStream(sbuf)

class wensixiu_tools(wx.Frame):
  def __init__(self,type="group",db_name=None,sq=None):
    """Constructor"""
    style =wx.DEFAULT_FRAME_STYLE;
    # style = wx.CLIP_CHILDREN | wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR |  wx.NO_BORDER | wx.FRAME_SHAPED;

    self.type = type;
    self.sq = sq;

    wx.Frame.__init__(self, parent=None, title=u"南无阿弥陀佛",size=(900,670),style=style)

    flower_str='''
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
'''
    icon_str='''
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
'''
    # swicon = wx.Icon('data/icon.png', wx.BITMAP_TYPE_PNG, 16, 16)
    swicon = wx.EmptyIcon()
    # swicon.CopyFromBitmap(wx.Image("data/icon.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
    swicon.CopyFromBitmap(get_wx_img_string(icon_str).ConvertToBitmap());
    wx.Frame.SetIcon(self, swicon)

    #upload resources
    ctime = time.time();
    # self.flower = wx.Image("data/flower.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
    # self.jiayou = wx.Image("data/jiayou.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
    self.flower = get_wx_img_string(flower_str).ConvertToBitmap();

    #load database and initial zbclass
    self.zbc = zbclass(db_name);

    #upload panels.
    self.nb = wx.Notebook(self)

    #
    self.page_wens = zbc_wensi(self.nb,self);
    self.nb.AddPage(self.page_wens, u"闻思")
    #
    self.page_wens_xianzhi = zbc_wensi_xianzhi(self.nb,self);
    self.nb.AddPage(self.page_wens_xianzhi, u"限制性课程")

    #ttype=u"特殊修法"
    self.page_xiu_teshu = zbc_xiu_teshu(self.nb,self);
    self.nb.AddPage(self.page_xiu_teshu, u"实修")

    #ttype=u"个人实修"
    self.page_xiu_personal = zbc_xiu_teshu(self.nb,self,ttype=u"个人实修");
    self.nb.AddPage(self.page_xiu_personal, u"个人实修")

    #
    self.page_xiu = zbc_xiu_guanxiu(self.nb,self);
    self.nb.AddPage(self.page_xiu, u"观修")

    if self.type=="group":
      #kao qing
      self.page_attendance = zbc_attendance(self.nb,self);
      self.nb.AddPage(self.page_attendance, u"考勤记录")

    self.page_attendance_statistic = zbc_attendance_statistic(self.nb,self);
    self.nb.AddPage(self.page_attendance_statistic, u"学修汇总")

    self.page_summary = zbc_summary(self.nb,self);
    self.nb.AddPage(self.page_summary, u"基本信息")

    self.refresh_tables();

    print "--prepare add all pages takes",time.time()-ctime;ctime=time.time();

  def refresh_tables(self):
    # self.mframe.page_wens
    #

    trecords = self.zbc.get_current_records(jiebie=self.zbc.jiebie,student_id=self.zbc.student_id,stime=self.zbc.stime,etime=self.zbc.etime);
    self.page_wens.update_ultimateList(trecords);
    self.page_wens_xianzhi.update_ultimateList(trecords);
    self.page_xiu.update_ultimateList(trecords); #page_xiu_personal
    self.page_xiu_personal.update_ultimateList(trecords);
    self.page_xiu_teshu.update_ultimateList(trecords);
    if self.type=="group":
      self.page_attendance.update_page();
    pass;


import sys;
if __name__ == "__main__":

  ctime = time.time();
  ttime = time.time()

  app = wx.App(False)
  print "prepare app pages takes",time.time()-ctime;ctime=time.time();

  type = "group";
  # type = "personal"
  # if len(sys.argv)==2:
  #   type = sys.argv[1];

  st_list = Queue.Queue();

  frame = wensixiu_tools(type=type,db_name="wensixiu.db",sq=st_list);
  print "prepare frame pages takes",time.time()-ctime;ctime=time.time();
  frame.Show();
  print "prepare frame show takes",time.time()-ctime;ctime=time.time();
  print "all takes",time.time()-ttime;ctime=time.time();

  #this th_hook have to put outside of the app's frame.

  app.MainLoop()
  print u"南无阿弥陀佛";