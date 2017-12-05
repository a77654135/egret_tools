#-.-coding:utf-8
"""
bone合并图片
把一个文件夹下面的bone图片合成在一起
"""

import os
import getopt
import sys
import traceback
import json
import shutil
from PIL import Image

boneDir = ""


def parse():

    global boneDir

    ske_list = []
    tex_list = []
    png_list = []

    absDir = os.path.abspath(boneDir)
    parentName = os.path.split(boneDir)[1]

    for f in os.listdir(absDir):
        if f.endswith(r"ske.json"):
            ske_list.append(f)
        elif f.endswith(r"tex.json"):
            tex_list.append(f)
        elif f.endswith(r"tex.png"):
            png_list.append(f)

    pngStr = ""
    for f in png_list:
        pngStr += os.path.join(absDir,f)
        pngStr += " "
    outJson = os.path.join(absDir,parentName+"_all.json")
    outPng = outJson.replace("_all.json","_all.png")
    outStr = outJson
    os.system(r"TextureMerger.exe -p {} -o {}".format(pngStr,outStr))

    img = Image.open(outPng, "r")
    width,height = img.size

    outPng = os.path.split(outPng)[1]

    with open(outJson,"r") as f:
        allJson = json.load(f)

    for tex in tex_list:
        absTex = os.path.join(absDir,tex)
        with open(absTex,"r") as f:
            content = json.load(f)
        oriImg = content.get("imagePath","")
        imgKey = oriImg.replace(r".png","_png")
        content["imagePath"] = outPng
        content["width"] = width
        content["height"] = height
        info = allJson["frames"][imgKey]
        SubTexture = content.get("SubTexture",{})
        for item in SubTexture:
            item["x"] = item["x"] + info["x"]
            item["y"] = item["y"] + info["y"]
        with open(absTex, "w") as f:
            json.dump(content,f,indent=4)

    os.unlink(outJson)
    for f in png_list:
        os.unlink(os.path.join(absDir,f))




def main(argv):
    global boneDir
    try:
        opts, args = getopt.getopt(argv, "d:", ["boneDir=",])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'boneMerger -d <boneDir>'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'boneMerger -d <boneDir>'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-d", "--boneDir"):
            boneDir = arg

    try:
        #boneDir = r"F:\work\n5\roll\client\client\resource\assets\animation\dragonbone\map\juming"
        parse()
    except:
        print traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])