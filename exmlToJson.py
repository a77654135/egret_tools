# -*- coding: UTF-8 -*-

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import getopt
import xml.sax
import re
import json
import datetime
import traceback
import collections

exmlDir = ""
currentFile = ""



class ExmlHandler( xml.sax.ContentHandler):

    def __init__(self):
        self.data = collections.OrderedDict()
        #当前正在解析的节点
        self.curNode = None
        #当前解析的借点的父节点
        self.parentNode = None


    # 元素开始事件处理
    def startElement(self, tag, attributes):
        # print "startElement:  " + tag
        #
        # for k in dict(attributes):
        #     print k,attributes[k]

        attr = dict(attributes)
        if tag.strip() == "e:Skin":
            self.curNode = self.data
            if attr.has_key("width"):
                self.curNode["width"] = int(attr["width"])
            if attr.has_key("height"):
                self.curNode["height"] = int(attr["height"])
            self.curNode["children"] = []
        else:
            self.parentNode = self.curNode
            self.curNode = collections.OrderedDict()
            self.parentNode["children"].append(self.curNode)

            tagList = tag.split(":")
            self.curNode["class"] = tagList[-1]
            if tagList[-1] == "Group":
                self.curNode["children"] = []

            for k in attr:
                if k == "touchEnabled":
                    self.curNode["touchEnabled"] = attr[k] == "true"
                elif k == "touchChildren":
                    self.curNode["touchChildren"] = attr[k] == "true"
                elif k == "width":
                    prop = attr[k]
                    if prop.endswith(r"%"):
                        self.curNode["percentWidth"] = int(prop.replace(r"%",""))
                    else:
                        self.curNode["width"] = int(prop)
                elif k == "height":
                    prop = attr[k]
                    if prop.endswith(r"%"):
                        self.curNode["percentHeight"] = int(prop.replace(r"%", ""))
                    else:
                        self.curNode["height"] = int(prop)
                elif k == "source":
                    prop = attr[k]
                    propList = prop.split(r".")
                    if len(propList) > 1:
                        self.curNode["source"] = propList[-1]
                    else:
                        self.curNode["source"] = prop
                elif k == "x":
                    self.curNode["x"] = int(attr[k])
                elif k == "y":
                    self.curNode["y"] = int(attr[k])
                elif k == "alpha":
                    self.curNode["alpha"] = float(attr[k])
                elif k == "id":
                    self.curNode["id"] = attr[k]
                elif k == "name":
                    self.curNode["name"] = attr[k]
                else:
                    self.curNode[k] = attr[k]




    # 元素结束事件处理
    def endElement(self, tag):
        # print "endElement..........." + tag
        self.curNode = self.parentNode


    def endDocument(self):
        # print "endDocument"
        # print self.data
        global currentFile
        path, filename = os.path.split(currentFile)
        fname = os.path.join(path,filename.replace(r".exml",r".json"))

        with open(fname,"w") as f:
            json.dump(self.data,f,indent=4)



def parseFile(filename):
    '''
    解析单个文件
    :param filename:
    :return:
    '''
    if os.path.splitext(filename)[1] != ".exml":
        return

    print "parseFile:  {}".format(filename)
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    Handler = ExmlHandler()
    parser.setContentHandler(Handler)

    global currentFile
    currentFile = filename
    parser.parse(filename)



def parse():
    global exmlDir
    walkDir(exmlDir)



def walkDir(dirName):
    for f in [x for x in os.listdir(os.path.abspath(dirName))]:
        path = os.path.join(dirName, f)
        if os.path.isdir(path):
            walkDir(path)
        else:
            parseFile(path)



def main(argv):
    global exmlDir
    try:
        opts, args = getopt.getopt(argv, "e:", ["exmlDir=", ])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'exmlToJson -e <exmlDir> '
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'exmlToJson -e <exmlDir> '
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-e", "--exmlDir"):
            exmlDir = os.path.abspath(arg)

    try:
        exmlDir = os.path.abspath(r"F:\work\n5\roll\client\stable_client\resource\skins\city")
        parse()
    except Exception,e:
        print traceback.print_exc()

def ttt():
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    Handler = ExmlHandler()
    parser.setContentHandler(Handler)

    parser.parse(r"")

if __name__ == '__main__':

    # parseFile(r"F:\work\n5\roll\client\stable_client\resource\skins\city\City_huoguo\City_huoguo_5Skin.exml")

    main(sys.argv[1:])