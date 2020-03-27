# 多线程下载程序
# 主页地址: https://github.com/zou-z/Download
import requests
import threading
import os
import time

class Config(object):
    def __init__(self):
        self.url=""
        self.file_name=""
        self.thread_num=64
        self.headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
            "Connection":"keep-alive"
        }
        self.output=self.__get_output()

    def __get_output(self):
        return {
            "url":"链接地址",
            "file_name":"文件名",
            "file_length":"文件大小",
            "thread_num":"线程数",
            "single_thread_download":"无法多线程下载，正以单线程下载文件...",
            "downloaded_length":"已下载",
            "file_exists":"文件名已存在",
            "exists_the_same_dir":"存在同名文件夹",
            "download_failed":"下载失败，链接无效！(404)",
            "download_finished":"下载完成",
            "spend_time":"耗时",
            "writing_file":"正在写入",
            "writing_finished":"写入完成",
            "press_any_key":"按任意键退出",
        }

class Download(Config):
    def __init__(self):
        super().__init__()
        self.url=input("{0}: ".format(self.output["url"]))
        self.file_name=input("{0}: ".format(self.output["file_name"]))
        self.session=requests.session()
        self.file_length=0
        self.data=[bytes()]*self.thread_num
        self.working_thread_num=0
        self.downloaded_length=0
        self.file_status=[" "]*50
        self.can_write=True
        self.start_time=0

    def __check_input_data(self):
        res=self.session.head(self.url,headers=self.headers)
        if res.status_code==200:
            if os.path.isfile(self.file_name):
                return "FileExists"
            elif os.path.isdir(self.file_name):
                return "ExistsTheSameDir"
            try:
                self.file_length=int(res.headers["content-length"])
                return "MultiThread"
            except KeyError:
                return "SingleThread"
        elif res.status_code==404:
            return "ErrorUrl"

    def start(self):
        res=self.__check_input_data()
        if res=="FileExists":
            print(self.output["file_exists"])
        elif res=="ExistsTheSameDir":
            print(self.output["exists_the_same_dir"])
        elif res=="ErrorUrl":
            print(self.output["download_failed"])
        else:
            self.start_time=time.time()
            if res=="SingleThread":
                print(self.output["single_thread_download"])
                res=self.session.get(self.url,headers=self.headers,stream=True)
                with open(self.file_name,"wb") as f:
                    for chunk in res.iter_content(chunk_size=10240):
                        f.write(chunk)
                        self.downloaded_length+=len(chunk)
                        print("{0}: {1}\t\t".format(self.output["downloaded_length"],self.__format_num(self.downloaded_length)),end="\r")
                self.session.close()
                print("\n{0},{1}{2}".format(self.output["download_finished"],self.output["spend_time"],self.__format_time(int(time.time()-self.start_time))))
            elif res=="MultiThread":
                print("{0}: {1}".format(self.output["file_length"],self.__format_num(self.file_length)))
                print("{0}: {1}".format(self.output["thread_num"],self.thread_num))
                offset=self.file_length/self.thread_num
                for i in range(self.thread_num):
                    t=threading.Thread(target=self.__get,args=(int(i*offset+0.5),int((i+1)*offset+0.5)-1,i))
                    self.__change_working_thread_num(True)
                    t.start()
        if not res=="MultiThread":
            input(self.output["press_any_key"])
        return res

    def __get(self,start,end,index):
        self.__display()
        headers=dict(self.headers)
        headers["Range"]="bytes={0}-{1}".format(start,end)
        res=self.session.get(self.url,headers=headers)
        while len(res.content)<(end-start+1):
            res=self.session.get(self.url,headers=headers)
            print(start,end,index)
        self.data[index]=res.content
        self.__change_working_thread_num(False)
        self.downloaded_length+=end-start+1
        self.__display(index)
        if self.working_thread_num==0:
            self.session.close()
            print("\n{0},{1}{2},{3}...".format(self.output["download_finished"],self.output["spend_time"],self.__format_time(int(time.time()-self.start_time)),self.output["writing_file"]))
            with open(self.file_name,"wb") as f:
                for i in range(len(self.data)):
                    f.write(self.data[i])
            print(self.output["writing_finished"])
            input(self.output["press_any_key"])

    def __display(self,index=None):
        while not self.can_write:
            pass
        self.can_write=False
        if not index==None:
            if self.thread_num<len(self.file_status):
                offset=len(self.file_status)/self.thread_num
                for i in range(int(index*offset+0.5),int((index+1)*offset+0.5)):
                    self.file_status[i]="#"
            elif len(self.file_status)<self.thread_num:
                offset=self.thread_num/len(self.file_status)
                for i in range(len(self.file_status)):
                    if self.file_status[i]==" ":
                        for j in range(int(i*offset+0.5),int((i+1)*offset+0.5)):
                            if self.data[j]==bytes():
                                break
                            elif j==(int((i+1)*offset+0.5)-1):
                                self.file_status[i]="#"
            elif len(self.file_status)==self.thread_num:
                self.file_status[index]="#"
        print("[{0}][{1}][{2}]\t\t".format("".join(self.file_status),self.working_thread_num,self.__format_num(self.downloaded_length)),end="\r")
        self.can_write=True

    def __change_working_thread_num(self,add):
        while not self.can_write:
            pass
        self.can_write=False
        if add:
            self.working_thread_num+=1
        else:
            self.working_thread_num-=1
        self.can_write=True

    def __format_num(self,num):
        units=["B","K","M","G"]
        index=0
        while num>=1024:
            num/=1024
            index+=1
        return "{0:.2f}{1}".format(num,units[index])
    
    def __format_time(self,sec):
        if sec<60:
            return "{0}s".format(sec)
        elif sec<3600:
            minute=int(sec/60)
            if sec%60==0:
                return "{0}min".format(minute)
            else:
                return "{0}min{1}".format(minute,self.__format_time(sec-minute*60))
        elif sec<86400:
            hour=int(sec/3600)
            if sec%3600==0:
                return "{0}hour".format(hour)
            else:
                return "{0}hour{1}".format(hour,self.__format_time(sec-hour*3600))

if __name__ == "__main__":
    download=Download()
    download.start()
