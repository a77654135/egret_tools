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
import traceback
from psd_tools import PSDImage,Group,Layer
#from PSDParser import getLabelStrokeInfo,getLabelBold,getLabelItalic,getLabelSize,getLabelColor

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

s9gFile = ""
s9gMap = {}

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
    if fileName.startswith("unuse"):
        return
    global absPsdDir
    global absSkinDir
    global force
    global currentPsdFile
    print "parsePsd:   " + fileName

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
        print u"解析 PSD 失败:  {}   {}".format(fileName,e.message)
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
            raise e
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

#解析属性 名字：属性名=属性值;属性名=属性值;属性名=属性值
def getAttrs(layer):
    assert isinstance(layer,Layer) or isinstance(layer,Group)
    ret = {}
    try:
        if layer.name:
            lst = layer.name.strip().split(r":")
            # if len(lst) <= 1:
            #     return ret
            name = lst[0].split(" ")[0].strip()
            #print name
            ret["clsName"] = name[1:] if name.startswith(r"$") else name
            if len(lst) > 1:
                attrs = lst[1].strip().split(" ")[0].strip()
                if attrs.endswith(r";"):
                    attrs = attrs.rstrip(r";")
                for attr in attrs.split(r";"):
                    k,v = attr.split(r"=")
                    #print k,v
                    ret[k] = v
            return ret
        else:
            return None
    except Exception,e:
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

#name:green_btn_png or green_btn
def getS9Info(name):
    global s9gMap
    name = name.replace("_png","")
    if s9gMap.has_key(name):
        return s9gMap[name]
    return None

