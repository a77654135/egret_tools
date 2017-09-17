#-.-coding:utf-8
# author: talus
# date: 2017/09/03
# email: talus_wang@sina.com

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import getopt
import json
from psd_tools import PSDImage,Group,Layer
from PSDParser import getLabelStrokeInfo,getLabelBold,getLabelItalic,getLabelSize,getLabelColor

psdDir = ""
imgDir = ""
skinDir = ""

absPsdDir = ""
absImgDir = ""
absSkinDir = ""

resFile = "default.res.json"

genImg = False
intelligent = False
force = False
genFontImg = False

resNameMap = {}
currentPsdFile = ""

#获得文件的名字和扩展名
def getNameAndExt(fileName):
    list = fileName.split(r".")
    length = len(list)
    ext = list[length - 1]
    name = r".".join(list[0:length-1])
    return name,ext

#fileName: test.psd
#depthPath: [folder1,folder2,folder3]
def parsePsd(fileName,depthPath):
    global absPsdDir
    global absSkinDir
    global force
    global currentPsdFile

    name,ext = getNameAndExt(fileName)

    currentPsdFile = name

    exmlDir = os.path.join(absSkinDir, *depthPath)
    exmlFile = os.path.join(exmlDir, u"{}Skin.exml".format(name))

    if os.path.exists(exmlFile) and not force:
        print "--------------------------------------------"
        print u"exml 文件已经存在，忽略：  {} ".format(u"{}Skin.exml".format(name))
        print "--------------------------------------------"
        return

    content = u""
    content += u"<?xml version='1.0' encoding='utf-8'?>"
    content += u'\n'
    psd = PSDImage.load(os.path.join(os.path.join(absPsdDir,*depthPath),fileName))
    content += u'<e:Skin class="{}" width="{}" height="{}" xmlns:e="http://ns.egret.com/eui" xmlns:w="http://ns.egret.com/wing" xmlns:n="*">'.format(name+"Skin",psd.header.width,psd.header.height)
    content += u'\n'
    content += parseGroup(psd,0,depthPath[:],True)
    content += u'</e:Skin>'

    if os.path.exists(exmlFile):
        os.unlink(exmlFile)
    if not os.path.exists(exmlDir):
        os.makedirs(exmlDir)

    try:
        with open(exmlFile, mode="w+") as f:
            f.write(content)
            print u"生成 exml 文件：  " + exmlFile
            print u"解析 PSD 成功: {}".format(fileName)
    except Exception,e:
        print "--------------------------------------------"
        print u"解析 PSD 失败:  {}".format(fileName)
        print "--------------------------------------------"

    getImages(psd, depthPath[:])

#从psd文件中，生成图片
def getImages(psd,depthPath):
    global genImg
    global genFontImg
    global absImgDir
    global currentPsdFile
    if not genImg:
        return

    assert isinstance(psd,PSDImage)

    dir = os.path.join(absImgDir, *depthPath)
    dir = os.path.join(dir, currentPsdFile)
    if not os.path.exists(dir):
        os.makedirs(dir)
    for emd in psd.embedded:
        filename = emd.filename
        name,ext = getNameAndExt(filename)
        if ext == "psd":
            continue
        data = emd.data
        imgFile = os.path.join(dir,filename)
        if os.path.exists(imgFile):
            os.unlink(imgFile)
        try:
            with open(imgFile,mode="wb") as f:
                f.write(data)
                print u"生成图片：  " + imgFile
        except Exception,e:
            pass
    # #生成文字图片
    # if genFontImg:
    #     for layer in psd.layers:
    #         if isinstance(layer,Group) and hasattr(layer,"name") and layer.name.strip().startswith(r"$Skin"):
    #             continue
    #         if isinstance(layer,Layer) and layer.text_data is not None:
    #             print u"生成文字图片：" + u"txt_{}.png".format(layer.name.strip())
    #             pngFile = os.path.join(dir,u"txt_{}.png".format(layer.name.strip()))
    #             if os.path.exists(pngFile):
    #                 os.unlink(pngFile)
    #             layer_image = layer.as_PIL()
    #             layer_image.save(pngFile)


