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

exmlDir = ""
tsDir = ""

dstDir = ""
dstFile = ""
ignoreFile = ""
ignoreList = []
expectedFile = ""




class ExmlHandler( xml.sax.ContentHandler):
   def __init__(self):
       self.content = ""
       self.tsName = ""
       self.ids = []
       self.buttonNames = []
       self.hasButton = False
       self.hasTween = False
       self.tweenIds = []

   # 元素开始事件处理
   def startElement(self, tag, attributes):
       if tag == "e:Skin":
           self.content = ""
           self.tsName = ""
           self.ids = []
           self.buttonNames = []
           self.hasButton = False
           self.hasTween = False
           self.tweenIds = []

           className = attributes.getValue("class")
           self.tsName = className.replace("Skin","")
       elif re.match(r".*Button.*",tag):
           id = attributes.getValue("id")
           name = attributes.getValue("name")
           self.ids.append((id,tag))
           self.buttonNames.append(name)
           self.hasButton = True
       else:
           id = ""
           try:
               id = attributes.getValue("id")
           except Exception,e:
               pass
           finally:
               if id != "":
                   self.ids.append((id,tag))
               else:
                   pass

   def getIdContent(self):
       content = ""
       for item in self.ids:
           id = item[0]
           tag = item[1]
           tags = tag.split(":")
           cls = u""
           if tags[0] == "e":
               cls = u"eui." + tags[1]
           elif tags[0] == "n":
               cls = tags[1]
           elif tag == r"tween:TweenGroup":
               cls = r"egret.tween.TweenGroup"
               self.hasTween = True
               self.tweenIds.append(id)
           if cls != u"":
               cls = u": " + cls
           content += u"    private {}{};".format(id,cls)
           content += u"\n"
       return content

   def getIdEvents(self):
       content = u""

       content += u"    private onClick(e: egret.TouchEvent) {\n"
       content += u"        var name = e.target.name;\n"
       #content += u"        var name = target.name;\n"
       content += u"        switch(name) {\n"

       for name in self.buttonNames:
           content += u'            case "%s":\n' % name
           content += u"                this.on%sClick();\n" % name.capitalize()
           content += u"                break;\n"

       content += u"        }\n"
       content += u"    }\n"
       content += u"\n"

       for name in self.buttonNames:
           content += u"    private on%sClick() {\n" % name.capitalize()
           content += u"\n"
           content += u"    }\n"

           content += u"\n"

       return content

   def getTweenContent(self):
       if self.hasTween:
           content = u""
           for id in self.tweenIds:
               content += u"        this.{}.stop();\n".format(id)
           return content
       else:
           return u""


   def getContent(self,hasButton):
       content = u""
       content += u"/**\n"
       content += u"* author:talus\n"
       content += u"* date:{}\n".format(datetime.date.today())
       content += u"*/\n"

       if not hasButton:
           content += u"class %s extends eui.Component {" % self.tsName
           content += u"\n"
           content += u"    private disposed: boolean = false;\n"
           content += self.getIdContent()
           content += u"\n"
           content += u""
           content += u"    public constructor() {\n"
           content += u"        super();\n"
           content += u"        this.skinName = %sSkin;\n" % self.tsName
           content += u"        this.init();\n"
           content += u"    }\n"
           content += u"\n"
           content += u"    public init() {\n"
           content += u"        this.disposed = false;\n"
           content += u"        this.addEventListener(egret.Event.REMOVED_FROM_STAGE,this.dispose,this);\n"
           content += u"    }\n"
           content += u"\n"
           content += u"    /**\n"
           content += u"    * 清理资源\n"
           content += u"    * 手动调用或者从显示列表移除时自动调用\n"
           content += u"    */\n"
           content += u"    public dispose() {\n"
           content += u"        if (this.disposed) {\n"
           content += u"            return;\n"
           content += u"        }\n"
           content += u"        this.disposed = true;\n"
           content += u"\n"
           content += self.getTweenContent()
           content += u"        this.removeEventListener(egret.Event.REMOVED_FROM_STAGE,this.dispose,this);\n"
           content += u"        if (this.parent) {\n"
           content += u"            this.parent.removeChild(this);\n"
           content += u"        }\n"
           content += u"    }\n"
           content += u"}\n"
       else:
           content += u"class %s extends eui.Component {\n" % self.tsName
           content += u"    private disposed: boolean = false;\n"
           content += self.getIdContent()
           content += u"\n"
           content += u"    public constructor() {\n"
           content += u"        super();\n"
           content += u"        this.skinName = %sSkin;\n" % self.tsName
           content += u"        this.init();\n"
           content += u"    }\n"
           content += u"\n"
           content += u"    public init() {\n"
           content += u"        this.disposed = false;\n"
           content += u"        this.addEventListener(egret.Event.REMOVED_FROM_STAGE,this.dispose,this);\n"
           content += u"        this.addEventListener(egret.TouchEvent.TOUCH_TAP,this.onClick,this);\n"
           content += u"    }\n"
           content += u"\n"
           content += self.getIdEvents()
           content += u"\n"

           content += u"    /**\n"
           content += u"    * 清理资源\n"
           content += u"    * 手动调用或者从显示列表移除时自动调用\n"
           content += u"    */\n"
           content += u"    public dispose() {\n"
           content += u"        if (this.disposed) {\n"
           content += u"            return;\n"
           content += u"        }\n"
           content += u"        this.disposed = true;\n"
           content += u"\n"
           content += self.getTweenContent()
           content += u"        this.removeEventListener(egret.Event.REMOVED_FROM_STAGE,this.dispose,this);\n"
           content += u"        this.removeEventListener(egret.TouchEvent.TOUCH_TAP,this.onClick,this);\n"
           content += u"        if (this.parent) {\n"
           content += u"            this.parent.removeChild(this);\n"
           content += u"        }\n"
           content += u"    }\n"
           content += u"}\n"

       return content

   def genTsFile(self):
       global dstDir
       global dstFile

       if not os.path.exists(dstDir):
           os.makedirs(dstDir)
       with open(dstFile,mode="w+") as f:
           f.write(self.getContent(self.hasButton))
           f.close()
           print u"生成文件成功：" + dstFile

   # 元素结束事件处理
   def endElement(self, tag):
       if tag == "e:Skin":
           self.genTsFile()
       else:
           pass