#生成信息
def genContent(layer,clz,otherAttr,depth,isButton=False,depthPath=[]):
    assert isinstance(layer,Layer) or isinstance(layer,Group)
    attrs = getAttrs(layer)
    if attrs is None:
        return ""

    x, y, width, height = getDimension(layer)
    if isButton:
        #assert len(layer.layers) > 0
        #x,y,width,height = getDimension(layer.layers[0])
        x,y = getCenterPos(x,y,width,height)
    oldAttrs = {
        "width": width,
        "height": height
    }
    if x:
        oldAttrs["x"] = x
    if y:
        oldAttrs["y"] = y
    if isButton:
        oldAttrs["anchorOffsetX"] = int(width * 0.5)
        oldAttrs["anchorOffsetY"] = int(height * 0.5)
        oldAttrs["touchChildren"] = "false"
        oldAttrs["touchEnabled"] = "true"

    newAttrs = mergeAttr(oldAttrs, otherAttr)
    newAttrs = mergeAttr(newAttrs,attrs)
    if newAttrs.has_key("width") and type(newAttrs["width"]) == float:
        newAttrs["width"] = int(newAttrs["width"])
    if newAttrs.has_key("height") and type(newAttrs["height"]) == float:
        newAttrs["height"] = int(newAttrs["height"])

    prefix = depth * u"    "
    content = u""

    if isButton:
        if len(layer.layers) == 1:
            content += u"{0}<{1} ".format(prefix, "n:SimpleButton")

            if newAttrs.has_key("x"):
                content += u'{0}="{1}" '.format("x", int(newAttrs["x"]))
            if newAttrs.has_key("y"):
                content += u'{0}="{1}" '.format("y", int(newAttrs["y"]))
            if newAttrs.has_key("width"):
                content += u'{0}="{1}" '.format("width", newAttrs["width"])
            if newAttrs.has_key("height"):
                content += u'{0}="{1}" '.format("height", newAttrs["height"])
            if newAttrs.has_key("id"):
                content += u'{0}="{1}" '.format("id", newAttrs["id"])
            if newAttrs.has_key("name"):
                content += u'{0}="{1}" '.format("name", newAttrs["name"])
            if newAttrs.has_key("anchorOffsetX"):
                content += u'{0}="{1}" '.format("anchorOffsetX", int(newAttrs["anchorOffsetX"]))
            if newAttrs.has_key("anchorOffsetY"):
                content += u'{0}="{1}" '.format("anchorOffsetY", int(newAttrs["anchorOffsetY"]))
            if newAttrs.has_key("bgSource"):
                content += u'{0}="{1}" '.format("source", newAttrs["bgSource"])
            content += u'/>'
        else:
            content += u"{0}<{1} ".format(prefix, clz)

            if newAttrs.has_key("x"):
                content += u'{0}="{1}" '.format("x", int(newAttrs["x"]))
            if newAttrs.has_key("y"):
                content += u'{0}="{1}" '.format("y", int(newAttrs["y"]))
            if newAttrs.has_key("width"):
                content += u'{0}="{1}" '.format("width", newAttrs["width"])
            if newAttrs.has_key("height"):
                content += u'{0}="{1}" '.format("height", newAttrs["height"])
            if newAttrs.has_key("id"):
                content += u'{0}="{1}" '.format("id", newAttrs["id"])
            if newAttrs.has_key("name"):
                content += u'{0}="{1}" '.format("name", newAttrs["name"])

            for k, v in newAttrs.iteritems():
                if k == "clsName":
                    continue
                if k in ("x", "y", "width", "height", "id", "name"):
                    continue
                content += u'{0}="{1}" '.format(k, v)
            content += u">\n"

            content += u"{}<e:skinName><e:Skin>\n".format(prefix * 2)

            bx, by, bw, bh = 0, 0, 0, 0
            layers = layer.layers
            layers.reverse()
            for idx, ly in enumerate(layers):
                if idx == 0:
                    bx, by, bw, bh = getDimension(ly)
                    src = getLayerSrc(ly, depthPath[:])
                    s9Info = getS9Info(src)
                    x, y, width, height = getDimension(ly)
                    content += u'{}<e:Image width="{}" height="{}" id="{}" source="{}" '.format(prefix * 3, width,
                                                                                                height, "bg", src)
                    if s9Info is not None:
                        content += u'scale9Grid="{}" />\n'.format(s9Info)
                    else:
                        content += u'/>\n'
                else:
                    if isLayerLocked(ly):
                        # 图层被锁定，不解析
                        continue
                    if isinstance(ly, Layer):
                        content += parseLayer(ly, depth + 2, depthPath[:], [bx, by])

            # if otherAttr.has_key("bgSource"):
            #     src = otherAttr["bgSource"]
            #     s9Info = getS9Info(src)
            #     #print "src:  {}   info:{}  ".format(src,s9Info)
            #     if s9Info is not None:
            #         content += u'{}<e:Image id="{}" width="100%" height="100%" source="{}" scale9Grid="{}" />\n'.format(prefix * 3, "bg",src,s9Info)
            #     else:
            #         content += u'{}<e:Image id="{}" width="100%" height="100%" source="{}"/>\n'.format(prefix * 3, "bg",src)
            # if otherAttr.has_key("iconSource"):
            #     src = otherAttr["iconSource"]
            #     s9Info = getS9Info(src)
            #     #print "src:  {}   info:{}  ".format(src, s9Info)
            #     if s9Info is not None:
            #         content += u'{}<e:Image id="{}" horizontalCenter="0" verticalCenter="0" source="{}" scale9Grid="{}" />\n'.format(prefix * 3, "icon",src,s9Info)
            #     else:
            #         content += u'{}<e:Image id="{}" horizontalCenter="0" verticalCenter="0" source="{}"/>\n'.format(prefix * 3, "icon", src)

            content += u'{}</e:Skin></e:skinName>\n'.format(prefix * 2)
            content += u"{}</{}>".format(prefix, clz)
    else:
        content += u"{0}<{1} ".format(prefix, clz)

        if newAttrs.has_key("x"):
            content += u'{0}="{1}" '.format("x", int(newAttrs["x"]))
        if newAttrs.has_key("y"):
            content += u'{0}="{1}" '.format("y", int(newAttrs["y"]))
        if newAttrs.has_key("width"):
            content += u'{0}="{1}" '.format("width", newAttrs["width"])
        if newAttrs.has_key("height"):
            content += u'{0}="{1}" '.format("height", newAttrs["height"])
        if newAttrs.has_key("id"):
            content += u'{0}="{1}" '.format("id", newAttrs["id"])
        if newAttrs.has_key("name"):
            content += u'{0}="{1}" '.format("name", newAttrs["name"])

        for k, v in newAttrs.iteritems():
            if k == "clsName":
                continue
            if k in ("x","y","width","height","id","name"):
                continue
            content += u'{0}="{1}" '.format(k, v)
        content += u'/>'
    content += u'\n'
    return content


#解析skinGroup
def parseSkinGroup(group,depth,depthPath,root=False):
    layer = group.layers[0]
    nm = layer.name.strip().split(" ")[0]
    x, y, width, height = getDimension(layer)

    otherAttr = {
        "skinName": nm + "Skin",
        "width": width,
        "height": height
    }
    if x:
        otherAttr["x"] = x
    if y:
        otherAttr["y"] = y
    return genContent(group,r"e:Panel",otherAttr,depth)

