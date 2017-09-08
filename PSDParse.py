#-.-coding:utf-8

# author: talus
# date: 2017/09/03
# email: talus_wang@sina.com

import os
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


