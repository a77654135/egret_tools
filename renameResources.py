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

resFile = ""
root = ""
data = {}
mapInfo = {}


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
        print u"解析文件成功"


def walk(d):
    global mapInfo
    absDir = os.path.abspath(d)
    for f in os.listdir(absDir):
        newf = os.path.join(absDir,f)
        if os.path.isdir(newf):
            walk(newf)
        else:
            tm = time.time()

            path, fname = os.path.split(newf)
            m = hashlib.md5()
            m.update(fname)
            m.update(str(tm))
            newName = m.hexdigest()
            newFile = os.path.join(path, newName)
            os.rename(newf, newFile)
            mapInfo[fname] = {
                "name":newName,
                "path":path
            }

            print "rename:  " + fname

def replInfo():
    global mapInfo
    for k,v in mapInfo.iteritems():
        if os.path.splitext(k)[1] in [".json",".fnt"]:
            file = os.path.join(v["path"],v["name"])
            with open(file,"r") as f:
                content = json.load(f)
            if content.has_key("file"):
                fname = content["file"]
                if mapInfo.has_key(fname):
                    content["file"] = mapInfo[fname]["name"]

            jsonContent = json.dumps(content)
            ret = []
            for s in jsonContent:
                ret.append(ord(s) + 4)
            with open(file,"w") as f:
                json.dump(content,f)

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
                item["url"] = r"{}/{}?{}".format(path,mapInfo[name]["name"],version)
                if item["type"] == "json":
                    item["type"] = "o"
                elif item["type"] == "sheet":
                    item["type"] = "p"
                elif item["type"] == "font":
                    item["type"] = "q"
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
        # resFile = r"F:\work\n5\roll\client\client\resource\default.res.json"
        # root = r"F:\work\n5\roll\client\client\resource"
        parse()
    except:
        print traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])