#解析其他命名group，扩展group的功能，允许自定义
def parseCommonGroup(group,depth,depthPath,root=False):
    attrs = getAttrs(group)
    alpha = 1 if group.opacity == 255 else group.opacity / 255.0
    if alpha != 1:
        attrs["alpha"] = alpha
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
    global intelligent
    global currentPsdFile
    names = layer.name.strip().split(r":")
    src = r"{}_png".format(names[0].split(" ")[0])
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
    return int(x+hw),int(y+hh)

#解析特殊的图层组，根据命名规则，生成对应的信息
def parseButtonGroup(group,depth,depthPath,root=False):
    assert isinstance(group,Group)
    cls = r"n:BaseButton"
    otherAttr = {
        "touchChildren":'false',
        "touchEnabled":'true'
    }
    alpha = 1 if group.opacity == 255 else group.opacity / 255.0
    if alpha != 1:
        otherAttr["alpha"] = alpha
    layers = group.layers
    length = len(layers)
    attrs = getAttrs(group)
    if attrs.has_key("id"):
        otherAttr["name"] = attrs["id"]
    # otherAttr["skinName"] = "SimpleButtonSkin"
    if length > 0:
        bgLayer = layers[length-1]
        src = getLayerSrc(bgLayer, depthPath)
        otherAttr["bgSource"] = src

    # if length == 1:
    #     otherAttr["skinName"] = "SimpleButtonSkin"
    #     layer = layers[0]
    #     src = getLayerSrc(layer,depthPath)
    #     otherAttr["bgSource"] = src
    # elif length > 1:
    #     #bgLayer = getLayerById(group,"bg")
    #     #iconLayer = getLayerById(group,"icon")
    #     bgLayer = group.layers[1]
    #     iconLayer = group.layers[0]
    #     if bgLayer is not None and iconLayer is not None:
    #         otherAttr["skinName"] = "IconButtonSkin"
    #     if bgLayer is not None:
    #         bgSrc = getLayerSrc(bgLayer,depthPath)
    #         otherAttr["bgSource"] = bgSrc
    #     if iconLayer is not None:
    #         iconSrc = getLayerSrc(iconLayer,depthPath)
    #         otherAttr["iconSource"] = iconSrc
    return genContent(group,cls,otherAttr,depth,True,depthPath)


#解析龙骨图层组，根据命名规则，生成对应的信息
def parseBoneGroup(group,depth,depthPath,root=False):
    content = u""
    content += u'{}<e:Group y="0" height="100%" width="100%" touchEnabled="false" x="0" touchChildren="false" >\n'.format(depth * u"    ")
    gropAttrs = getAttrs(group)
    alpha = 1 if group.opacity == 255 else group.opacity / 255.0
    if alpha != 1:
        gropAttrs["alpha"] = alpha
    for layer in group.layers:
        #龙骨的名字
        name = layer.name.strip().split(":")[0].split(" ")[0].replace("_tex","").strip()
        # name = layer.name.strip().split(" ")[0].replace("_tex","")
        x,y,_,__ = getDimension(layer)
        layerAttrs = getAttrs(layer)
        attrs = mergeAttr(gropAttrs,layerAttrs)
        content += u'{}<n:BaseBoneComponent x="{}" y="{}" boneName="{}" '.format(((depth + 1)* u"    "),x,y,name)

        for k,v in attrs.iteritems():
            if k == "clsName":
                continue
            content += u'{0}="{1}" '.format(k,v)
        content += u'/>\n'

    content += u'{}</e:Group>\n'.format(depth * u"    ")
    return content

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
    elif cls == "Bone":
        return parseBoneGroup(group, depth, depthPath, root)
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
        if group.name.strip().startswith(r"$"):
            return parseSpecialGroup(group,depth,depthPath)
    # if not root:
    #     print "parseGroup:  " + group.name
    content = u""
    prefix = depth * u"    "
    if root == False:
        oldAttrs = {
            "width": "100%",
            "height": "100%",
            "touchEnabled":"false",
            "touchChildren":"true"
        }
        alpha = 1 if group.opacity == 255 else group.opacity / 255.0
        if alpha != 1:
            oldAttrs["alpha"] = alpha
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
            content += parseGroup(layer,depth+1,depthPath[:])
    if root == False:
        content += u'{}</e:Group>'.format(prefix)
        content += u'\n'
    return content

