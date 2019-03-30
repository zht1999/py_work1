# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 22:23:44 2019

@author: dell
"""
import cv2 as cv
import numpy as np
import os
#from API import FOLDERPATH
import sys
from API import Question_bank as Qb
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QWidget, QPushButton,QDesktopWidget,QLabel,QGridLayout,
    QMainWindow, QAction,QRadioButton, QApplication,QButtonGroup,QMessageBox)
#答题界面UI
class Question_solvingUI(QWidget):
    
    def __init__(self,subject,model,testType):
        
        super().__init__()    
        
        self.param={
                 "subject":subject,
                 "model":model,
                 "testType":testType,
                 }
        self.img = np.ndarray(())#存储图片
        self.Q=Qb(subject,model,testType)
        self.list=[]#存放当前列表题目
        self.dict={}#存放当前题目
        self.order=-1#存放当前题目在列表中顺序
        self.read_progress()#提取并修改order值
        self.initUI() 
     #初始化界面   
    def initUI(self):
        #初始化界面设置     
        self.resize(400, 300)
        self.center()
        
        self.setWindowTitle('驾照考试题目练习'+self.param["testType"]) 
        
        self.imglabel = QLabel()
        self.explainlabel=QLabel()
        self.explainlabel.setWordWrap(True)#设置解释文本自动换行
        self.title=QLabel()
        
        self.textA = QLabel()
        self.textB = QLabel()
        self.textC = QLabel()
        self.textD = QLabel()
        
        self.btnA=QPushButton("A")
        self.btnB=QPushButton("B")
        self.btnC=QPushButton("C")
        self.btnD=QPushButton("D")
        self.btnnext=QPushButton("下一题")
        self.btnstop=QPushButton("结束做题")
        #布局设定
        grid = QGridLayout()
        grid.addWidget(self.title, 1,0,1,1)
        grid.addWidget(self.btnA, 2, 0,1,1)
        grid.addWidget(self.textA, 2, 1,1,3)
        grid.addWidget(self.btnB, 3, 0,1,1)
        grid.addWidget(self.textB, 3, 1,1,3)
        grid.addWidget(self.btnC, 4, 0,1,1)
        grid.addWidget(self.textC, 4, 1,1,3)
        grid.addWidget(self.btnD, 5, 0,1,1)
        grid.addWidget(self.textD, 5, 1,1,3)
        grid.addWidget(self.imglabel,6,0,1,4)
        grid.addWidget(self.explainlabel,7,0,3,4)
        grid.addWidget(self.btnnext, 10,0,1,1)
        grid.addWidget(self.btnstop, 10,2,1,1)
        #信号与槽连接
        self.btnA.clicked.connect(self.buttonclicked)
        self.btnB.clicked.connect(self.buttonclicked)
        self.btnC.clicked.connect(self.buttonclicked)
        self.btnD.clicked.connect(self.buttonclicked)
        self.btnnext.clicked.connect(self.practice)
        self.btnstop.clicked.connect(self.toclose)
        
        self.setLayout(grid)
        self.show()
        #初始化题库
        if self.param["testType"]=="wrong":
            #读取文档初始化Wqlist
            if not self.Q.read_file():
                QMessageBox.information(self,"Information","您还没有错题呢，先去随机测试或顺序做题吧！")
                self.close()
            else:
                self.list=self.Q.Wqlist
                self.practice()
        else:
            #判断是否成功连接API，初始化Qlist
            if self.Q.read_appkey()&self.Q.request():
                self.list=self.Q.Qlist
                self.practice()
            else:
                QMessageBox.information(self,"Information","未成功读取数据，请检查网络状态与appkey是否导入")
                self.close()
    #控制窗口显示在屏幕中心    
    def center(self):
        
        qr = self.frameGeometry()
        #获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        #显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())
     #开始做题输出题目信息   
    def practice(self):
        
        self.order+=1#题目次序依次变化
        #通过题目次序判断列表是否输出完
        if self.order<len(self.list):
            self.dict=self.list[self.order]
            self.title.setText(self.dict["id"]+' . '+self.dict["question"])
            self.textA.setText(self.dict["item1"])
            self.textB.setText(self.dict["item2"])
            self.textC.setText(self.dict["item3"])
            self.textD.setText(self.dict["item4"])
            self.explainlabel.setText("")
            #获取输出图片，复习错题本地获取，其他类型链接下载
            if self.dict["url"]!="":
                if(self.param["testType"]=="wrong"):
                    self.refreshShowimg(self.dict["url"])
                else:
                    status=self.Q.down_loadimg(self.order)
                    if status[0]==True:
                        self.refreshShowimg(status[1])
                        self.Q.Qlist[self.order]["url"]=status[1]                        
                    else:
                        QMessageBox.information(self,"Information","未成功下载图片，请检查网络设置！")
            else:
                self.imglabel.setPixmap(QPixmap(""))
        else:
            QMessageBox.information(self,"Information","题目已经做完了")    
    #获取显示图片
    def refreshShowimg(self,fileName):
        #获取图片
        self.img = cv.imread(fileName, -1)
        if isinstance(self.img,np.ndarray):
            # 提取图像的尺寸和通道, 用于将opencv下的image转换成Qimage
            height, width, channel = self.img.shape
#原本试图调节图片大小来适应窗口，但发现压缩之后图片变得很不清晰
#            if width>400 & width>height:
#                img=cv.resize(self.img,None,fx=400/width,fy=400/width,interpolation=cv.INTER_AREA)
#            elif height>300:
#                img=cv.resize(self.img,None,fx=300/height,fy=300/height,interpolation=cv.INTER_AREA)
#            else:
#                img=self.img
            img=self.img
            bytesPerLine = 3 * width
            self.qImg = QImage(img.data, width, height, bytesPerLine,
                               QImage.Format_RGB888).rgbSwapped()
            # 将Qimage显示出来
            self.imglabel.setPixmap(QPixmap.fromImage(self.qImg)) 
        else:
            QMessageBox.information(self,"Information","未成功找到图片，请检查保存路径！")
            return
     #槽函数，与选项按钮连接   
    def buttonclicked(self):
        #获取信号发出按钮
        sender=self.sender()
        #比较与正确答案是否相同
        str_ex="\n"+"正确答案："+chr(ord('A')+ord(self.dict["answer"])-ord('1'))+"  解释："+self.dict["explains"]
        if ord(sender.text())==(ord('A')+ord(self.dict["answer"])-ord('1')):
            self.explainlabel.setText("正确"+str_ex)
            self.remove()
            if self.param["testType"]=="wrong":
                #修改复习错题中作对题的“id”
                self.Q.Wqlist[self.order]["id"]="right"
        else:
            self.explainlabel.setText("错误"+str_ex)
            if self.param["testType"]!="wrong":
                #将错题写入文档
                self.Q.write_file(self.order)
    #读取order学习进度            
    def read_progress(self):
        if self.param["testType"]=="order":
            path=self.Q.path+"progress.txt"
            if os.path.exists(path):
                f=open(path,"r")
                #读取并修改order值
                self.order=int(f.readline())-1
                f.close()
            else:
                self.order=-1  
        else:
            self.order=-1
    #槽函数，关闭窗口            
    def toclose(self):

        if self.param["testType"]=="wrong":
            self.Q.write_file()
        elif self.param["testType"]=="order":
            f=open(self.Q.path+"progress.txt","w")
            #在关闭程序之前写入学习进度
            f.write(str(self.order))
            f.close()
        self.close()
    #删除缓存图片
    def remove(self):
        if os.path.exists(self.dict["url"]):
            os.remove(self.dict["url"])
#主窗口
class menu(QMainWindow):
    
    def __init__(self):
        
        self.info1=''#选项结果
        self.info2=''#选项结果
        self.status_selected = False#选项状态
        self.param={
                "subject":"",
                "model":"",
                "testType":"",
                 }
        super().__init__()
        self.initUI()
    #初始化界面    
    def initUI(self):
        #创建状态栏
        self.statusBar()
        self.statusBar().showMessage('Ready')
        #创建事件
        exitAction = QAction("退出", self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')#状态栏提示语
        exitAction.triggered.connect(self.close)#槽函数
        randAction = QAction("随机测试", self)
        randAction.setStatusTip("随机测试题目")
        randAction.triggered.connect(self.QrUI)
        orderAction= QAction("顺序练习", self)
        orderAction.setStatusTip("顺序练习题目")
        orderAction.triggered.connect(self.QoUI)
        wrongAction= QAction("复习错题", self)
        wrongAction.setStatusTip("复习错题")
        wrongAction.triggered.connect(self.QwUI)
        #创建工具栏
        self.toolbar = self.addToolBar("rand")
        self.toolbar.addAction(randAction)
        self.toolbar = self.addToolBar("order")
        self.toolbar.addAction(orderAction)
        self.toolbar = self.addToolBar("wrong")
        self.toolbar.addAction(wrongAction)
        self.toolbar = self.addToolBar("exit")
        self.toolbar.addAction(exitAction)
        #创建菜单栏
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&选项")
        fileMenu.addAction(exitAction)
        
        self.label = QLabel("请选择考试科目和驾照类型：",self)
        self.label.resize(300,50)
        self.label.wordWrap=True
        self.rb11 = QRadioButton('科目一',self)
        self.rb12 = QRadioButton('科目四',self)
        self.rb21 = QRadioButton('c1',self)
        self.rb22 = QRadioButton('c2',self)
        self.rb23 = QRadioButton('a1',self)
        self.rb24 = QRadioButton('a2',self)
        self.rb25 = QRadioButton('b1',self)
        self.rb26 = QRadioButton('b2',self)
        self.bt1 = QPushButton('提交',self)
        #布局设定，由于radiobuton在用其他布局方式时不能显示，所以选择绝对布局
        self.label.move(30,100)
        self.rb11.move(20,150)
        self.rb12.move(20,250)
        self.rb21.move(170,150)
        self.rb22.move(170,200)
        self.rb23.move(170,250)
        self.rb24.move(230,150)
        self.rb25.move(230,200)
        self.rb26.move(230,250)
        self.bt1.move(150,300)
        #radiobutton单选分组
        self.bg1 = QButtonGroup(self)
        self.bg1.addButton(self.rb11, 11)
        self.bg1.addButton(self.rb12, 12)

        self.bg2 = QButtonGroup(self)
        self.bg2.addButton(self.rb21, 21)
        self.bg2.addButton(self.rb22, 22)
        self.bg2.addButton(self.rb23, 23)
        self.bg2.addButton(self.rb24, 24)
        self.bg2.addButton(self.rb25, 25)
        self.bg2.addButton(self.rb26, 26)
        #信号与槽函数连接
        self.bg1.buttonClicked.connect(self.rbclicked)
        self.bg2.buttonClicked.connect(self.rbclicked)
        self.bt1.clicked.connect(self.submit)
        
        self.resize(500,400)
        self.center()
        self.setWindowTitle("驾照考试题目练习") 
        self.show()
    #将窗口设定在屏幕中心，同上一个类    
    def center(self):
        
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    #槽函数，给出选项内容
    def rbclicked(self):
        
        sender = self.sender()
        if sender == self.bg1:
            if self.bg1.checkedId() == 11:
                self.info1 = '1'
            elif self.bg1.checkedId() == 12:
                self.info1 = '4'
            else:
                self.info1 = ''
        else:
            if self.bg2.checkedId() == 21:
                self.info2 = 'c1'
            elif self.bg2.checkedId() == 22:
                self.info2 = 'c2'
            elif self.bg2.checkedId() == 23:
                self.info2 = 'a1'
            elif self.bg2.checkedId() == 24:
                self.info2 = 'a2'
            elif self.bg2.checkedId() == 25:
                self.info2 = 'b1'
            elif self.bg2.checkedId() == 26:
                self.info2 = 'b2'
            else:
                self.info2 = ''
    #槽函数，提交选项内容    
    def submit(self):
        
        if self.info1=='' or self.info2=='':
            QMessageBox.information(self,"Information","请选择完全！")
            return
        QMessageBox.information(self,"Information","接下来您可以选择开始做答")
        self.status_selected=True#选项状态，此处表示已选中
        self.param["subject"]=self.info1
        self.param["model"]=self.info2
        self.mkdir()#创建保存目录
        self.label.setText("请选择考试科目和驾照类型"+"\n"+"科目:"+self.info1+"\t"+"驾照："+self.info2)
    #槽函数，调用子窗口，开始做题
    def QrUI(self):
        if self.status_selected:
            self.QUI=Question_solvingUI(self.param["subject"],self.param["model"],"rand")
        else:
            QMessageBox.information(self,"Information","请先选择考试项目提交，再选择随机测试")
    def QoUI(self):
        
        if self.status_selected:
            self.QUI=Question_solvingUI(self.param["subject"],self.param["model"],"order")
        else:
            QMessageBox.information(self,"Information","请先选择考试项目提交，再选择顺序做题")            
    def QwUI(self):
        if self.status_selected:
            self.QUI=Question_solvingUI(self.param["subject"],self.param["model"],"wrong")
        else:
            QMessageBox.information(self,"Information","请先选择考试项目提交，再选择复习错题")            
    #创建存储目录
    def mkdir(self):
        
        path=self.param["subject"]+"\\"+self.param["model"]
        if not os.path.exists(path):
            os.makedirs(path)
            return True
        else:
            return False
#主函数
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = menu()
    sys.exit(app.exec_())  