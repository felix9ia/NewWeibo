#coding=utf-8
import requests
import smtplib
import time
import threading
import re
import logging
from lxml import etree
from email.mime.text import MIMEText
from email.header import Header


cookie = {"Cookie": "这里填你的cookie信息"}
sender = '这里填你的发送方邮箱'
receivers = '这里填你的接收方邮箱'
smtp_server = '这里填你的发送方邮箱SMTP服务地址'
password = '这里填你的发送方邮箱密码'

pattern = re.compile(r'^.{1,2}秒前|^.{1,2}分钟前|^今天')
filehandler = logging.FileHandler(filename='newweibo.log',encoding="utf-8")
fmter = logging.Formatter(fmt="%(asctime)s [line:%(lineno)d] %(levelname)s %(message)s",datefmt="%Y-%m-%d %H:%M:%S")
filehandler.setFormatter(fmter)
loger = logging.getLogger(__name__)
loger.addHandler(filehandler)
loger.setLevel(logging.INFO)

def spider(url):
    startFlag = 0;
    lastText = '';
    while True:
        print('**************************')
        loger.info('**************************')
        try:
            currentText = '';
            html = requests.get(url, cookies = cookie).content
            selector = etree.HTML(html)
            lastweibo = selector.xpath('/html/body/div[@class="c"][1]/div[1]/span[@class="ctt"][1]')[0]
            if(lastweibo.text != None):
                currentText += lastweibo.text
            for t in lastweibo.getchildren():
                if(t.text != None):
                    currentText += t.text
                if(t.tail != None):
                    currentText += t.tail
            lastweiboTime = selector.xpath('/html/body/div[@class="c"][1]/div[last()]/span[last()]')[0]
            print(lastweiboTime.text)
            loger.info(lastweiboTime.text)
            
            if(startFlag == 0):
                lastText = currentText
                startFlag = 1
            elif(currentText != lastText):
                if(pattern.match(lastweiboTime.text) != None):
                    print('准备发送邮件')
                    loger.info('准备发送邮件')
                    message = MIMEText(currentText, 'plain', 'utf-8')
                    message['From'] = Header(sender)
                    message['To'] =  Header(receivers)
                    message['Subject'] = Header('微博'+url, 'utf-8')
                    server = smtplib.SMTP()
                    server.connect(smtp_server)
                    server.login(sender,password) #登录邮箱
                    server.sendmail(sender,receivers,message.as_string())  #将msg转化成string发出
                    server.quit()
                    print('发送结束')
                    loger.info('发送结束')
                    lastText = currentText
                else:
                    print('爬取错误')
                    loger.warning('爬取错误')
                    print(currentText)
                    loger.info(currentText)
                    print(lastText)
                    loger.info(lastText)
            
            time.sleep(60)
        except Exception as e:
            print(e)
            loger.warning(e)
        print('**************************')
        loger.info('**************************')

threads = []
t1 = threading.Thread(target=spider, args=(u'https://weibo.cn/u/1974808274?filter=1&page=1',))
threads.append(t1)
t2 = threading.Thread(target=spider, args=(u'https://weibo.cn/u/1904769205?filter=1&page=1',))
threads.append(t2)

for t in threads:
    t.setDaemon(True)
    t.start()
for t in threads:
    t.join()