#解析psd图层
def parseLayer(layer,depth,depthPath,offset=[0,0]):
    assert isinstance(layer,Layer)
    global absImgDir
    global intelligent
    global genImg
    global genFontImg
    global currentPsdFile
    global s9gMap

    content = u""
    prefix = depth * u"    "
    isLabel = True if layer.text_data is not None else False
    name = layer.name.strip().split(":")[0].strip().split(" ")[0].strip()
    #print "parseLayer:  " + name
    #name = layer.name.strip().split(" ")[0]
    x,y,width,height = getDimension(layer)
    visible = layer.visible

    oldAttrs = {
        "x":x - offset[0],
        "y":y - offset[1],
        "width":width,
        "height":height,
        "touchEnabled":"false"
    }
    if not visible:
        oldAttrs["visible"] = "false"
    alpha = 1 if layer.opacity == 255 else layer.opacity / 255.0
    if alpha != 1:
        oldAttrs["alpha"] = alpha
    if isLabel:
        oldAttrs["fontFamily"] = "Microsoft YaHei"
        oldAttrs["text"] = layer.text_data.text
        #print layer.text_data.text
        se,sz,sc = getLabelStrokeInfo(layer)
        if se:
            oldAttrs["stroke"] = int(sz)
            oldAttrs["strokeColor"] = sc
        # if getLabelBold(layer):
        #     oldAttrs["bold"] = "true"
        # if getLabelItalic(layer):
        #     oldAttrs["italic"] = "true"
        oldAttrs["size"] = getLabelSize(layer)
        color,alpha = getLabelColor(layer)
        oldAttrs["textColor"] = color
        if float(alpha) != float(1):
            oldAttrs["alpha"] = alpha
    else:
        src = r"{}_png".format(name)
        if intelligent:
            length = len(depthPath)
            if length > 0:
                parentFolder = depthPath[length - 1]
                src = getIntelligentSource(src, parentFolder)
        oldAttrs["source"] = src
        if s9gMap.has_key(name):
            oldAttrs["scale9Grid"] = s9gMap[name]

    attrs = getAttrs(layer)
    newAttrs = mergeAttr(oldAttrs, attrs)
    # print type(newAttrs["width"])
    if newAttrs.has_key("width") and type(newAttrs["width"]) == float:
        newAttrs["width"] = int(newAttrs["width"])
    if newAttrs.has_key("height") and type(newAttrs["height"]) == float:
        newAttrs["height"] = int(newAttrs["height"])


    if isLabel:
        content += u'{}<e:Label '.format(prefix)

        if newAttrs.has_key("x"):
            content += u'{0}="{1}" '.format("x", int(newAttrs["x"]))
        if newAttrs.has_key("y"):
            content += u'{0}="{1}" '.format("y", int(newAttrs["y"]))
        if newAttrs.has_key("width"):
            content += u'{0}="{1}" '.format("width", newAttrs["width"])
        if newAttrs.has_key("height"):
            content += u'{0}="{1}" '.format("height", newAttrs["height"])
        if newAttrs.has_key("id"):
            content += u'{0}="{1}" '.format("id", newAttrs["id"])
        if newAttrs.has_key("name"):
            content += u'{0}="{1}" '.format("name", newAttrs["name"])

        for k,v in newAttrs.iteritems():
            if k == "clsName":
                continue
            if k in ("x","y","width","height","id","name"):
                continue
            content += u'{0}="{1}" '.format(k,v)
        content += u'/>'
    else:
        content += u'{}<e:Image '.format(prefix)

        if newAttrs.has_key("x"):
            content += u'{0}="{1}" '.format("x", int(newAttrs["x"]))
        if newAttrs.has_key("y"):
            content += u'{0}="{1}" '.format("y", int(newAttrs["y"]))
        if newAttrs.has_key("width"):
            content += u'{0}="{1}" '.format("width", newAttrs["width"])
        if newAttrs.has_key("height"):
            content += u'{0}="{1}" '.format("height", newAttrs["height"])
        if newAttrs.has_key("id"):
            content += u'{0}="{1}" '.format("id", newAttrs["id"])
        if newAttrs.has_key("name"):
            content += u'{0}="{1}" '.format("name", newAttrs["name"])

        for k,v in newAttrs.iteritems():
            if k == "clsName":
                continue
            if k in ("x","y","width","height","id","name"):
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
    #print "parsedir:   " + depthPath
    global absPsdDir
    dir = os.path.join(absPsdDir,*depthPath)
    for f in os.listdir(dir):
        absFile = os.path.join(dir,f)
        try:
            if os.path.isdir(absFile):
                dpt = depthPath[:]
                dpt.append(f)
                parseDir(dpt)
            elif os.path.isfile(absFile):
                name, ext = getNameAndExt(f)
                if ext == "psd":
                    dpt = depthPath[:]
                    parsePsd(f,dpt)
        except Exception,e:
            print "parseDir error:  " + e.message
            print traceback.print_exc()
            continue

