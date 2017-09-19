#-.-coding:utf-8

# author: talus
# date: 2017/09/03
# email: talus_wang@sina.com

import os
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from psd_tools import PSDImage,Group,Layer

#获得文件的名字和扩展名
def getNameAndExt(fileName):
    list = fileName.split(r".")
    length = len(list)
    ext = list[length - 1]
    name = r".".join(list[0:length-1])
    return name,ext

def rgbToHex(r,g,b):
    r = hex(int(r))[2:]
    g = hex(int(g))[2:]
    b = hex(int(b))[2:]
    r = "0" + r if len(r) < 2 else "" + r
    g = "0" + g if len(g) < 2 else "" + g
    b = "0" + b if len(b) < 2 else "" + b
    return r"0x{}{}{}".format(r, g, b)

def isImage(layer):
    return isinstance(layer,Layer) and layer.text_data is None

def isLabel(layer):
    return isinstance(layer,Layer) and layer.text_data is not None

def isGroup(layer):
    return isinstance(layer,Group)

def getName(layer):
    return layer.name.strip()

def getText(layer):
    return layer.text_data.text if isLabel(layer) else ""

def getLayerStroke(layer):
    assert isLabel(layer)
    try:
        baseEffects = layer._info[13][0][1][2][2]
        strokeEffect = None
        for lst in baseEffects:
            if lst[0] == "FrFX":
                strokeEffect = lst[1]
                break
        if strokeEffect is None:
            return False,0,""
        enabled,size,r,g,b = False,0,0,0,0
        for item in strokeEffect[2]:
            if item[0].strip() == "enab":
                enabled = item[1][0]
            elif item[0].strip() == "Sz":
                size = item[1][1]
            elif item[0].strip() == "Clr":
                colorInfo = item[1][2]
                r = colorInfo[0][1][0]
                g = colorInfo[1][1][0]
                b = colorInfo[2][1][0]
                r = hex(int(r))[2:]
                g = hex(int(g))[2:]
                b = hex(int(b))[2:]
                r = "0" + r if len(r) < 2 else "" + r
                g = "0" + g if len(g) < 2 else "" + g
                b = "0" + b if len(b) < 2 else "" + b

        color = r"0x{}{}{}".format(r, g, b)
        return enabled, size, color
    except:
        return False,0,""

#如果是按钮，设置anchorOffset为中心位置，重新计算x,y坐标
def getCenterPos(x,y,width,height):
    hw = width * 0.5
    hh = height * 0.5
    return x+hw,y+hh

#是否被锁定
def isLayerLocked(layer):
    assert isinstance(layer,Layer) or isinstance(layer,Group)
    return layer._info[9][0]

#获得图层或图层组的尺寸信息
def getDimension(layer):
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
        print "--------------------------------------------"
        print u"解析图层组[ " + layer.name + u" ]错误：  " + e.message
        print "--------------------------------------------"
        return 0,0,0,0

def getVisible(layer):
    return layer.visible

def getOpacity(layer):
    return layer.opacity / 255

def getPsdSize(psd):
    assert isinstance(psd,PSDImage)
    return psd.header.width,psd.header.height

def genImages(psd,dir):
    assert isinstance(psd,PSDImage)
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
                f.close()
                print u"生成图片：  " + imgFile
        except Exception,e:
            pass

def genLabels(psd,dir):
    assert isinstance(psd, PSDImage) or isinstance(psd, Group)
    if not os.path.exists(dir):
        os.makedirs(dir)
    for label in getLabels(psd):
        name = getName(label)
        labelFile = os.path.join(dir,name+r".png")
        if os.path.exists(labelFile):
            os.unlink(labelFile)
        layer_image = label.as_PIL()
        layer_image.save(labelFile)

def getLabels(group):
    assert isinstance(group,PSDImage) or isinstance(group,Group)
    for layer in group.layers:
        if isGroup(layer):
            yield getLabels(layer)
        elif isLabel(layer):
            yield layer
        else:
            continue

def getLabelInfo(label):
    assert isLabel(label)
    info = None
    try:
        #ps的版本不一样。。。。家中电脑的版本
        info = label._tagged_blocks["TySh"][9][2][5][1]["EngineDict"]["StyleRun"]["RunArray"][0]["StyleSheet"]["StyleSheetData"]
        #info = label._tagged_blocks["lfx2"]
    except Exception,e:
        print "getLabelInfo error:  " + e.message
    return info

def getLabelSize(label):
    assert isLabel(label)
    info = getLabelInfo(label)
    if info is not None:
        return info["FontSize"]
    return 18

def getLabelColor(label):
    try:
        assert isLabel(label)
        info = getLabelInfo(label)
        if info is not None:
            colorInfo = info["FillColor"]["Values"]
            a,r,g,b = colorInfo[0],colorInfo[1],colorInfo[2],colorInfo[3]
        else:
            a,r,g,b = 1,0,0,0
        return rgbToHex(round(r*255),round(g*255),round(b*255)),a
    except:
        return "0x000000",1

def getLabelFontFamily(label):
    assert isLabel(label)
    try:
        dr = label._tagged_blocks["TySh"][9][2][5][1]["DocumentResources"]
        fontName = dr["FontSet"][0]["Name"]
        return fontName.split(r"-")[0]
    except Exception,e:
        print "getLabelFontFamily  error:  " + e.message
        return "MicrosoftYaHei"

def getLabelBold(label):
    assert isLabel(label)
    try:
        dr = label._tagged_blocks["TySh"][9][2][5][1]["DocumentResources"]
        fontName = dr["FontSet"][0]["Name"]
        bi = fontName.split(r"-")[1]
        return re.match(r".*Bold.*",bi) is not None
    except Exception,e:
        #print "getLabelBold  error:  " + e.message
        return False

def getLabelItalic(label):
    assert isLabel(label)
    try:
        dr = label._tagged_blocks["TySh"][9][2][5][1]["DocumentResources"]
        fontName = dr["FontSet"][0]["Name"]
        bi = fontName.split(r"-")[1]
        return re.match(r".*Italic.*", bi) is not None
    except Exception, e:
        #print "getLabelItalic  error:  " + e.message
        return False

def getLabelStrokeInfo(label):
    assert isLabel(label)
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
        # return False,0,"0x000000"

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
        return False, 0, "0x000000"

    except Exception,e:
        print "getLabelStrokeInfo error:  " + e.message
        return False,0,"0x000000"


def getListTupleAttr(lst,key):
    for l in lst:
        if l[0].strip() == key:
            return l[1]
    return None


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
    except:
        return None


def main():

    psd = PSDImage.load(r'C:\work\N5\roll\art\psd\main2.psd')
    for layer in psd.layers:
        if isLabel(layer):
            print getLabelSize(layer)
            print getLabelColor(layer)
            print getLabelBold(layer)
            print getLabelItalic(layer)
            print getLabelStrokeInfo(layer)

            TySh = layer._tagged_blocks["TySh"][9][2]
            for tp in TySh:
                if tp[0] == "EngineData":
                    engineData = tp[1][0]
                    break

            print engineData
            print type(engineData)

            lines = engineData.splitlines()
            newLines = []
            for line in lines:
                ln = line.strip()
                if ln == "":
                    continue
                newLines.append(ln)
            print newLines

            print ""

            ed = {}
            stack = [ed]
            for idx,ln in enumerate(newLines):
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
                    stack = stack[0:stackLen-1]
            print ed





if __name__ == '__main__':
    main()

