# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     mergeAnimation
   Author :       talus
   date：          2018/1/4 0004
   Description : 把一个文件夹中的骨骼动画，MC，和普通图片合并在一起
-------------------------------------------------

"""
__author__ = 'talus'

import os
import getopt
import sys
import traceback
import re
import json
import time
from PIL import Image

resDir = ""
packJson = ""
allJson = {}


'''
os.system(r"TextureMerger.exe -p {} -o {}".format(dir,os.path.join(path,"{}.json".format(name))))
'''

def parse():
    pack()
    time.sleep(1)
    parseJsons()

def pack():
    global resDir
    global packJson
    resDir = os.path.abspath(resDir)
    path,dirname = os.path.split(resDir)
    packJson = os.path.join(resDir,dirname + "_all.json")
    mergeStr = ur"TextureMerger.exe -p {} -o {} -e /.*.png".format(resDir.decode("utf-8"),packJson.decode("utf-8"))
    os.system(mergeStr)
    print mergeStr

    #删除已经打包的小图
    for f in [x for x in os.listdir(resDir) if os.path.splitext(x)[1] == ".png" and not x.endswith(r"_all.png")]:
        path = os.path.join(resDir,f)
        os.unlink(path)



def parseJsons():
    global resDir
    global packJson
    global allJson

    with open(packJson.decode("utf-8"),"r") as fp:
        allJson = json.load(fp)

    for f in [n for n in os.listdir(resDir) if (os.path.splitext(n)[1] == ".json" or os.path.splitext(n)[1] == ".fnt") and not re.search("_ske",n) and not re.search("_all",n)]:
        parseJson(f)

def parseJson(jsonFile):
    global packJson
    global allJson

    path,allName = os.path.split(packJson)
    allName = allName.replace(".json",".png")
    allName = allName.replace(".fnt",".png")
    outPng = packJson.replace("_all.json","_all.png")
    img = Image.open(outPng, "r")
    width, height = img.size

    with open(os.path.join(resDir, jsonFile), "r") as fp:
        content = json.load(fp)
    res = content.get("res", None)
    frames = content.get("frames", None)
    SubTexture = content.get("SubTexture", None)
    pngName = jsonFile.replace(r".json", "_png")
    pngName = pngName.replace(r".fnt", "_png")
    pngData = allJson["frames"][pngName]
    if res:
        for k,v in content["res"].iteritems():
            for s,p in v.iteritems():
                if s == "x":
                    content["res"][k]["x"] = content["res"][k]["x"] + pngData["x"] + pngData["offX"]
                if s == "y":
                    content["res"][k]["y"] = content["res"][k]["y"] + pngData["y"] + pngData["offY"]
    elif frames:
        content["file"] = allName
        for k,v in content["frames"].iteritems():
            for s,p in v.iteritems():
                if s == "x":
                    content["frames"][k]["x"] = content["frames"][k]["x"] + pngData["x"] + pngData["offX"]
                if s == "y":
                    content["frames"][k]["y"] = content["frames"][k]["y"] + pngData["y"] + pngData["offY"]
    elif SubTexture:
        content["imagePath"] = allName
        content["width"] = width
        content["height"] = height
        for item in SubTexture:
            for k,v in item.iteritems():
                if k == "x":
                    item["x"] = item["x"] + pngData["x"] + pngData["offX"]
                if k == "y":
                    item["y"] = item["y"] + pngData["y"] + pngData["offY"]


    with open(os.path.join(resDir, jsonFile), "w") as fp:
        json.dump(content,fp,indent=4)



def main(argv):
    global resDir
    try:
        opts, args = getopt.getopt(argv, "d:", ["resDir=",])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'mergeResource -d <resDir>'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'mergeResource -d <resDir>'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-d", "--resDir"):
            resDir = arg

    try:
        # resDir = r"F:\work\n5\roll\art\donghua\donghua\map\juming"
        parse()
    except:
        print traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])