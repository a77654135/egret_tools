#-.-coding:utf-8

import os
import getopt
import sys
import traceback
import json
import shutil
from collections import OrderedDict
from psd_tools import PSDImage,Layer,Group

psdDir = ""
imgDir = ""
jsonFile = ""
currentPsdName = ""
data = OrderedDict()
groundData = OrderedDict()


'''
layer_image = layer.as_PIL()
layer_image.save(pngFile)
'''

#获得文件的名字和扩展名
def getNameAndExt(fileName):
    list = fileName.split(r".")
    length = len(list)
    ext = list[length - 1]
    name = r".".join(list[0:length-1])
    return name,ext

#获得图层或图层组的尺寸信息
def getDimension(layer):
    #"".strip()
    assert isinstance(layer, Group) or isinstance(layer, Layer)
    try:
        if isinstance(layer,Group):
            box = layer.bbox
            return int(box.x1), int(box.y1), int(box.width), int(box.height)
        elif isinstance(layer,Layer):
            #box = layer.transform_bbox if layer.transform_bbox is not None else layer.bbox
            box = layer.bbox
            return int(box.x1), int(box.y1), int(box.width), int(box.height)
        return 0,0,0,0
    except Exception,e:
        # print "--------------------------------------------"
        # print u"解析图层组[ " + layer.name.strip() + u" ]错误：  " + e.message
        # print "--------------------------------------------"
        return 0,0,0,0

def isLayerLocked(layer):
    assert isinstance(layer,Layer) or isinstance(layer,Group)
    locked = False
    try:
        locked = layer._info[9][0]
    except:
        pass
    return locked

def exportImage(group):
    assert isinstance(group,Group)
    global imgDir
    global currentPsdName
    pngDir = os.path.join(os.path.abspath(imgDir),currentPsdName)
    pngDir = os.path.join(pngDir,group.name.strip())
    if not os.path.exists(pngDir):
        os.makedirs(pngDir)
    for layer in group.layers:
        layerName = layer.name.strip()
        sd = "s"
        layerName = layerName.split(":")
        if len(layerName) > 1:
            sd = "d"
        layerName = layerName[0]
        layerName = layerName.split("-")
        layerName = "_".join(layerName)
        buildingName = r"{}_{}_{}_{}.png".format(currentPsdName,group.name.strip(),layerName,sd)
        pngFile = os.path.join(pngDir,buildingName)
        layer_image = layer.as_PIL()
        layer_image.save(pngFile)
        print "export image:  " + buildingName

def exportDimesion(layer,grpName=None,isRight=False):
    global data
    global groundData
    global currentPsdName

    #print "exportDimesion:   " + grpName

    if isinstance(layer,Layer):
        layerName = layer.name.strip()
        if layerName.startswith("ground"):
            x, y, w, h = getDimension(layer)
            groundData["x"] = x
            groundData["y"] = y
            groundData["w"] = w
            groundData["h"] = h
    elif isinstance(layer,Group):
        for l in layer.layers:
            if isLayerLocked(l):
                continue
            pos = "r" if isRight else "l"
            ids = grpName.split("_")
            sd = "s"
            layerNames = l.name.strip().split(":")
            if len(layerNames) > 1:
                sd = "d"
            else:
                sd = "s"
            layerNames = layerNames[0]

            layerNames = layerNames.split("-")
            if len(layerNames) == 1:
                imgName = layerNames[0]
                lvs = [imgName]
            else:
                imgName = "_".join(layerNames)
                lvs = range(int(layerNames[0]),(int(layerNames[1]) + 1))

            x, y, w, h = getDimension(l)
            src = "{}_{}_{}_{}_png".format(currentPsdName, grpName, imgName,sd)
            for lv in lvs:
                for id in ids:
                    # print ids
                    name = "{}_{}_{}_{}".format(currentPsdName, id, lv, pos)
                    data[name] = OrderedDict()
                    data[name]["ox"] = x
                    data[name]["oy"] = y
                    data[name]["w"] = w
                    data[name]["h"] = h
                    data[name]["s"] = src
                    #print src
                    if isRight:
                        data[name]["sx"] = -1



def parseJson():
    global data
    global groundData
    for k in data:
        buildingData = data[k]
        if k == "shadow" or k == "commonBuilding":
            for m in buildingData:
                bd = buildingData[m]
                if not isinstance(bd,dict):
                    continue
                if bd.has_key("sx"):
                    del bd["sx"]
                    bd["ox"] = bd["ox"] - groundData["x"] + bd["w"] - 5
                    bd["oy"] = bd["oy"] - groundData["y"] - 5
                elif bd.has_key("ox"):
                    bd["ox"] = bd["ox"] - groundData["x"]
                    bd["oy"] = bd["oy"] - groundData["y"]
        elif k == "shadow_img" or k == "commonBuilding_img":
            for m in buildingData:
                bd = buildingData[m]
                if bd.has_key("sx"):
                    del bd["sx"]
                    bd["ox"] = bd["ox"] - groundData["x"] + bd["w"] - 5
                    bd["oy"] = bd["oy"] - groundData["y"] - 5
                else:
                    bd["ox"] = bd["ox"] - groundData["x"]
                    bd["oy"] = bd["oy"] - groundData["y"]
        else:
            if buildingData.has_key("sx"):
                del buildingData["sx"]
                buildingData["ox"] = buildingData["ox"] - groundData["x"] + buildingData["w"] - 5
                buildingData["oy"] = buildingData["oy"] - groundData["y"] - 5
            else:
                buildingData["ox"] = buildingData["ox"] - groundData["x"]
                buildingData["oy"] = buildingData["oy"] - groundData["y"]

