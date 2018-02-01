# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     sourceDownload
   Author :       talus
   date：          2018/1/31 0031
   Description :
-------------------------------------------------

"""
__author__ = 'talus'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import getopt
import re
import json
import datetime
import traceback
import shutil
import time
import requests
import redis


infoFile = ""
resourceDir = ""
domain = ""

redisCli = None

class DownloadTools():
    '''
    下载工具类
    '''
    @staticmethod
    def downloadFile(url):
        '''
        下载链接内容
        :param url:
        :return:
        '''
        global resourceDir

        realUrl = url.split(r"?")[0]   #https://upload.jianshu.io/users/upload_avatars/1716974/1e37c3f70250.gif
        realUrl = realUrl.replace(r"https:","http:")
        realUrl_2 = realUrl.replace(r"https://", "")
        realUrl_2 = realUrl_2.replace(r"http://", "")   # upload.jianshu.io/users/upload_avatars/1716974/1e37c3f70250.gif
        urlPath = realUrl_2.split(r"/")    # ['upload.jianshu.io', 'users', 'upload_avatars', '1716974', '1e37c3f70250.gif']
        domainName = urlPath[0]

        fileDir = os.path.join(os.path.abspath(resourceDir),*urlPath[:-1])
        fileName = urlPath[-1].strip()
        fileName = fileName.split("?")[0]
        fileName = fileName.split("%")[0]
        absFileName = os.path.join(fileDir,fileName)
        if not os.path.exists(fileDir):
            os.makedirs(fileDir)

        ext = fileName.split(".")[-1].strip()
        ext = ext.split(r"?")[0]
        ext = ext.split(r"%")[0]

        if ext == "jpg":
            DownloadTools.downloadJpg(realUrl,absFileName)
        elif ext == "png":
            DownloadTools.downloadPng(realUrl,absFileName)
        elif ext == "gif":
            DownloadTools.downloadGif(realUrl,absFileName)
        elif ext in ["mp3","ogg", "wav"]:
            DownloadTools.downloadMp3(realUrl,absFileName)
        elif ext == "js":
            DownloadTools.downloadJs(realUrl,absFileName)
        elif ext == "html":
            DownloadTools.downloadHtml(realUrl,absFileName)
        elif ext == "css":
            DownloadTools.downloadCss(realUrl,absFileName)
        elif ext == "json":
            DownloadTools.downloadJson(realUrl,absFileName,domainName)
        elif ext == "fnt":
            DownloadTools.downloadFnt(realUrl,absFileName)
        elif ext == "xml":
            DownloadTools.downloadXml(realUrl,absFileName)
        elif ext == "exml":
            DownloadTools.downloadExml(realUrl,absFileName)
        elif ext == "dbbin":
            DownloadTools.downloadDbbin(realUrl,absFileName)
        elif ext == "webp":
            DownloadTools.downloadBin(realUrl,absFileName)
        elif ext == "plist":
            DownloadTools.downloadPlain(realUrl,absFileName)
        elif ext == "ccbi":
            DownloadTools.downloadPlain(realUrl,absFileName)
        elif ext == "zip":
            DownloadTools.downloadBin(realUrl,absFileName)
        else:
            print "ext:  {}".format(ext.strip())
            print "fileName:  {}".format(fileName.strip())
            print ""

    @staticmethod
    def downloadBin(url,filename):
        if os.path.exists(filename):
            print "exist:  {}".format(filename)
            return
        try:
            print "download bin: {}".format(url)
            res = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}, verify=False)
            if res.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(res.content)
                print "download file: {}".format(filename)
            else:
                print "download failed:  {}".format(filename)
                redisCli.lpush("fail_link", url)
            time.sleep(0.5)
        except Exception,e:
            print e.message
            print "download failed:  {}".format(filename)
            redisCli.lpush("fail_link", url)

    @staticmethod
    def downloadPlain(url,filename):
        if os.path.exists(filename):
            print "exist:  {}".format(filename)
            return
        try:
            print "download plain: {}".format(url)
            res = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}, verify=False)
            if res.status_code == 200:
                with open(filename, "w") as f:
                    f.write(res.content)
                print "download file: {}".format(filename)
            else:
                print "download failed:  {}".format(filename)
                redisCli.lpush("fail_link", url)
            time.sleep(0.5)
        except Exception,e:
            print e.message
            print "download failed:  {}".format(filename)
            redisCli.lpush("fail_link", url)

    @staticmethod
    def downloadJpg(url,filename):
        DownloadTools.downloadBin(url,filename)

    @staticmethod
    def downloadPng(url, filename):
        DownloadTools.downloadBin(url,filename)

    @staticmethod
    def downloadGif(url, filename):
        DownloadTools.downloadBin(url, filename)

    @staticmethod
    def downloadMp3(url, filename):
        DownloadTools.downloadBin(url, filename)

    @staticmethod
    def downloadJs(url, filename):
        DownloadTools.downloadPlain(url, filename)

    @staticmethod
    def downloadHtml(url, filename):
        DownloadTools.downloadPlain(url, filename)

    @staticmethod
    def downloadCss(url, filename):
        DownloadTools.downloadPlain(url, filename)

    @staticmethod
    def downloadXml(url, filename):
        DownloadTools.downloadPlain(url, filename)

    @staticmethod
    def downloadExml(url, filename):
        DownloadTools.downloadPlain(url, filename)

    @staticmethod
    def downloadJson(url, filename, domainName):
        DownloadTools.downloadPlain(url, filename)
        fname = os.path.split(filename)[1]
        if fname == r"default.res.json":
            DownloadTools.parseDefaultResJson(url,filename,domain)
        elif fname == r"default.thm.json":
            DownloadTools.parseDefaultThmJson(url,filename,domain)


    @staticmethod
    def parseDefaultResJson(urlStr, filename, domainName):
        print "parseDefaultResJson:  {}".format(filename)
        global redisCli
        urlStr = urlStr.replace(r"default.res.json","")
        if os.path.exists(filename):
            with open(filename,"r") as f:
                content = json.load(f)
                resources = content.get("resources",[])
                if not len(resources):
                    return
                for item in resources:
                    url = item.get("url","")
                    if not url:
                        continue
                    url = url.split(r"?")[0]
                    url = url.split(r"%")[0]

                    newUrl = urlStr + url
                    if not redisCli.sismember("duplicate",newUrl):
                        redisCli.lpush("download",newUrl)
                        redisCli.sadd("duplicate",newUrl)


    @staticmethod
    def parseDefaultThmJson(urlStr, filename, domainName):
        print "parseDefaultThmJson:  {}".format(filename)
        urlStr = urlStr.replace(r"default.thm.json", "")
        if urlStr.endswith(r"resource/"):
            idx = urlStr.index(r"resource/")
            urlStr = urlStr[0:idx]

        if os.path.exists(filename):
            with open(filename, "r") as f:
                content = json.load(f)
                exmls = content.get("exmls", [])
                skins = content.get("skins", {})
                if len(skins):
                    if isinstance(skins,dict):
                        for k,item in skins.iteritems():
                            url = item.split(r"?")[0]
                            url = item.split(r"%")[0]
                            newUrl = urlStr + url
                            redisCli.lpush("download", newUrl)
                if len(exmls):
                    for item in exmls:
                        if isinstance(item,str):
                            url = item.split(r"?")[0]
                            url = item.split(r"%")[0]
                            newUrl = urlStr + url
                            if not redisCli.sismember("duplicate", newUrl):
                                redisCli.lpush("download", newUrl)
                                redisCli.sadd("duplicate", newUrl)
                        elif isinstance(item,dict):
                            path = item.get("path","")
                            if path:
                                url = path.split(r"?")[0]
                                url = item.split(r"%")[0]
                                newUrl = urlStr + url
                                if not redisCli.sismember("duplicate", newUrl):
                                    redisCli.lpush("download", newUrl)
                                    redisCli.sadd("duplicate", newUrl)


    @staticmethod
    def downloadFnt(url, filename):
        DownloadTools.downloadPlain(url, filename)

    @staticmethod
    def downloadDbbin(url, filename):
        DownloadTools.downloadBin(url, filename)


def downNext():
    global redisCli

    while redisCli.llen("download"):
        url = redisCli.rpop("download")
        try:
            DownloadTools.downloadFile(url)
        except Exception,e:
            print e.message




def parseLine(line):
    '''
    解析文件中的一行
    :param line:
    :return:
    '''
    # print "parseLine:  " + line
    global domain
    global redisCli
    if re.search(r"HTTP/1\.1",line):
        urlStr = line.replace(r"GET ","")
        urlStr = urlStr.replace(r" HTTP/1.1","")
        urlStr = urlStr.split(r"?")[0]
        urlStr = urlStr.split(r"%")[0]
        urlStr = urlStr.replace("\n","")
        if domain and re.search(r"//{}/".format(domain),urlStr):
            redisCli.lpush("download", urlStr)


def parse():
    '''
    解析文件
    :return:
    '''
    global infoFile
    print "parse file:  {}".format(infoFile)

    if os.path.exists(infoFile):
        with open(infoFile,"r") as f:
            while True:
                line = f.readline()
                if line:
                    parseLine(line)
                else:
                    break

        os.unlink(infoFile)


def main(argv):
    global resourceDir
    global domain
    global infoFile

    try:
        opts, args = getopt.getopt(argv, "r:d:i:", ["resourceDir=", "domain=","infoFile=",])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'publish -r <resourceDir> -d <domain> -i <infoFile>'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'publish -r <resourceDir> -d <domain> -i <infoFile>'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-r", "--resourceDir"):
            resourceDir = os.path.abspath(arg)
        elif opt in ("-i", "--infoFile"):
            infoFile = os.path.abspath(arg)
        elif opt in ("-d", "--domain"):
            domain = arg


    # resourceDir = os.path.abspath(r"G:\source")
    # infoFile= os.path.abspath(r"G:\source\84_Headers.txt")
    # domain = r"cdn.11h5.com"

    global redisCli
    try:
        redisCli = redis.Redis("127.0.0.1",6379,12)
        parse()
        downNext()
    except Exception,e:
        print traceback.print_exc()



if __name__ == "__main__":
    main(sys.argv[1:])

    # resourceDir = os.path.abspath(r"G:\source")
    #
    # DownloadTools.downloadFile(r"https://cdn.11h5.com/island/vutimes/resource/default.thm.json")