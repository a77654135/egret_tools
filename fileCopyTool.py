#-.-coding:utf-8

import os
import getopt
import sys
import traceback
import json
import shutil
from collections import OrderedDict
from psd_tools import PSDImage,Layer,Group

resFile = ""
data = {}


#获得文件的名字和扩展名
def getNameAndExt(fileName):
    list = fileName.split(r".")
    length = len(list)
    ext = list[length - 1]
    name = r".".join(list[0:length-1])
    return name,ext


def parseFile():
    global resFile
    global data
    with open(os.path.abspath(resFile),"r") as f:
        data = json.load(f,encoding="utf-8")

def work():
    global data

    removeFiles = []
    for item in data:
        for k,v in item.iteritems():
            if not k:
                continue
            k = os.path.abspath(k)
            if v == "":
                removeFiles.append(k)
                continue

            p = os.path.abspath(v)
            if not os.path.exists(p):
                os.makedirs(p)

            if os.path.isdir(k):
                copyDir(k,p)
            else:
                tf = os.path.join(p, os.path.split(k)[1])
                shutil.copy(k, tf)
                print "{} -----> {}".format(k, tf)


            # rm = v[1]
            # if rm:
            #     removeFiles.append(k)
            # if not os.path.exists(p):
            #     os.makedirs(p)
            # if os.path.isdir(k):
            #     copyDir(k, os.path.abspath(p))
            # else:
            #     ff = os.path.abspath(k)
            #     tf = os.path.join(os.path.abspath(p), os.path.split(k)[1])
            #     print "{} -----> {}".format(ff, tf)
            #     # shutil.copy(ff,tf)
            #     # os.rename(ff,tf)
            #     shutil.copy(ff, tf)

    for fl in removeFiles:
        if os.path.isdir(fl):
            shutil.rmtree(fl)
        else:
            #os.unlink(fl)
            os.remove(fl)
        print "xxxx ----> {}".format(fl)

def copyDir(path,to):
    for f in os.listdir(path):
        ff = os.path.join(path,f)
        tf = os.path.join(to,f)
        shutil.copy(ff,tf)
        print "{} -----> {}".format(ff, tf)

def parse():
    parseFile()
    work()


def main(argv):
    global resFile
    try:
        opts, args = getopt.getopt(argv, "f:", ["file=",])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'fileCopyTool -f <resFile>'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'fileCopyTool -f <file>'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-f", "--file"):
            resFile = arg

    try:
        #resFile = r"F:\work\n5\roll\client\client\tools\source\fileCopy.json"
        parse()
    except:
        print traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])