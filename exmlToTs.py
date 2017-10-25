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

exmlDir = ""
tsDir = ""

dstDir = ""
dstFile = ""
ignoreFile = ""
ignoreList = []
expectedFile = ""
isPanel = 0
isRenderItem = 0




class ExmlHandler( xml.sax.ContentHandler):
   def __init__(self):
       self.content = ""
       self.tsName = ""
       self.ids = []
       self.buttonNames = []
       self.hasButton = False
       self.hasTween = False
       self.tweenIds = []
       self.isInSkin = False

   # 元素开始事件处理
   def startElement(self, tag, attributes):
       #print "startElement:  " + tag
       #print self.isInSkin
       if self.isInSkin:
           return
       if tag == "e:skinName":
           self.isInSkin = True
           return
       if tag == "e:Skin":
           self.content = ""
           self.tsName = ""
           self.ids = []
           self.buttonNames = []
           self.hasButton = False
           self.hasTween = False
           self.tweenIds = []
           self.isInSkin = False

           #print tag
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
               #print e.message
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
           if tag == "n:SimpleButton" or tag == "n:BaseButton":
               continue
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
       global isPanel
       content = u""

       if isPanel:
           content += u"    protected onClick(name: string) {\n"
       else:
           content += u"    private onClick(e: egret.TouchEvent) {\n"
           content += u"        var name = e.target.name;\n"

       content += u"        switch(name) {\n"

       for name in self.buttonNames:
           if isPanel and name=="close" or name == "closeBtn":
               continue
           content += u'            case "%s":\n' % name
           content += u"                this.on%sClick();\n" % name.capitalize()
           content += u"                break;\n"

       content += u"        }\n"
       content += u"    }\n"
       content += u"\n"

       for name in self.buttonNames:
           if isPanel and name=="close" or name == "closeBtn":
               continue
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
       #print "getContent............."
       global isPanel
       global isRenderItem

       content = u""
       content += u"/**\n"
       content += u"* author:talus\n"
       content += u"* date:{}\n".format(datetime.date.today())
       content += u"*/\n"

       if isPanel:
           if not hasButton:
               content += u"class %s extends BasePanel {" % self.tsName
               content += u"\n"
               content += self.getIdContent()
               content += u"\n"
               content += u""
               content += u"    public constructor() {\n"
               content += u"        super();\n"
               content += u"        this.skinName = %sSkin;\n" % self.tsName
               content += u"        this.layer = PanelLayer.BOTTOM_LAYER;\n"
               content += u"        this.mutex = true;\n"
               content += u"    }\n"
               content += u"\n"
               content += u"    public active() {\n"
               content += u"        \n"
               content += u"    }\n"
               content += u"\n"
               content += u"    /**\n"
               content += u"    * 清理资源\n"
               content += u"    * 手动调用或者从显示列表移除时自动调用\n"
               content += u"    */\n"
               content += u"    public dispose() {\n"
               content += self.getTweenContent()
               content += u"        super.dispose();\n"
               content += u"    }\n"
               content += u"}\n"
           else:
               content += u"class %s extends BasePanel {\n" % self.tsName
               content += self.getIdContent()
               content += u"\n"
               content += u"    public constructor() {\n"
               content += u"        super();\n"
               content += u"        this.skinName = %sSkin;\n" % self.tsName
               content += u"        this.layer = PanelLayer.BOTTOM_LAYER;\n"
               content += u"        this.mutex = true;\n"
               content += u"    }\n"
               content += u"\n"
               content += u"    public active() {\n"
               content += u"        \n"
               content += u"    }\n"
               content += u"\n"
               content += self.getIdEvents()
               content += u"\n"

               content += u"    /**\n"
               content += u"    * 清理资源\n"
               content += u"    * 手动调用或者从显示列表移除时自动调用\n"
               content += u"    */\n"
               content += u"    public dispose() {\n"
               content += self.getTweenContent()
               content += u"        super.dispose();\n"
               content += u"    }\n"
               content += u"}\n"
       elif isRenderItem:
           if not hasButton:
               content += u"class %s extends eui.ItemRenderer {" % self.tsName
               content += u"\n"
               content += self.getIdContent()
               content += u"\n"
               content += u""
               content += u"    public constructor() {\n"
               content += u"        super();\n"
               content += u"        this.skinName = %sSkin;\n" % self.tsName
               content += u"        this.addEventListener(egret.Event.REMOVED_FROM_STAGE, this.dispose, this);\n"
               content += u"    }\n"
               content += u"\n"
               content += u"    protected dataChanged() {\n"
               content += u"        super.dataChanged();\n"
               content += u"        \n"
               content += u"    }\n"
               content += u"\n"
               content += u"    public dispose() {\n"
               content += self.getTweenContent()
               content += u"        this.removeEventListener(egret.Event.REMOVED_FROM_STAGE,this.dispose,this);\n"
               content += u"    }\n"
               content += u"}\n"
           else:
               content += u"class %s extends eui.ItemRenderer {" % self.tsName
               content += u"\n"
               content += self.getIdContent()
               content += u"\n"
               content += u""
               content += u"    public constructor() {\n"
               content += u"        super();\n"
               content += u"        this.skinName = %sSkin;\n" % self.tsName
               content += u"        this.addEventListener(egret.Event.REMOVED_FROM_STAGE, this.dispose, this);\n"
               content += u"    }\n"
               content += u"\n"
               content += u"    protected dataChanged() {\n"
               content += u"        super.dataChanged();\n"
               content += u"        \n"
               content += u"    }\n"
               content += u"\n"
               content += self.getIdEvents()
               content += u"\n"
               content += u"    public dispose() {\n"
               content += self.getTweenContent()
               content += u"        this.removeEventListener(egret.Event.REMOVED_FROM_STAGE,this.dispose,this);\n"
               content += u"    }\n"
               content += u"}\n"
       else:
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
               content += u"        DisplayUtil.removeFromParent(this);\n"
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
               content += u"        DisplayUtil.removeFromParent(this);\n"
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
       print u"生成文件成功：" + dstFile

   # 元素结束事件处理
   def endElement(self, tag):
       #print "endElement..........." + tag

       if tag == "e:Skin" and not self.isInSkin:
           self.genTsFile()
       else:
           pass

       if tag == "e:skinName":
           self.isInSkin = False



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

    #print "waldDir:  " + dir
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
    #print "parseFile......................." + fileName
    global tsDir
    global dstDir
    global dstFile

    depthDir = os.path.join(tsDir,*depthPath)
    depthFile = os.path.join(depthDir,fileName.replace("Skin","") + ".ts")
    if os.path.exists(depthFile):
        #文件存在，不生成
        print u"文件已存在：" + fileName
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
    #print "parseIgnore................"
    global ignoreList
    global ignoreFile
    if ignoreFile != "":
        try:
            with open(ignoreFile) as f:
                ignoreList = json.load(f)
                f.close()
        except Exception,e:
            #print e.message
            pass

def main(argv):
    global exmlDir
    global tsDir
    global ignoreFile
    global expectedFile
    global isPanel
    global isRenderItem
    try:
        opts, args = getopt.getopt(argv, "e:t:i:", ["exmlDir=", "tsDir=","ignore=","expectedFile=","panel=","render="])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'convertPsd -e <exmlDir> -t <tsDir> -i <ignoreFileJson> --expectedFile --panel --render'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'convertPsd -e <exmlDir> -t <tsDir> -i <ignoreFileJson> --expectedFile --panel --render'
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
        elif opt in ("--panel",):
            isPanel = int(arg)
        elif opt in ("--render",):
            isRenderItem = int(arg)

    # print "ispanel:  %s" % isPanel
    # print "ispanel:  %s" % isRenderItem

    # exmlDir = r"C:\work\N5\roll\client\client\resource\skins"
    # tsDir = r"C:\work\N5\roll\client\client\src\game\view"

    try:
        parseIgnore()
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

    #ttt()

    #parse()
    main(sys.argv[1:])