#获得图层或图层组的尺寸信息
def getDimension(layer,isButton=False):
    #"".strip()
    assert isinstance(layer, Group) or isinstance(layer, Layer)
    try:
        if isinstance(layer,Group):
            box = layer.bbox
            return box.x1, box.y1, box.width, box.height
        elif isinstance(layer,Layer):
            box = layer.transform_bbox if layer.transform_bbox is not None else layer.bbox
            return box.x1, box.y1, box.width, box.height
        return 0,0,0,0
    except Exception,e:
        # print "--------------------------------------------"
        # print u"解析图层组[ " + layer.name.strip() + u" ]错误：  " + e.message
        # print "--------------------------------------------"
        return 0,0,0,0

#解析属性 名字：属性名=属性值;属性名=属性值;属性名=属性值
def getAttrs(layer):
    assert isinstance(layer,Layer) or isinstance(layer,Group)
    ret = {}
    try:
        if layer.name.strip():
            lst = layer.name.strip().split(r":")
            name = lst[0]
            ret["clsName"] = name[1:] if name.startswith(r"$") else name
            if len(lst) > 1:
                attrs = lst[1]
                if attrs.endswith(r";"):
                    attrs = attrs.rstrip(r";")
                for attr in attrs.split(r";"):
                    k,v = attr.split(r"=")
                    ret[k] = v
            return ret
        else:
            return None
    except Exception,e:
        print layer.name.strip()
        print u"解析名字属性出错： " + e.message
        return None

#合并属性
def mergeAttr(attr1,attr2):
    assert isinstance(attr1,dict) or isinstance(attr2,dict)
    if attr2 is None:
        return attr1
    if attr1 is None:
        return attr2
    ret = {}
    for k,v in attr1.iteritems():
        ret[k] = v
    for k,v in attr2.iteritems():
        ret[k] = v
    return ret

#生成信息
def genContent(layer,clz,otherAttr,depth,isButton=False):
    assert isinstance(layer,Layer) or isinstance(layer,Group)
    attrs = getAttrs(layer)
    if attrs is None:
        return ""

    x, y, width, height = getDimension(layer)
    if isButton:
        x,y = getCenterPos(x,y,width,height)
    oldAttrs = {
        "x": x,
        "y": y,
        "width": width,
        "height": height
    }
    if isButton:
        oldAttrs["anchorOffsetX"] = width * 0.5
        oldAttrs["anchorOffsetY"] = height * 0.5
        oldAttrs["touchChildren"] = "false"
        oldAttrs["touchEnabled"] = "true"

    newAttrs = mergeAttr(oldAttrs, otherAttr)
    newAttrs = mergeAttr(newAttrs,attrs)

    prefix = depth * u"    "
    content = u""
    content += u"{0}<{1} ".format(prefix, clz)
    for k, v in newAttrs.iteritems():
        if k == "clsName":
            continue
        content += u'{0}="{1}" '.format(k, v)
    content += u'/>'
    content += u'\n'
    return content


#解析skinGroup
def parseSkinGroup(group,depth,depthPath,root=False):
    layer = group.layers[0]
    nm = layer.name.strip()
    x, y, width, height = getDimension(layer)

    otherAttr = {
        "skinName": nm + "Skin",
        "x": x,
        "y": y,
        "width": width,
        "height": height
    }
    return genContent(group,r"e:Panel",otherAttr,depth)

#解析其他命名group，扩展group的功能，允许自定义
def parseCommonGroup(group,depth,depthPath,root=False):
    attrs = getAttrs(group)
    if attrs is None:
        return
    cls = attrs["clsName"]
    clz = cls[2:]
    if cls.startswith(r"e_"):
        clz = r"e:" + clz
        return genContent(group,clz,None,depth)
    elif cls.startswith(r"n_"):
        clz = r"n:" + clz
        return genContent(group, clz, None, depth)
    return ""

#通过id属性获得图层
def getLayerById(group,id):
    assert isinstance(group,Group)
    for layer in group.layers:
        attrs = getAttrs(layer)
        if attrs.has_key("id") and attrs["id"] == id:
            return layer
    return None

