# -*- coding: UTF-8 -*-

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import getopt
import shutil


flashDir = ""
dstDir = ""
force = False



#删除文件，重新生成
def removeDst():
    global dstDir
    shutil.rmtree(dstDir)
    if not os.path.exists(dstDir):
        os.makedirs(dstDir)

#生成对应文件夹中的文件
def parseDir(dir,depthPath):
    global dstDir
    dstPath = os.path.join(dstDir,*depthPath)
    os.system("TextureMerger.exe -mc {} -o {}".format(dir,dstPath))

def walkDir(dir,depthPath):
    parseDir(dir,depthPath)
    for name in os.listdir(dir):
        path = os.path.join(dir,name)
        if os.path.isdir(path):
            dp = depthPath[:]
            dp.append(name)
            walkDir(path,dp)

def parse():
    global flashDir
    walkDir(flashDir,[])


def main(argv):
    global flashDir
    global dstDir
    global force
    try:
        opts, args = getopt.getopt(argv, "f:d:", ["flashDir=", "dstDir=","force="])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'convertPsd -f <flashDir> -d <dstDir> --force'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'convertPsd -f <flashDir> -d <dstDir> --force'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-f", "--flashDir"):
            flashDir = os.path.abspath(arg)
        elif opt in ("-d", "--dstDir"):
            dstDir = os.path.abspath(arg)
        elif opt in ("--force"):
            force = True

    # exmlDir = r"C:\work\N5\roll\client\client\resource\skins"
    # tsDir = r"C:\work\N5\roll\client\client\src\game\view"

    try:
        if force:
            removeDst()
        parse()
    except Exception,e:
        print u"出错咯： " + e.message


if __name__ == '__main__':
    #parse()
    main(sys.argv[1:])