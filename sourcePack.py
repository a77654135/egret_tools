# -*- coding: UTF-8 -*-

"""
分析exml，归纳需要打包的资源
把xxxPanelSkin.exml中的资源收集起来
"""

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import getopt
import re
import json
import datetime
import time
import traceback
import shutil
from PIL import Image

projDir = ""
documentDir = ""
exmlData = {}
exmlLinkNames = {}
panelData = {}
resInfo = {}


def parseResFile():
    global projDir
    global resInfo

    resFile = os.path.join(projDir, "resource", "default.res.json")
    with open(resFile, "r") as f:
        content = json.load(f)
    resources = content.get("resources", [])
    for res in resources:
        name = res["name"]
        type = res["type"]

        if type == "image":
            if name not in resInfo:
                resInfo[name] = type
        elif type == "sheet":
            subkeys = res["subkeys"]
            keys = subkeys.split(",")
            for key in keys:
                resInfo[key] = name


def parseTsFile(tsFile):
    global panelData
    global exmlData
    global exmlLinkNames

    with open(tsFile) as f:
        content = f.read()
    names = re.findall("\ (\w+)\ extends BasePanel", content)
    if not names or not len(names):
        return
    panelName = names[0]
    src_list = re.findall('\.source\ *=\ *"(.*_png)"', content)
    skinName = re.findall('\.skinName\ *=\ *(.*);', content)[0]

    if skinName not in exmlData:
        return
    source_list = exmlData[skinName]
    if not source_list:
        source_list = []
    source_list.extend(src_list)
    # source_list = map(lambda x: x.split(".")[-1], source_list)
    # if len(source_list):
    #     panelData[panelName] = list(set(source_list))

    #搜集itemrender的资源
    itemRenderer = re.findall("\.itemRenderer\ *=\ *(.*?);", content)
    if itemRenderer and len(itemRenderer):
        itemRenderer = itemRenderer[0]
        itemRenderer1 = "{}Skin".format(itemRenderer)
        if itemRenderer in exmlData:
            source_list.extend(exmlData[itemRenderer])
        elif itemRenderer1 in exmlData:
            source_list.extend(exmlData[itemRenderer1])

    links = exmlLinkNames[skinName]
    if links and len(links):
        for skin in links:
            source_list.extend(exmlData[skin])

    source_list = map(lambda x: x.split(".")[-1], source_list)
    if len(source_list):
        panelData[panelName] = list(set(source_list))



def walkTsDirs(dirname):
    for name in os.listdir(dirname):
        filename = os.path.join(dirname, name)
        if name.endswith(".ts"):
            parseTsFile(filename)
        elif os.path.isdir(filename):
            walkTsDirs(filename)

def scanTs():
    global projDir

    tsDir = os.path.join(projDir, "src", "game", "view", "panel")
    walkTsDirs(tsDir)


def parseExmlFile(exmlFile):
    global exmlData
    global exmlLinkNames

    with open(exmlFile, "r") as f:
        content = f.read()
    name_list = re.findall('e:Skin\ class="(.*?)"', content)
    if not name_list or not len(name_list):
        return
    skinName = name_list[0]

    source_list = re.findall('source="(.*_png)"', content)
    exmlData[skinName] = source_list
    exmlLinkNames[skinName] = re.findall('skinName="(.*?)"', content)

def walkExmlDirs(dirname):
    for name in os.listdir(dirname):
        filename = os.path.join(dirname, name)
        if name.endswith(".exml"):
            parseExmlFile(filename)
        elif os.path.isdir(filename):
            walkExmlDirs(filename)


def scanExmls():
    global projDir

    exmlDir = os.path.join(projDir, "resource", "skins")
    walkExmlDirs(exmlDir)



def parseData():
    global panelData
    global resInfo

    for name in panelData:
        src_list = panelData[name]
        new_list = []
        for src in src_list:
            if src not in resInfo:
                continue
            if resInfo[src] == "image":
                new_list.append(src)
            else:
                if resInfo[src] not in new_list:
                    new_list.append(resInfo[src])

        panelData[name] = new_list


def mergeData():
    """
    合并原来的数据,如果原来有图片，并且图片存在，就保留，否则不保留
    :return:
    """
    global documentDir
    global panelData
    global resInfo

    panelFile = os.path.join(documentDir, "panel_n5.json")
    if os.path.exists(panelFile):
        with open(panelFile, "r") as f:
            content = json.load(f)
        for panelName in content:
            if panelName not in panelData:
                new_list = [x for x in content[panelName] if x in resInfo]
                panelData[panelName] = new_list
            else:
                new_list = (x for x in content[panelName] if x in resInfo and x not in panelData[panelName])
                panelData[panelName].extend(new_list)




def main(argv):
    global projDir
    global documentDir

    try:
        opts, args = getopt.getopt(argv, "p:d:", ["projDir=", "documentDir="])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'sourcePack -p <projDir> -d <documentDir> -r <artDir>'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'sourcePack -p <projDir> -d <documentDir> -r <artDir>'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-p", "--projDir"):
            projDir = os.path.abspath(arg)
        elif opt in ("-d", "--documentDir"):
            documentDir = os.path.abspath(arg)

    projDir = r"F:\work\n5\roll\client\client"
    documentDir = r"F:\work\n5\roll\document\表单\json".decode("utf-8")

    try:
        parseResFile()
        scanExmls()
        scanTs()
        parseData()
        mergeData()

        global panelData
        with open(os.path.join(documentDir, "panel_n5.json").decode("utf-8"), "w") as f:
            f.write(json.dumps(panelData, indent=4))
    except Exception,e:
        print traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])