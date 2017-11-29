#-.-coding:utf-8

import os
import getopt
import sys
import traceback
import json
import re
import shutil
from collections import OrderedDict
from psd_tools import PSDImage,Layer,Group

psdDir = ""
resFile = ""
data = {}

currentPsd = ""

psdInfo = OrderedDict()
result = []


def getLayerName(layer):
    assert isinstance(layer,Layer) or isinstance(layer,Group)
    name = layer.name
    name = name.split(":")[0].split(" ")[0].strip()
    return name

def getAttr(layer,attrName):
    assert isinstance(layer, Layer) or isinstance(layer, Group)

    name = layer.name
    names = name.split(":")
    if len(names) > 1:
        attrsStr = names[1]
        attrs = attrsStr.split(";")
        if len(attrs) > 0:
            for attrInfo in attrs:
                infos = attrInfo.split("=")
                if infos[0] == attrName:
                    return infos[1]
            return None
        else:
            return None
    else:
        return None


def checkGroup(group):
    global psdInfo
    global currentPsd

    if not psdInfo.has_key(currentPsd):
        psdInfo[currentPsd] = OrderedDict()

    id = getAttr(group,"id")
    if id:
        if psdInfo.has_key(id):
            psdInfo[currentPsd][id] += 1
        else:
            psdInfo[currentPsd][id] = 1

        if id == "roadGrp":
            checkRoadAndGround(group,"road")
        elif id == "groundGrp":
            checkRoadAndGround(group,"ground")


def checkRoadAndGround(group,prefix):
    global psdInfo
    global currentPsd

    info = psdInfo[currentPsd]
    info[prefix] = OrderedDict()

    for layer in group.layers:
        name = getAttr(layer,"name")
        if name is None:
            continue
        if info[prefix].has_key(name):
            info[prefix][name] += 1
        else:
            info[prefix][name] = 1



def checkPsd(psdFile):
    global currentPsd
    currentPsd = os.path.split(psdFile)[1]

    print "parse psd: " + os.path.split(psdFile)[1]
    psd = PSDImage.load(psdFile)
    for layer in psd.layers:
        if isinstance(layer,Group):
            checkGroup(layer)



def walk(d):
    for f in os.listdir(d):
        if f.startswith("unuse"):
            continue
        path = os.path.join(d,f)
        if os.path.isdir(path):
            walk(path)
        elif os.path.splitext(f)[1] == ".psd":
            checkPsd(path)

def analysis():
    global psdInfo
    global result
    global data

    result = []

    grps = ["gameGrp","roadGrp","groundGrp"]

    for psdName,info in psdInfo.iteritems():
        result.append(psdName)
        road_count = re.findall(r".*_([0-9]+).psd",psdName)[0]

        for g in grps:
            if not info.has_key(g):
                result.append(u"    缺少图层组："+g)
        for k,v in info.iteritems():
            if k != "ground" and k != "road":
                if v > 1:
                    result.append((u"    图层组命名重复，有{}个图层组:{}".format(v,k)))
        if info.has_key("ground"):
            grounds = info["ground"]
            if data.has_key(road_count):
                lst = data[road_count]
                lst.extend([100,300,500,700])
                for rid in lst:
                    if grounds.has_key("ground_"+str(rid)):
                        if grounds["ground_"+str(rid)] > 1:
                            result.append(u"    图层命名重复，有{}个图层：{}".format(grounds["ground_"+str(rid)],"ground_"+str(rid)))
                    else:
                        result.append(u"    缺少图层："+("ground_"+str(rid)))
            else:
                pass
        if info.has_key("road"):
            grounds = info["road"]
            if data.has_key(road_count):
                lst = data[road_count]
                lst.extend([100, 300, 500, 700])
                for rid in lst:
                    if grounds.has_key("road_"+str(rid)):
                        if grounds["road_"+str(rid)] > 1:
                            result.append(u"    图层命名重复，有{}个图层：{}".format(grounds["road_"+str(rid)],"road_"+str(rid)))
                    else:
                        result.append(u"    缺少图层："+("road_"+str(rid)))
            else:
                pass

        result.append("")
        result.append("")

    global psdDir
    with open(os.path.join(os.path.abspath(psdDir),"result.txt"),"w") as f:
        for line in result:
            line += "\n"
            f.write(line.encode('utf-8'))




def parse():
    global psdDir
    walk(os.path.abspath(psdDir))

    analysis()


def main(argv):
    global psdDir
    global resFile
    global data
    global psdInfo
    try:
        opts, args = getopt.getopt(argv, "d:f:", ["psdDir=","resFile="])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'checkPsd -d <psdDir> -f <resFile>'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'checkPsd -d <psdDir> -f <resFile>'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-f", "--resFile"):
            resFile = arg
        elif opt in ("-d", "--psdDir"):
            psdDir = arg

    try:
        # resFile = r"F:\work\n5\roll\art\psd_check.json"
        # psdDir = r"F:\work\n5\roll\art\psd\city"

        with open(os.path.abspath(resFile),"r") as f:
            data = json.load(f)

        parse()
        #print psdInfo
    except:
        print traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])