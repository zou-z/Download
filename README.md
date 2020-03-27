# Download
python多线程下载程序
## 目录
[使用方法](#使用方法)  
[参数配置](#参数配置)  
[帮助](#帮助)  
## 库
```
requests
threading
os
time
```
## 使用方法
两种打开方式：  
1.双击Download.py文件  
2.运行命令```python Download.py  ```   
然后分别输入下载链接和文件名
## 参数配置
可配置的参数都在Config类中  
1.链接: Config.url  
2.文件名: Config.file_name   
```
文件名可以是相对路径也可以是绝对路径，输入示例：
picture.jpg
download\picture.jpg
D:\music.mp3
````
3.多线程数: Config.thread_num  
4.请求头: Config.headers  
5.输出信息: Config.output  
## 界面
[######][xxx][xxx]  
1.第一个中括号: 文件已下载完成的位置信息  
2.第二个中括号: 正在运行的线程数  
3.第三个中括号: 已下载大小
## 返回值
start函数返回值(str类型)有以下5种：  
```
FileExists: 失败，文件名已存在
ExistsTheSameDir: 失败，存在同名文件夹
ErrorUrl: 失败，链接错误
MultiThread: 成功，正以多线程下载
SingleThread: 成功，正以单线程下载  
```
## 帮助
### 1.出现无法用多线程下载  
由于一些服务器采用chunked编码将内容分块输出，响应头中没有content-length不能确定文件的大小，所以只能用单线程下载  
### 2.命令提示符窗口怎么不动了
由于在下载中的时候鼠标点击了命令提示符窗口导致它进入选择模式，按下ESC键即可恢复
### 3.直接运行Download.py闪烁了一下，窗口就不见了
输入的链接无效或输入的文件名无效，可运行命令python Download.py运行程序，查看报错信息