def parseShadowGroup(group):
    assert isinstance(group,Group) and group.name.strip() == "shadow"
    global data
    global imgDir

    shadow = OrderedDict()
    shadow_img = OrderedDict()

    pngDir = os.path.join(os.path.abspath(imgDir), "shadow")
    if not os.path.exists(pngDir):
        os.makedirs(pngDir)

    for layer in group.layers:
        layerName = layer.name.strip()
        x,y,w,h = getDimension(layer)
        pngName = ""
        if layerName in [str(n) for n in [100,200,300,400,500,600,700,800]]:
            src = "shadow_{}_png".format(layerName)
            pngName = os.path.join(pngDir,"shadow_{}.png".format(layerName))
            shadow[layerName] = OrderedDict()
            shadow[layerName]["ox"] = x
            shadow[layerName]["oy"] = y
            shadow[layerName]["w"] = w
            shadow[layerName]["h"] = h
            shadow[layerName]["s"] = src
        else:
            names = layerName.split(":")
            if len(names) == 2:
                prefix = names[1]
            else:
                prefix = names[1]+"d"

            if not shadow.has_key(prefix):
                shadow[prefix] = []
            min, max = names[0].split("-")
            dataKey = "{}_{}_{}".format(min, max, prefix)
            shadow[prefix].append({
                "min": int(min),
                "max": int(max),
                "data": dataKey
            })
            src = "shadow_{}_png".format(dataKey)
            pngName = os.path.join(pngDir, "shadow_{}.png".format(dataKey))
            shadow_img[dataKey] = OrderedDict()
            shadow_img[dataKey]["ox"] = x
            shadow_img[dataKey]["oy"] = y
            shadow_img[dataKey]["w"] = w
            shadow_img[dataKey]["h"] = h
            shadow_img[dataKey]["s"] = src

        layer_image = layer.as_PIL()
        layer_image.save(pngName)

    data["shadow"] = shadow
    data["shadow_img"] = shadow_img

def parseCreatGroup(group):
    assert isinstance(group, Group) and group.name.strip() == "creat"
    global data
    global imgDir

    commonBuilding = OrderedDict()
    commonBuilding_img = OrderedDict()

    pngDir = os.path.join(os.path.abspath(imgDir), "commonBuilding")
    if not os.path.exists(pngDir):
        os.makedirs(pngDir)

    for layer in group.layers:
        layerName = layer.name.strip()
        x, y, w, h = getDimension(layer)

        names = layerName.split(":")
        if len(names) == 2:
            prefix = names[1]
        else:
            prefix = names[1] + "d"

        if not commonBuilding.has_key(prefix):
            commonBuilding[prefix] = []
        min, max = names[0].split("-")
        dataKey = "{}_{}_{}".format(min, max, prefix)
        commonBuilding[prefix].append({
            "min": int(min),
            "max": int(max),
            "data": dataKey
        })
        src = "commonBuilding_{}_png".format(dataKey)
        pngName = os.path.join(pngDir, "commonBuilding_{}.png".format(dataKey))
        commonBuilding_img[dataKey] = OrderedDict()
        commonBuilding_img[dataKey]["ox"] = x
        commonBuilding_img[dataKey]["oy"] = y
        commonBuilding_img[dataKey]["w"] = w
        commonBuilding_img[dataKey]["h"] = h
        commonBuilding_img[dataKey]["s"] = src


        layer_image = layer.as_PIL()
        layer_image.save(pngName)

    data["commonBuilding"] = commonBuilding
    data["commonBuilding_img"] = commonBuilding_img


def parsePsd(group):
    for layer in group.layers:
        if isLayerLocked(layer):
            continue
        if isinstance(layer,Layer):
            exportDimesion(layer)
        elif isinstance(layer,Group):
            grpName = layer.name.strip()
            lst = grpName.split(r":")
            if len(lst) > 1 and (lst[1] == "right" or lst[1] == "r"):
                exportDimesion(layer,lst[0],True)
            elif grpName == "shadow":
                #阴影层，特殊处理
                parseShadowGroup(layer)
            elif grpName == "creat":
                #阴影层，特殊处理
                parseCreatGroup(layer)
            else:
                exportImage(layer)
                exportDimesion(layer,grpName)

def parseFile(file,depth,fileName):
    ext = os.path.splitext(file)[-1]
    if ext != ".psd":
        return
    if fileName.startswith("unuse"):
        return
    global imgDir
    global currentPsdName

    currentPsdName,_ = getNameAndExt(fileName)

    psd = PSDImage.load(file)
    parsePsd(psd)

def walkDir(dir,depth):
    for f in os.listdir(dir):
        path = os.path.join(dir,f)
        dph = depth[:]
        if os.path.isfile(path):
            parseFile(path,dph,f)
        elif os.path.isdir(path):
            dph.append(f)
            walkDir(path,dph)

def parse():
    global psdDir
    global jsonFile
    global data
    walkDir(os.path.abspath(psdDir),[])
    parseJson()
    if jsonFile:
        with open(os.path.abspath(jsonFile),"w") as f:
            json.dump(data,f)
            print "export json ok."


def main(argv):
    global psdDir
    global imgDir
    global jsonFile
    try:
        opts, args = getopt.getopt(argv, "p:i:j:", ["psdDir=", "imgDir=", "jsonFile="])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'convertPsd -p <psdDir> -i <imgDir> -j <jsonFile>'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'convertPsd -p <psdDir> -i <imgDir> -j <jsonFile>'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-p", "--psdDir"):
            psdDir = arg
        elif opt in ("-i", "--imgDir"):
            imgDir = arg
        elif opt in ("-j", "--jsonFile"):
            jsonFile = arg

    try:
        parse()
    except:
        print traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])