def parse():
    global psdDir
    global imgDir
    global skinDir

    global absPsdDir
    global absImgDir
    global absSkinDir

    #print "parse.............."

    absPsdDir = os.path.abspath(psdDir)
    absImgDir = os.path.abspath(imgDir)
    absSkinDir = os.path.abspath(skinDir)
    #print "1111111111111111111111111"
    #print absPsdDir
    for f in os.listdir(absPsdDir):
        absFile = os.path.join(absPsdDir,f)
        #print absFile
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
    global s9gFile
    try:
        opts, args = getopt.getopt(argv, "p:i:s:r:", ["psdDir=", "imgDir=","skinDir=","genImg","genFontImg","resFile=","s9=","intelligent","force"])
    except getopt.GetoptError:
        print "--------------------------------------------"
        #print 'convertPsd -p <psdDir> -s <skinDir>    -i <imgDir> --genImg --genFontImg   -r resFile --intelligent --force'
        print 'convertPsd -p <psdDir> -s <skinDir>'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'convertPsd -p <psdDir> -s <skinDir>'
            #print 'convertPsd -p <psdDir> -s <skinDir>    -i <imgDir> --genImg --genFontImg   -r resFile --intelligent --force'
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
        elif opt in ("--s9",):
            s9gFile = arg

    #psdDir = r"C:\work\N5\roll\psd"
    if intelligent:
        parseResourceFile()
    if s9gFile != "":
        parseS9File()

    try:
        parse()
    except Exception,e:
        print u"解析psd失败：" + currentPsdFile
        print e.message
        print traceback.print_exc()

def parseList(lst):
    hasKh = False
    for l in lst:
        if l.strip() == r"[" or l.strip() == r"]":
            hasKh = True
            break
    if hasKh:
        nl = []
        inKh = False
        for l in lst:
            if l.strip() == r"[" and inKh == False:
                inKh = True
                continue
            if inKh and l.strip() == r"]":
                inKh = False
                break
            if inKh:
                nl.append(l)
        return nl
    else:
        return " ".join(lst)

def parseEngineData(layer):
    try:
        TySh = layer._tagged_blocks["TySh"][9][2]
        for tp in TySh:
            if tp[0] == "EngineData":
                engineData = tp[1][0]
                break
        if isinstance(engineData,str) and engineData != "":
            lines = engineData.splitlines()
            newLines = []
            for line in lines:
                ln = line.strip()
                if ln == "":
                    continue
                newLines.append(ln)

            ed = {}
            stack = [ed]
            for idx, ln in enumerate(newLines):
                stackLen = len(stack)
                if stackLen <= 0:
                    break
                lastData = stack[stackLen - 1]

                if ln == "<<":
                    continue
                if ln.startswith(r"/") and len(ln.split(r" ")) == 1 and newLines[idx + 1] == "<<":
                    key = ln.lstrip(r"/")
                    data = {}
                    lastData[key] = data
                    stack.append(data)
                if ln.startswith(r"/") and len(ln.split(r" ")) > 1:
                    lnlen = len(ln)
                    if ln[lnlen - 1] == r"[":
                        key = ln.lstrip(r"/")
                        key = key.rstrip(r" [")
                        data = {}
                        lastData[key] = data
                        stack.append(data)
                        continue
                    attrs = ln.split(r" ")
                    key = attrs[0].lstrip(r"/")
                    value = parseList(attrs[1:])
                    lastData[key] = value
                if ln == ">>":
                    stack = stack[0:stackLen - 1]
            return ed
        else:
            return None
    except Exception,e:
        #print "parseEngineData error: " + e.message
        return None

def rgbToHex(r,g,b):
    r = hex(int(r))[2:]
    g = hex(int(g))[2:]
    b = hex(int(b))[2:]
    r = "0" + r if len(r) < 2 else "" + r
    g = "0" + g if len(g) < 2 else "" + g
    b = "0" + b if len(b) < 2 else "" + b
    return r"0x{}{}{}".format(r, g, b)