#获取图层的资源属性
def getLayerSrc(layer,depthPath):
    assert isinstance(layer,Layer)
    names = layer.name.strip().split(r":")
    src = r"{}_png".format(names[0])
    if intelligent:
        length = len(depthPath)
        if length > 0:
            parentFolder = depthPath[length - 1]
            src = getIntelligentSource(src, parentFolder)
    return src

#如果是按钮，设置anchorOffset为中心位置，重新计算x,y坐标
def getCenterPos(x,y,width,height):
    hw = width * 0.5
    hh = height * 0.5
    return x+hw,y+hh

#解析特殊的图层组，根据命名规则，生成对应的信息
def parseButtonGroup(group,depth,depthPath,root=False):
    assert isinstance(group,Group)
    cls = r"n:BaseButton"
    otherAttr = {
        "touchChildren":'false',
        "touchEnabled":'true'
    }
    layers = group.layers
    length = len(layers)
    attrs = getAttrs(group)
    if attrs.has_key("id"):
        otherAttr["name"] = attrs["id"]
    if length == 1:
        otherAttr["skinName"] = "SimpleButtonSkin"
        layer = layers[0]
        src = getLayerSrc(layer,depthPath)
        otherAttr["bgSource"] = src
    elif length > 1:
        bgLayer = getLayerById(group,"bg")
        iconLayer = getLayerById(group,"icon")
        if bgLayer is not None and iconLayer is not None:
            otherAttr["skinName"] = "IconButtonSkin"
        if bgLayer is not None:
            bgSrc = getLayerSrc(bgLayer,depthPath)
            otherAttr["bgSource"] = bgSrc
        if iconLayer is not None:
            iconSrc = getLayerSrc(iconLayer,depthPath)
            otherAttr["iconSource"] = iconSrc
    return genContent(group,cls,otherAttr,depth,True)


#解析特殊的图层组，根据命名规则，生成对应的信息
def parseSpecialGroup(group,depth,depthPath,root=False):
    attrs = getAttrs(group)
    if attrs is None:
        return
    cls = attrs["clsName"]
    if cls == "Skin":
        return parseSkinGroup(group, depth, depthPath, root)
    elif cls == "Button":
        return parseButtonGroup(group, depth, depthPath, root)
    elif cls.startswith(r"e_") or cls.startswith(r"n_"):
        return parseCommonGroup(group, depth, depthPath, root)
    else:
        return ""

#解析psd图层组
def parseGroup(group,depth,depthPath,root=False):
    assert isinstance(group,Group) or isinstance(group,PSDImage)
    if root == False and isLayerLocked(group):
        #如果图层组锁定了，就不要解析了
        return ""
    if hasattr(group,"name"):
        print "111111"
        if group.name.strip().startswith(r"$"):
            print "22222222"
            return parseSpecialGroup(group,depth,depthPath)


    content = u""
    prefix = depth * u"    "
    if root == False:
        oldAttrs = {
            "x": "0",
            "y": "0",
            "width": "100%",
            "height": "100%",
            "touchEnabled":"false",
            "touchChildren":"false"
        }
        attrs = getAttrs(group)
        newAttrs = mergeAttr(oldAttrs, attrs)
        content += u'{}<e:Group '.format(prefix)
        for k,v in newAttrs.iteritems():
            if k == "clsName":
                continue
            content += u'{0}="{1}" '.format(k,v)
        content += u'>\n'
    layers = group.layers
    layers.reverse()
    for layer in layers:
        if isLayerLocked(layer):
            #图层被锁定，不解析
            continue
        if isinstance(layer,Layer):
            content += parseLayer(layer,depth+1,depthPath[:])
        elif isinstance(layer,Group):
            print root
            print layer.name
            content += parseGroup(layer,depth+1,depthPath[:])
    if root == False:
        content += u'{}</e:Group>'.format(prefix)
        content += u'\n'
    return content