#获得文件的名字和扩展名
def getNameAndExt(fileName):
    list = fileName.split(r".")
    length = len(list)
    ext = list[length - 1]
    name = r".".join(list[0:length-1])
    return name,ext

def walkDir(dir,parser,depthPath):
    global ignoreList
    global expectedFile

    for name in os.listdir(dir):
        if expectedFile == "" and name in ignoreList:
            continue
        path = os.path.join(dir,name)
        if os.path.isdir(path):
            dp = depthPath[:]
            dp.append(name)
            walkDir(path,parser,dp)
        else:
            if expectedFile != "" and name != expectedFile:
                continue
            nm,ext = getNameAndExt(name)
            if ext == "exml":
                #parser.parse(path)
                parseFile(parser,nm,depthPath,path)

def parseFile(parser,fileName,depthPath,exmlFile):
    global tsDir
    global dstDir
    global dstFile

    depthDir = os.path.join(tsDir,*depthPath)
    depthFile = os.path.join(depthDir,fileName.replace("Skin","") + ".ts")
    if os.path.exists(depthFile):
        #文件存在，不生成
        print u"文件已存在：" + depthFile
        return

    dstDir = depthDir
    dstFile = depthFile
    parser.parse(exmlFile)


def parse():
    global exmlDir
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    Handler = ExmlHandler()
    parser.setContentHandler(Handler)

    walkDir(exmlDir,parser,[])

def parseIgnore():
    global ignoreList
    global ignoreFile
    if ignoreFile != "":
        try:
            with open(ignoreFile) as f:
                ignoreList = json.load(f)
                f.close()
        except Exception,e:
            pass

def main(argv):
    global exmlDir
    global tsDir
    global ignoreFile
    global expectedFile
    try:
        opts, args = getopt.getopt(argv, "e:t:i:", ["exmlDir=", "tsDir=","ignore=","expectedFile="])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'convertPsd -e <exmlDir> -t <tsDir> -i <ignoreFileJson> --expectedFile'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'convertPsd -e <exmlDir> -t <tsDir> -i <ignoreFileJson> --expectedFile'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-e", "--exmlDir"):
            exmlDir = os.path.abspath(arg)
        elif opt in ("-t", "--tsDir"):
            tsDir = os.path.abspath(arg)
        elif opt in ("-i", "--ignore"):
            ignoreFile = os.path.abspath(arg)
        elif opt in ("--expectedFile",):
            expectedFile = arg

    # exmlDir = r"C:\work\N5\roll\client\client\resource\skins"
    # tsDir = r"C:\work\N5\roll\client\client\src\game\view"

    try:
        parseIgnore()
        parse()
    except Exception,e:
        print u"出错咯： " + e.message


if __name__ == '__main__':
    #parse()
    main(sys.argv[1:])