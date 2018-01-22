#-.-coding:utf-8


"""
拷贝资源并且压缩
从原目录中拷贝到目标目录中，不拷贝重复的资源，删除不需要的资源，拷贝资源会压缩没压缩过的资源
"""

import os
import getopt
import sys
import traceback
import json
import hashlib
import shutil
import time
from collections import OrderedDict

resFile = ""
fromDir = ""
toDir = ""

imgData = {}
data = {}

#解析配置文件
def parseFile():
    global resFile
    global data
    with open(os.path.abspath(resFile),"r") as f:
        data = json.load(f,encoding="utf-8")
        print u"解析文件成功"

#解析图片文件信息，上次压缩过的文件
def parseImgData():
    global imgData
    global fromDir
    imgDataFile = os.path.join(os.path.abspath(os.path.dirname(fromDir)),"imgData.json")
    if os.path.exists(imgDataFile):
        with open(imgDataFile,"r") as f:
            imgData = json.load(f)
            print u"解析文件成功"

#拷贝资源，拷贝压缩目录中没有的资源
def copyImg(depth):
    global fromDir
    global toDir
    global imgData

    fd = os.path.join(fromDir,*depth)
    td = os.path.join(toDir,*depth)
    if not os.path.exists(td):
        os.makedirs(td)

    for f in os.listdir(fd):
        path = os.path.join(fd,f)
        if os.path.isdir(path):
            dp = depth[:]
            dp.append(f)
            copyImg(dp)
        elif os.path.isfile(path):
            if os.path.splitext(path)[1] == ".png":
                parsePng(path,depth[:],f)
            else:
                shutil.copyfile(path, os.path.join(td, f))
                print u"拷贝文件：  " + f


def parsePng(path,depth,imgName):
    global data
    global imgData
    global toDir
    default = data.get("default", 100)
    imgs = data.get("imgs", {})
    dirs = data.get("dirs", {})
    skipImg = data.get("skipImg", [])
    skipDir = data.get("skipDir", [])

    ff = path
    tf = os.path.join(toDir, *depth)
    tf = os.path.join(tf, imgName)

    st_size_t = 0
    st_size_f = os.stat(ff).st_size
    if os.path.exists(tf):
        st_size_t = os.stat(tf).st_size

    imgData[tf] = st_size_t
    imgData[ff] = st_size_f
    if os.path.exists(tf) and imgData.get(ff) == st_size_f and imgData.get(tf) == st_size_t:
        pass
    else:
        if imgName in skipImg:
            shutil.copyfile(ff,tf)
            print u"拷贝文件：" + imgName
        else:
            cp = False
            for d in depth:
                if d in skipDir:
                    cp = True
                    break
            if cp:
                shutil.copyfile(ff, tf)
                print u"拷贝文件：" + imgName
            else:
                quality = default
                for d in depth:
                    if d in dirs:
                        quality = dirs.get(d)
                if imgName in imgs:
                    quality = imgs.get(imgName)

                os.system(r"pngquant.exe --force --quality={0} {1} --output {2}".format(quality, ff,tf))
                print u"压缩文件成功:   " + imgName
                try:
                    if os.path.exists(tf):
                        imgData[tf] = os.stat(tf).st_size
                    else:
                        shutil.copyfile(ff, tf)
                        imgData[tf] = os.stat(tf).st_size
                except:
                    pass




#删除没用的资源
def delImg(depth):
    global fromDir
    global toDir
    global imgData

    fd = os.path.join(fromDir, *depth)
    td = os.path.join(toDir, *depth)

    delList = []

    for f in os.listdir(td):
        fp = os.path.join(fd,f)
        tp = os.path.join(td,f)
        if not os.path.exists(fp):
            if os.path.isdir(tp):
                shutil.rmtree(tp)
                print u"删除文件夹:  " + tp
                for k in imgData:
                    if k.startswith(tp) and imgData.has_key(k):
                        delList.append(k)
            else:
                os.unlink(tp)
                print u"删除文件:  " + tp
                if imgData.has_key(tp):
                    delList.append(tp)
        elif os.path.isdir(tp):
            dp = depth[:]
            dp.append(f)
            delImg(dp)
    for d in delList:
        del imgData[d]

#保存文件
def restore():
    global imgData
    global fromDir
    imgDataFile = os.path.join(os.path.abspath(os.path.dirname(fromDir)), "imgData.json")
    with open(imgDataFile, "w") as f:
        json.dump(imgData,f,indent=4)

def parse():
    global fromDir

    parseFile()
    parseImgData()
    copyImg([])
    delImg([])
    restore()


def main(argv):
    global fromDir
    global toDir
    global resFile
    try:
        opts, args = getopt.getopt(argv, "f:t:c:", ["fromDir=","toDir=","config=",])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'imageMin -f <fromDir> -t <toDir> -c <config> '
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'imageMin -f <fromDir> -t <toDir> -c <config> '
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-f", "--fromDir"):
            fromDir = os.path.abspath(arg)
        elif opt in ("-t", "--toDir"):
            toDir= os.path.abspath(arg)
        elif opt in ("-c", "--config"):
            resFile= os.path.abspath(arg)

    try:
        fromDir = r"F:\work\n5\roll\art\resources"
        toDir = r"F:\work\n5\roll\art\resources_1"
        resFile = r"F:\work\n5\roll\art\tools\src\imageMinInfo.json"
        parse()
    except:
        print traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])