def getLabelSize(label):
    assert isinstance(label,Layer) and label.text_data is not None
    try:
        ed = parseEngineData(label)
        if ed is None:
            return 18
        else:
            return int(ed["EngineDict"]["StyleRun"]["RunArray"]["StyleSheet"]["StyleSheetData"]["FontSize"])
    except Exception,e:
        #print "getLabelSize error: " + e.message
        return 18

# def getLabelBold(label):
#     assert isinstance(label) and label.text_data is not None

def getLabelColor(label):
    assert isinstance(label,Layer) and label.text_data is not None
    try:
        ed = parseEngineData(label)
        if ed is None:
            return "0xffffff", 1
        else:
            colorInfo = ed["EngineDict"]["StyleRun"]["RunArray"]["StyleSheet"]["StyleSheetData"]["FillColor"]["Values"]
            a, r, g, b = colorInfo[0], colorInfo[1], colorInfo[2], colorInfo[3]
            return rgbToHex(round(float(r) * 255), round(float(g) * 255), round(float(b) * 255)), a
    except Exception,e:
        #print "getLabelColor error: " + e.message
        return "0xffffff", 1
    # try:
    #     assert isLabel(label)
    #     info = getLabelInfo(label)
    #     if info is not None:
    #         colorInfo = info["FillColor"]["Values"]
    #         a,r,g,b = colorInfo[0],colorInfo[1],colorInfo[2],colorInfo[3]
    #     else:
    #         a,r,g,b = 1,0,0,0
    #     return rgbToHex(round(r*255),round(g*255),round(b*255)),a
    # except:
    #     return "0xffffff",1

def getLabelStrokeInfo(label):
    assert isinstance(label,Layer) and label.text_data is not None
    try:
        #家里ps的版本

        # info = label._tagged_blocks["lfx2"][2][2]
        # for item in info:
        #     if item[0] == "FrFX":
        #         strokeInfo = item[1][2]
        #         enabled = strokeInfo[0][1][0]
        #         size = strokeInfo[5][1][1]
        #         clr = strokeInfo[6][1][2]
        #         r,g,b = clr[0][1][0],clr[1][1][0],clr[2][1][0]
        #         #print enabled,size,r
        #         return enabled,size,rgbToHex(round(r),round(g),round(b))
        # return False,0,"0xffffff"

        #公司的ps版本
        info = label._tagged_blocks["lfx2"][2][2]
        for item in info:
            if item[0] == "FrFX":
                frfx = item[1][2]
                enabled = getListTupleAttr(frfx,"enab")[0] if getListTupleAttr(frfx,"enab") is not None else False
                size = getListTupleAttr(frfx,"Sz")[1] if getListTupleAttr(frfx,"Sz") is not None else 0
                clr = getListTupleAttr(frfx,"Clr")[2]
                if clr is not None:
                    r, g, b = clr[0][1][0], clr[1][1][0], clr[2][1][0]
                else:
                    r,g,b, = 0,0,0
                return enabled, size, rgbToHex(round(r), round(g), round(b))
        return False, 0, "0xffffff"

    except Exception,e:
        #print "getLabelStrokeInfo error:  " + e.message
        return False,0,"0xffffff"

def getListTupleAttr(lst,key):
    for l in lst:
        if l[0].strip() == key:
            return l[1]
    return None

def parseS9File():
    global s9gFile
    global s9gMap

    absS9File = os.path.abspath(s9gFile)

    if os.path.exists(absS9File):
        try:
            with open(absS9File,mode='r') as f:
                s9gMap = json.load(f,encoding="utf-8")
            #print u"解析 .9 文件 success......"
        except Exception,e:
            print "--------------------------------------------"
            print u"解析 .9 文件 failed......"
            print e.message
            print "--------------------------------------------"
    else:
        print "--------------------------------------------"
        print u'无法找到 .9 文件 ......'
        print "--------------------------------------------"

def main2():
    '''
    not use, for debug
    :return:
    '''
    #psd = PSDImage.load(r'C:\work\N5\roll\art\main2.psd')

    #print getLayerStroke(psd.layers[4])
    global absPsdDir
    global absSkinDir
    #dir = r"F:\work\n5\roll\art\testPsd"
    dir = r"F:\work\n5\roll\art\psd\city"
    absPsdDir = os.path.abspath(dir)
    absSkinDir = absPsdDir
    parseDir([])
    #print psd
    # getAttrs(psd.layers[2])
    # for layer in psd.layers:
    #     print isLayerLocked(layer)

if __name__ == '__main__':
    #main2()
    main(sys.argv[1:])
