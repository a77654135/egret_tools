#-.-coding:utf-8

import os
import getopt
import sys
import traceback
import json
import hashlib
import shutil
import time
from collections import OrderedDict
from psd_tools import PSDImage,Layer,Group

path = ""
resFile = ""
data = {}

def parseFile():
    global resFile
    global data
    with open(os.path.abspath(resFile),"r") as f:
        data = json.load(f,encoding="utf-8")
        print u"解析文件成功"


def walk(d):
    global data
    default = data.get("default",30)
    names = data.get("name",{})
    skip = data.get("skip",[])
    absDir = os.path.abspath(d)
    for f in os.listdir(absDir):
        newf = os.path.join(absDir,f)
        if os.path.isdir(newf):
            walk(newf)
        else:
            name,ext = os.path.splitext(f)
            if ext == ".png":
                if name in skip:
                    continue
                if name in names:
                    quality = names[name]
                else:
                    quality = default
                os.system(r"pngquant.exe --force --quality={0} {1} --output {1}".format(quality,newf))
                print "imageMin:  " + os.path.split(newf)[1]


def parse():
    global path

    parseFile()
    walk(os.path.abspath(path))



def main(argv):
    global resFile
    global path
    try:
        opts, args = getopt.getopt(argv, "p:f:", ["path=","resFile=",])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'imageMin -p <path> -f resFile'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'imageMin -p <path> -f resFile'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-p", "--path"):
            path = arg
        elif opt in ("-f", "--resFile"):
            resFile= arg

    try:
        # resFile = r"F:\work\n5\roll\art\imageMinInfo.json"
        # path = r"F:\work\n5\roll\art\resources\texture"
        parse()
    except:
        print traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])