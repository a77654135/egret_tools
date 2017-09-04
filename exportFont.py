#-.-coding:utf-8
# author: talus
# date: 2017/09/03
# email: talus_wang@sina.com

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import getopt
import json
import shutil
from psd_tools import PSDImage,Group,Layer

psDir = ""
fontDir = ""

nameMap = {}
count = 0

def getName():
    global count
    count += 1
    return "f_{}".format(count)

#获得文件的名字和扩展名
def getNameAndExt(fileName):
    list = fileName.split(r".")
    length = len(list)
    ext = list[length - 1]
    name = r".".join(list[0:length-1])
    return name,ext

#解析PSD文件:  test.psd
def parsePsd(psdName):
    global psDir
    global fontDir
    global nameMap

    name,ext = getNameAndExt(psdName)
    psdFile = os.path.join(psDir,psdName)
    psd = PSDImage.load(psdFile)
    dir = os.path.join(fontDir,name)
    if os.path.exists(dir):
       shutil.rmtree(dir)
    os.makedirs(dir)
    for layer in psd.layers:
        try:
            layer_img = layer.as_PIL()
            name = getName()
            nameMap[name+"_png"] = layer.name
            imgName = os.path.join(dir,name+".png")
            layer_img.save(imgName)
        except Exception,e:
            pass

#打包字体
def packFont():
    global fontDir
    for dir in os.listdir(fontDir):
        path = os.path.join(fontDir,dir)
        os.system(r"TextureMerger.exe -p {} -o {}.fnt".format(path,path))

#删除散图
def rmFiles():
    global fontDir
    for name in os.listdir(fontDir):
        path = os.path.join(fontDir,name)
        if os.path.isdir(path):
            shutil.rmtree(path)

def replaceName():
    global fontDir
    global nameMap
    newContent = {}
    for name in os.listdir(fontDir):
        path = os.path.join(fontDir, name)
        if os.path.isfile(path):
            name,ext = getNameAndExt(name)
            if ext == "fnt":
                try:
                    with open(path, mode='r') as f:
                        content = json.load(f, encoding="utf-8")
                        newContent["file"] = content["file"]
                        newContent["frames"] = {}
                        if content["frames"] is not None:
                            frames = content["frames"]
                            for nm in frames:
                                if nm in nameMap:
                                    newContent["frames"][nameMap[nm]] = frames[nm]
                                else:
                                    newContent["frames"][nm] = frames[nm]
                    print "unlink: " + path
                    os.unlink(path)
                    with open(path,mode='w') as f:
                        print "write: " + path
                        json.dump(newContent, f,indent=4)
                    print u"解析{} 文件 success......".format(name)
                except Exception, e:
                    print "--------------------------------------------"
                    print u"解析{} 文件 failed......".format(name)
                    print e.message
                    print "--------------------------------------------"

def parse():
    global psDir
    global fontDir

    if os.path.exists(fontDir):
        shutil.rmtree(fontDir)

    psDir = os.path.abspath(psDir)
    fontDir = os.path.abspath(fontDir)

    for file in os.listdir(psDir):
        name,ext = getNameAndExt(file)
        if ext != "psd":
            continue
        parsePsd(file)


def main(argv):
    global psDir
    global fontDir
    try:
        opts, args = getopt.getopt(argv, "p:f:", ["psDir=", "fontDir="])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'usage python convertPsd.py -p <psDir> -f <fontDir>'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'usage python convertPsd.py -p <psDir> -f <fontDir>'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-p", "--psDir"):
            psDir = arg
        elif opt in ("-f", "--fontDir"):
            fontDir = arg

    # psDir = r"C:\work\N5\roll\psd\font"
    # fontDir = r"C:\work\N5\roll\font"

    try:
        parse()
        packFont()
        replaceName()
        rmFiles()
    except Exception,e:
        print "--------------------------------------------"
        print "error:  " + e.message
        print "--------------------------------------------"

    # parse()
    # packFont()
    # replaceName()
    # rmFiles()


def main2():
    '''
    not use, for debug
    :return:
    '''
    psd = PSDImage.load(r'C:\work\N5\roll\psd\test.psd')

    print psd

if __name__ == '__main__':
    #main2()
    main(sys.argv[1:])