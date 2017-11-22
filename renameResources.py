#-.-coding:utf-8

import os
import getopt
import sys
import traceback
import json
import hashlib
import shutil
import time

resFile = ""
root = ""
data = {}
mapInfo = {}


def parseFile():
    global resFile
    global data
    with open(os.path.abspath(resFile),"r") as f:
        data = json.load(f,encoding="utf-8")
        print u"解析文件成功"

def walk(d):
    global mapInfo
    absDir = os.path.abspath(d)
    for f in os.listdir(absDir):
        newf = os.path.join(absDir,f)
        if os.path.isdir(newf):
            walk(newf)
        else:
            #根据文件名生成md5
            path, fname = os.path.split(newf)
            m = hashlib.md5()
            m.update(fname)
            m.update(str(time.time()))
            newName = m.hexdigest()
            newFile = os.path.join(path, newName)
            os.rename(newf, newFile)
            #旧文件名：｛
            #    "name"："新文件名",
            #    "path": "路径"
            # ｝
            mapInfo[fname] = {
                "name":newName,
                "path":path
            }

            print "rename:  " + fname

#加密json
def encryptJson(jsonFile):
    with open(jsonFile,"r") as f:
        jsonContent = json.load(f)
        content = json.dumps(jsonContent)
    ret = ""
    for s in content:
        ret += (chr(ord(s) - 4))
    with open(jsonFile, "w") as f:
        f.write(ret)

    print "encrypt png: " + os.path.split(jsonFile)[1]

def encryptPng(pngFile):
    with open(pngFile,"rb") as f:
        f.seek(0,2)
        length = f.tell()
        f.seek(16,0)
        #content = f.read(length - 12)
        content = []
        for i in range(length - 28):
            content.append(f.read(1))

    with open(pngFile,"wb") as f:
        for i in content:
            f.write(i)

    print "encrypt png: " + os.path.split(pngFile)[1]



#替换json文件中的file:属性
#加密
def replInfo():
    global mapInfo
    #替换名字
    for k,v in mapInfo.iteritems():
        ext = os.path.splitext(k)[1]
        file = os.path.join(v["path"], v["name"])
        if ext in [".json",".fnt"]:
            with open(file,"r") as f:
                content = json.load(f)
            if content.has_key("file"):
                fname = content["file"]
                if mapInfo.has_key(fname):
                    content["file"] = mapInfo[fname]["name"]
            with open(file,"w") as f:
                json.dump(content,f)

            #加密json
            encryptJson(file)
        # elif ext == ".png":
        #     encryptPng(file)

    print "replace info success."

def rewriteFile():
    global resFile
    global mapInfo
    with open(os.path.abspath(resFile),"r") as f:
        content = json.load(f)
    resources = content.get("resources","")
    for item in resources:
        url = item.get("url")
        if url:
            path,name_version = os.path.split(url)
            name,version = name_version.split("?")
            if mapInfo.has_key(name):
                item["url"] = r"{}/{}".format(path,mapInfo[name]["name"])
                if item["type"] == "json":
                    item["type"] = "o"
                elif item["type"] == "sheet":
                    item["type"] = "p"
                elif item["type"] == "font":
                    item["type"] = "q"
                elif item["type"] == "font":
                    item["type"] = "q"
                # elif item["type"] == "image" and item["name"].endswith("_png"):
                #     item["type"] = "m"
    with open(os.path.abspath(resFile),"w") as f:
        json.dump(content,f,indent=4)
    print "rewrite file success."

def parse():
    global root
    global mapInfo

    parseFile()
    walk(os.path.join(os.path.abspath(root),"assets"))
    replInfo()
    rewriteFile()

    with open(os.path.join(os.path.abspath(root),"mapInfo.json"),"w") as f:
        json.dump(mapInfo,f,indent=4)



def main(argv):
    global resFile
    global root
    try:
        opts, args = getopt.getopt(argv, "f:r:", ["file=","root=",])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'renameResources -f <resFile> -r root'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'renameResources -f <file> -r root'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-f", "--file"):
            resFile = arg
        elif opt in ("-r", "--root"):
            root= arg

    try:
        resFile = r"F:\work\n5\roll\client\client\resource\default.res.json"
        root = r"F:\work\n5\roll\client\client\resource"
        parse()
        # pngFile = r"F:\work\n5\roll\art\resources\unuse\common_bg_add2.png"
        # encryptPng(pngFile)
    except:
        print traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])