#解析psd图层
def parseLayer(layer,depth,depthPath):
    assert isinstance(layer,Layer)
    global absImgDir
    global intelligent
    global genImg
    global genFontImg
    global currentPsdFile

    content = u""
    prefix = depth * u"    "
    isLabel = True if layer.text_data is not None else False
    name = layer.name.strip()
    x,y,width,height = getDimension(layer)
    visible = layer.visible
    alpha = 1 if layer.opacity != 255 else layer.opacity / 255

    oldAttrs = {
        "x":x,
        "y":y,
        "width":width,
        "height":height,
        "touchEnabled":"false"
    }
    if not visible:
        oldAttrs["visible"] = "false"
    if alpha != 1:
        oldAttrs["alpha"] = alpha
    if isLabel:
        oldAttrs["fontFamily"] = "Microsoft YaHei"
        oldAttrs["text"] = layer.text_data.text
        se,sz,sc = getLabelStrokeInfo(layer)
        if se:
            oldAttrs["stroke"] = sz
            oldAttrs["strokeColor"] = sc
        if getLabelBold(layer):
            oldAttrs["bold"] = "true"
        if getLabelItalic(layer):
            oldAttrs["italic"] = "true"
        oldAttrs["size"] = getLabelSize(layer)
        color,alpha = getLabelColor(layer)
        oldAttrs["textColor"] = color
        if alpha != 1:
            oldAttrs["alpha"] = alpha
    else:
        src = r"{}_png".format(name)
        if intelligent:
            length = len(depthPath)
            if length > 0:
                parentFolder = depthPath[length - 1]
                src = getIntelligentSource(src, parentFolder)
        oldAttrs["source"] = src

    attrs = getAttrs(layer)
    newAttrs = mergeAttr(oldAttrs, attrs)

    if isLabel:
        content += u'{}<e:Label '.format(prefix)
        for k,v in newAttrs.iteritems():
            if k == "clsName":
                continue
            content += u'{0}="{1}" '.format(k,v)
        content += u'/>'
    else:
        content += u'{}<e:Image '.format(prefix)
        for k,v in newAttrs.iteritems():
            if k == "clsName":
                continue
            content += u'{0}="{1}" '.format(k,v)
        content += u'/>'
    content += u'\n'

    #遍历layer的时候，如果是字体，生成字体图片
    if genImg and genFontImg and isLabel:
        pngDir = os.path.join(absImgDir,*depthPath)
        pngDir = os.path.join(pngDir,currentPsdFile)
        pngFile = os.path.join(pngDir,u"txt_{}.png".format(name))
        print u"生成字体图片:  " + pngFile
        if os.path.exists(pngFile):
            os.unlink(pngFile)
        if not os.path.exists(pngDir):
            os.makedirs(pngDir)
        layer_image = layer.as_PIL()
        layer_image.save(pngFile)

    return content

#遍历psd的目录
def parseDir(depthPath):
    global absPsdDir
    dir = os.path.join(absPsdDir,*depthPath)
    for f in os.listdir(dir):
        absFile = os.path.join(dir,f)
        if os.path.isdir(absFile):
            dpt = depthPath[:]
            dpt.append(f)
            parseDir(dpt)
        elif os.path.isfile(absFile):
            name, ext = getNameAndExt(f)
            if ext == "psd":
                dpt = depthPath[:]
                parsePsd(f,dpt)

def parse():
    global psdDir
    global imgDir
    global skinDir

    global absPsdDir
    global absImgDir
    global absSkinDir

    absPsdDir = os.path.abspath(psdDir)
    absImgDir = os.path.abspath(imgDir)
    absSkinDir = os.path.abspath(skinDir)

    for f in os.listdir(absPsdDir):
        absFile = os.path.join(absPsdDir,f)
        if os.path.isdir(absFile):
            parseDir([f])
        elif os.path.isfile(absFile):
            name, ext = getNameAndExt(f)
            if ext == "psd":
                parsePsd(f,[])

#解析组员组中的一个资源
def parseSingleResource(res):
    global resNameMap
    if res["type"] == "sheet":
        if res["subkeys"]:
            for name in res["subkeys"].split(r","):
                if resNameMap.has_key(name):
                   resNameMap[name].append(res["name"])
                else:
                    resNameMap[name] = []
                    resNameMap[name].append(res["name"])
    elif res["type"] == "image":
        if resNameMap.has_key(res["name"]):
            resNameMap[res["name"]].append(None)
        else:
            resNameMap[res["name"]] = []
            resNameMap[res["name"]].append(None)

