# -*- coding:utf-8 -*-
import urllib2
import re
import threading
import time,random
import xlsxwriter
import sys,os
import logging
import traceback
from Tkinter import *



flag = True


file_path=os.path.abspath(sys.argv[0])  
path_list=file_path.split('\\')
path_list.pop()
path='\\'.join(path_list)

log_path=path+'\\'
result_path=path+'\\'

log_path=unicode(log_path,"gb2312")
result_path=unicode(result_path,"gb2312")

current_date=time.strftime('%Y-%m-%d', time.localtime(time.time()))   

def createlogger(name): 
    """Create a logger named specified name with the level set in config file.
    """   
    logger = logging.getLogger(name)
    logger.setLevel("DEBUG")
    fh = logging.FileHandler(log_path+"\\get_app.log")
    #ch = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d: [%(levelname)s] [%(name)s] [%(funcName)s] %(message)s',
        '%y%m%d %H:%M:%S')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

def log_traceback(traceback):
    """print traceback information with the log style.
     
    """
    str_list = traceback.split("\n")
    for string in str_list:
        logger.warning(string)
        
    
logger = createlogger("myapp") 

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = { 'User-Agent' : user_agent }


class Get_App(threading.Thread):
 
    def __init__(self,log_name,app,web_type,base_date,config_path):
        threading.Thread.__init__(self)
        self.logger = createlogger(log_name)
        self.app=app
        self.web_type=web_type
        self.base_time=time.mktime(time.strptime(base_date,'%Y-%m-%d'))
        self.config_path=config_path
        
        self.package_list=[]
        self.app_name_list=[]
        self.app_version_list=[]
        self.update_time_list=[]
        self.old_version_list=[]


    @staticmethod
    def set_flag(f):
        global flag
        if f == "False":
            flag = False
        else:
            flag = True
            print 'set flag True'

    def set_pattern(self):
        print self.web_type
        if self.web_type==u'应用宝':
            self.base_url='http://sj.qq.com/myapp/detail.htm?apkName='
            self.title_pattern=re.compile(r'<div class="det-name-int">(.*?)</div>')
            self.version_pattern=re.compile('<div class="det-othinfo-data">(.*?)</div>')
            self.date_pattern=re.compile('data-apkPublishTime="(.*?)"></div>')
    
        elif self.web_type==u'应用市场':
            self.title_pattern=re.compile(r'<div class="det-name-int">(.*?)</div>')
            self.version_pattern=re.compile('<div class="det-othinfo-data">(.*?)</div>')
            self.date_pattern=re.compile('data-apkPublishTime="(.*?)"></div>')
        else:
            self.logger.debug(u'未定义的网站类型')
            self.app.text_msglist.insert(END, u'未定义的网站类型\n', 'blue')
            return False
        self.logger.info(u'测试网站类型:'+self.web_type)
        self.app.text_msglist.insert(END, u'测试网站类型:'+self.web_type+'\n\n', 'red')
        return True
    
    def getPage(self,url):
        try:
            #构建请求的request
            request = urllib2.Request(url,headers=headers)
            #利用urlopen获取页面代码
            response = urllib2.urlopen(request)
            #将页面转化为UTF-8编码
            pageCode = response.read()
            return pageCode
        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                self.logger.debug(u"连接%s失败，错误原因:%s"%(self.web_type,e.reason))
                self.app.text_msglist.insert(END, u"连接%s失败,错误原因:%s\n"%(self.web_type,e.reason), 'red')
                return None
          
    def getPageItems(self,url):
        pageCode = self.getPage(url)
        if not pageCode:
            self.logger.debug(u'页面加载失败....')
            self.app.text_msglist.insert(END, u'页面加载失败....\n', 'red')
            return None
        
        title=re.findall(self.title_pattern,pageCode)
        t=title[0]
        app_name=unicode(t,'utf-8')
        self.app_name_list.append(app_name)
        self.logger.info(u'app_name:'+app_name)
        self.app.text_msglist.insert(END, u'app_name:'+app_name+'\n', 'blue')
        
        version = re.findall(self.version_pattern,pageCode)
        ver=version[0]
        ver=ver[1:]
        self.app_version_list.append(ver)
        self.logger.info(u'app_version:'+ver)
        self.app.text_msglist.insert(END, u'app_version:'+ver+'\n', 'blue')
        
        update_date=re.findall(self.date_pattern,pageCode)
        time_suffix=float(update_date[0])
        update_time=time.strftime("%Y-%m-%d", time.localtime(time_suffix))
        self.update_time_list.append(update_time)
        self.logger.info(u'update_time:'+update_time)
        self.app.text_msglist.insert(END, u'update_time:'+update_time+'\n\n', 'blue')
        self.app.text_msglist.see(END)
          
    
    def write_xlsx(self):
        w=xlsxwriter.Workbook(result_path+self.web_type+current_date+'.xlsx')
        ws=w.add_worksheet('data')
        format1 = w.add_format()
        format1.set_font_color('red')
        ws.set_column('A:A',12)
        ws.set_column('B:B',30)
        ws.set_column('C:C',19)
        ws.set_column('D:D',10)
        ws.write_column('A1',self.app_name_list)
        ws.write_column('B1',self.package_list)
        ws.write_column('C1',self.app_version_list)
    
        for i in range(len(self.update_time_list)):
            if self.update_time_list[i]=='1970-01-01':
                update_date=0
            else:
                update_date=time.mktime(time.strptime(self.update_time_list[i],'%Y-%m-%d'))
            
            if update_date>=self.base_time:
                ws.write_string(i,3,self.update_time_list[i],format1)
                ws.write_string(i,0,self.app_name_list[i],format1)
            else:
                ws.write_string(i,3,self.update_time_list[i])
        
        w.close() 

    def get_package_name(self):
        
        f=open(self.config_path,'r')
        s=f.readlines()
        for t in s:
            app_info=t.split(',')
            package_name=app_info[0]
            old_version=app_info[1].strip()
            self.package_list.append(package_name)
            self.old_version_list.append(old_version)
        f.close()
        
    def run(self):
        global flag
        if not self.set_pattern():return 0
        try:
            self.get_package_name()
            for package_name in self.package_list:
                url =self.base_url+package_name
                self.logger.info(u'url: '+url)
                self.app.text_msglist.insert(END, u'url: '+url+'\n', 'blue')
                if flag:
                    self.getPageItems(url)
                    sleep_time=random.uniform(0,2)
                    time.sleep(sleep_time)
                else:
                    break
            self.write_xlsx()
        except Exception,e:
            log_traceback(traceback.format_exc())
            self.app.text_msglist.insert(END, traceback.format_exc(), 'red')
            
        flag=False
        self.logger.debug(u'测试完成....')
        self.app.text_msglist.insert(END, u'测试完成....\n', 'green')
        self.app.b1.config(state=NORMAL)
        self.app.b2.config(state=DISABLED)
        

    
    
 
    

        









    
