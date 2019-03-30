# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 20:56:26 2019

@author: dell
"""

FOLDERPATH =""#可自定义保存文件与照片路径，默认为当前文件夹下
URL=r"http://v.juhe.cn/jztk/query"

import os
import requests
#Question_bank类用来存储及操作通过API获得的题库
class Question_bank:

    def __init__(self,subject,model,testType="rand"):
        
        self.Qlist = []#存储随机或顺序获得的题库
        self.Wqlist =[]#存储本地的错题
        self.param={
            "key":"",
            "subject":subject,#驾照考试科目
            "model":model,#驾照类型
            "testType":testType,#获取题目序列方式“rand”或“order”
        }
        self.path=FOLDERPATH+self.param["subject"]+"\\"+self.param["model"]+"\\"
    #请求API数据
    def request(self):
        
        try:
            r=requests.get(URL,params=self.param,timeout=10)
            r.raise_for_status()
        except requests.RequestException:
            return False
        else:
            self.Qlist = r.json()["result"]
            return True
    #将错题写入本地文档
    def write_file(self,num=-1):
        #若不提供num值默认将Wqlist写入本地文档
        if num==-1:
            f=open(self.path+"test.txt","w",encoding="utf-8")
            for x in range(len(self.Wqlist)):
                #除去重新做对的题目“id”--“right”，其余题目存入文档
                if self.Wqlist[x]["id"]!="right":
                    f.write("id"+"\t"+self.Wqlist[x]["id"]+"\n")
                    f.write("question"+"\t"+self.Wqlist[x]["question"]+"\n")
                    f.write("answer"+"\t"+self.Wqlist[x]["answer"]+"\n")
                    f.write("item1"+"\t"+self.Wqlist[x]["item1"]+"\n")
                    f.write("item2"+"\t"+self.Wqlist[x]["item2"]+"\n")
                    f.write("item3"+"\t"+self.Wqlist[x]["item3"]+"\n")
                    f.write("item4"+"\t"+self.Wqlist[x]["item4"]+"\n")
                    f.write("explains"+"\t"+self.Wqlist[x]["explains"]+"\n")
                    f.write("url"+"\t"+self.Wqlist[x]["url"]+"\n")
        #若提供num值可将Qlist单独写入文档
        else:
            f=open(self.path+"test.txt","a",encoding="utf-8")
            x=num
            f.write("id"+"\t"+self.Qlist[x]["id"]+"\n")
            f.write("question"+"\t"+self.Qlist[x]["question"]+"\n")
            f.write("answer"+"\t"+self.Qlist[x]["answer"]+"\n")
            f.write("item1"+"\t"+self.Qlist[x]["item1"]+"\n")
            f.write("item2"+"\t"+self.Qlist[x]["item2"]+"\n")
            f.write("item3"+"\t"+self.Qlist[x]["item3"]+"\n")
            f.write("item4"+"\t"+self.Qlist[x]["item4"]+"\n")
            f.write("explains"+"\t"+self.Qlist[x]["explains"]+"\n")
            f.write("url"+"\t"+self.Qlist[x]["url"]+"\n")
        f.close()
    #从文件中读取题目存入Wqlist    
    def read_file(self):
        
        path=self.path+"test.txt"
        #判断文件是否存在
        if not os.path.exists(path):
            return False
        else:
            f=open(path,"r",encoding="utf-8")
            i=-1
            #分行读取字符串，readline返回为list
            for line in f.readlines():
                name = line.split()#spilt函数可以按空格分割每行读取字符串
                if isinstance(name,list) and len(name)==2:
                    if name[0]=="id":
                        i+=1
                        self.Wqlist.append({})
                    self.Wqlist[i][name[0]]=name[1]
                else:
                    #部分未分割的
                    self.Wqlist[i][name[0]]=""
            return True
    #从网络上下载图片                
    def down_loadimg(self,order):
        #图片下载地址与存储地址
        url_info=[self.Qlist[order]["url"],self.path+self.Qlist[order]["id"]+".jpg"]
        if url_info[1]:
            try:
                url = url_info[0]
                response = requests.get(url)
                img = response.content
                path ='%s' % (url_info[1])
                with open(path, 'wb') as f:
                    f.write(img)
                return (True,path)
            except Exception as ex:
                return (False,ex)
                pass        
    #读取appkey，默认appkey.txt内容不可被修改，故不作错误处理    
    def read_appkey(self):
        
        path="appkey.txt"
        if not os.path.exists(path):
            return False
        else:
            f=open(path,"r",encoding="utf-8") 
            self.param["key"]=f.readline()
            f.close()
            return True
        