def isLayerLocked(layer):
    assert isinstance(layer,Layer) or isinstance(layer,Group)
    locked = False
    try:
        locked = layer._info[9][0]
    except:
        pass
    return locked


#解析default.res.json文件
def parseResourceFile():
    global resFile
    global resNameMap
    #resFile = r"E:\study\code\EgretProjects\league\resource\default.res.json"
    if os.path.exists(resFile):
        try:
            with open(resFile,mode='r') as f:
                content = json.load(f,encoding="utf-8")
                if content["resources"] is not None:
                    for res in content["resources"]:
                        parseSingleResource(res)
            print u"解析default.res.json文件 success......"
        except Exception,e:
            print "--------------------------------------------"
            print u"解析default.res.json文件 failed......"
            print e.message
            print "--------------------------------------------"
    else:
        print "--------------------------------------------"
        print u'无法找到default.res.json文件 ......'
        print "--------------------------------------------"

#智能选择图片的最优source，减少drawcall
def getIntelligentSource(sourceName,parentFolder):
    global resNameMap
    global currentPsdFile
    try:
        if resNameMap.has_key(sourceName):
            folders = resNameMap[sourceName]
            if currentPsdFile+"_json" in folders:
                return currentPsdFile+r"_json."+sourceName
            if parentFolder+"_json" in folders:
                return parentFolder+r"_json."+sourceName
            elif "common_json" in folders:
                return r"common_json."+sourceName
            else:
                fd = folders[0]
                if fd is None:
                    return sourceName
                else:
                    return fd+r"."+sourceName
        else:
            print "--------------------------------------------"
            print u"找不到图片: {}".format(sourceName.replace(r"_png",r".png"))
            print "--------------------------------------------"
            return sourceName
    except Exception,e:
        print "--------------------------------------------"
        print u"智能寻找贴图错误: " + e.message
        print "--------------------------------------------"
        return sourceName

def main(argv):
    global psdDir
    global imgDir
    global skinDir
    global resFile
    global genImg
    global intelligent
    global force
    global genFontImg
    global currentPsdFile
    try:
        opts, args = getopt.getopt(argv, "p:i:s:r:", ["psdDir=", "imgDir=","skinDir=","genImg","genFontImg","resFile=","intelligent","force"])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'convertPsd -p <psdDir> -s <skinDir>    -i <imgDir> --genImg --genFontImg   -r resFile --intelligent --force'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'convertPsd -p <psdDir> -s <skinDir>    -i <imgDir> --genImg --genFontImg   -r resFile --intelligent --force'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-p", "--psdDir"):
            psdDir = arg
        elif opt in ("-i", "--imgDir"):
            imgDir = arg
        elif opt in ("-s", "--skinDir"):
            skinDir = arg
        elif opt in ("-r", "--resFile"):
            resFile = arg
        elif opt in ("--genImg",):
            genImg = True
        elif opt in ("--intelligent",):
            intelligent = True
        elif opt in ("--force",):
            force = True
        elif opt in ("--genFontImg",):
            genFontImg = True

    #psdDir = r"C:\work\N5\roll\psd"
    if intelligent:
        parseResourceFile()
    try:
        parse()
    except Exception,e:
        print u"解析psd失败：" + currentPsdFile
        print e.message

def main2():
    '''
    not use, for debug
    :return:
    '''
    #psd = PSDImage.load(r'C:\Users\Administrator\Desktop\test.psd')

    #print getLayerStroke(psd.layers[4])
    global absPsdDir
    dir = r"E:\study\code\EgretProjects\psd\common"
    absPsdDir = os.path.abspath(dir)
    parseDir([])
    #print psd
    # getAttrs(psd.layers[2])
    # for layer in psd.layers:
    #     print isLayerLocked(layer)

if __name__ == '__main__':
    #main2()
    main(sys.argv[1:])
