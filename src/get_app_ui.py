#coding=utf-8
from Tkinter import *
import tkMessageBox
import os
import tkFileDialog
from ttk import Combobox
import get_app


def get_path(ico):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    base_path=unicode(base_path,"gb2312")
    return os.path.join(base_path, ico)


class Application(Frame):

        def __init__(self,master):
            Frame.__init__(self,master)
            self.root = master
            self.root.title('get_app_version (v1.0.0,qing.guo)')
            self.root.geometry('700x410')
            self.root.resizable(0, 0)  # 禁止调整窗口大小
            self.root.protocol("WM_DELETE_WINDOW",self.close)
            self.root.iconbitmap(get_path('get_app.ico'))

        def creatWidgets(self):
            frame_left = Frame(self.root, width=380, height=410, bg='#C1CDCD')
            frame_right = Frame(self.root, width=320, height=410, bg='#C1CDCD')

            frame_left.grid_propagate(0)
            frame_right.propagate(0)
            frame_right.grid_propagate(0)

            frame_left.grid(row=0, column=0)
            frame_right.grid(row=0, column=1)

            self.v1 = StringVar()
            self.v2 = StringVar()
            self.v3 = StringVar()
            self.v4 = StringVar()
            self.v5 = StringVar()
            self.v4.set(get_app.result_path)
            
            web_list=[u'应用宝',u'...',u'...']
            
            Label(frame_left, text=u"选择网站类型:",bg='#C1CDCD').grid(row=0, column=0, pady=20, padx=5)
            self.cb1 = Combobox(frame_left, width=30, textvariable=self.v1,values=web_list)
            self.cb1.grid(row=0, column=1, ipady=1, padx=5, sticky=W)
            self.cb1.current(0)
        
            Label(frame_left, text=u"设置基准日期 :", bg='#C1CDCD').grid(row=1, column=0, pady=30, padx=5)
            Entry(frame_left, width=33, textvariable=self.v2).grid(row=1,column=1, padx=2,pady=30,ipady=2,sticky=W)

            Button(frame_left, text=u"选择配置文件 :",command=self.open_file1, bg='#C1CDCD').grid(row=2, column=0, pady=30, padx=5)
            Entry(frame_left, width=33, textvariable=self.v3).grid(row=2,column=1, padx=2,pady=30,ipady=2,sticky=W)
            
            self.b1=Button(frame_left, text=u"开始获取",command=self.start_test, bg='#C1CDCD')
            self.b1.grid(row=3,column=0,padx=25,pady=30)
                
            self.b2=Button(frame_left, text=u"停止获取",command=self.end_test, bg='#C1CDCD')
            self.b2.grid(row=3,column=1,padx=25,pady=30)
                
            Button(frame_left, text=u"查看结果", command=self.open_file2,bg='#C1CDCD').grid(row=4, column=0, padx=3, pady=15)
            Entry(frame_left, width=34, textvariable=self.v4).grid(row=4, column=1, ipady=1, padx=3, pady=15)
            
            self.v2.set(get_app.current_date)
            
            #Scrollbar
            scrollbar = Scrollbar(frame_right,bg='#C1CDCD')
            scrollbar.pack(side=RIGHT, fill=Y)
            self.text_msglist = Text(frame_right, yscrollcommand=scrollbar.set,bg='#C1CDCD')
            self.text_msglist.pack(side=RIGHT, fill=BOTH)
            scrollbar['command'] = self.text_msglist.yview
            self.text_msglist.tag_config('green', foreground='#008B00')
            self.text_msglist.tag_config('blue', foreground='#0000FF')
            self.text_msglist.tag_config('red', foreground='#FF3030')
            self.text_msglist.tag_config('purple', foreground='#CD00CD')
            text_message1 = u"1.选择数据APK来源网站，目前支持应用宝\n"
            self.text_msglist.insert(END,text_message1,'green')
            text_message2 = u"2.设置基准日期，检测应用在基准日期之后的更新情况，格式示例: 2017-05-12\n"
            self.text_msglist.insert(END,text_message2,'green')
            text_message3 = u"3.选择配置文件路径，不同网站配置文件可能不同\n"
            self.text_msglist.insert(END,text_message3,'green')
            
    
            
        def start_test(self):

            get_app.Get_App.set_flag('True')
            web_type=self.v1.get()
            base_date=self.v2.get()
            config_path=self.v3.get()
            
            if base_date == '' or base_date.isspace():
                self.text_msglist.insert(END, 'please input base date\n', 'red')
                self.b1.config(state=NORMAL)
                return -1
            if config_path == '' or config_path.isspace():
                self.text_msglist.insert(END, 'please choose config path\n', 'red')
                self.b1.config(state=NORMAL)
                return -1
            
            self.b1.config(state=DISABLED)
            self.b2.config(state=NORMAL)
            thread1=get_app.Get_App('get_app',app,web_type,base_date,config_path)
            thread1.setDaemon(True)
            thread1.start()

        def end_test(self):
            self.b1.config(state=NORMAL)
            get_app.Get_App.set_flag('False')
            self.b2.config(state=DISABLED)
            self.text_msglist.insert(END, 'click end test button,end_test\n', 'blue')
                


        def open_file1(self):
            filename=tkFileDialog.askopenfilename(initialdir =get_app.log_path)
            print filename
            if filename == '':
                return 0
            self.v3.set(filename)

        def open_file2(self):
            filename = tkFileDialog.askopenfilename(initialdir=get_app.result_path)
            if filename == '':
                return 0
            os.startfile(filename)
            
        def close(self):
            
            if get_app.flag:
                result = tkMessageBox.askokcancel(title=u"警告", message=u"测试还未完成，确定要退出程序？")
            else:
                result = tkMessageBox.askokcancel(title=u"退出", message=u"确定退出程序？")
            if result:
                self.root.quit()
                self.root.destroy()


if __name__ == "__main__":

    root=Tk()
    app=Application(root)
    app.creatWidgets()
    app.mainloop()

   


