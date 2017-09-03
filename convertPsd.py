#-.-coding:utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import getopt
import json
from psd_tools import PSDImage,Group,Layer

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
        print "{} already exists, ignore......".format(u"{}Skin.exml".format(name))
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
        print u"解析 PSD 失败:  {}".format(fileName)

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
    #         if isinstance(layer,Group) and hasattr(layer,"name") and layer.name.startswith(r"$Skin"):
    #             continue
    #         if isinstance(layer,Layer) and layer.text_data is not None:
    #             print u"生成文字图片：" + u"txt_{}.png".format(layer.name)
    #             pngFile = os.path.join(dir,u"txt_{}.png".format(layer.name))
    #             if os.path.exists(pngFile):
    #                 os.unlink(pngFile)
    #             layer_image = layer.as_PIL()
    #             layer_image.save(pngFile)


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
        print u"解析图层组[ " + layer.name + u" ]错误：  " + e.message
        return 0,0,0,0

#解析skinGroup
def parseSkinGroup(group,depth,depthPath,root=False):
    name = group.name[1:]
    nameList = name.split(r"_")
    id = nameList[1]
    x,y,width,height = getDimension(group)
    prefix = depth * u"    "
    content = u""
    content += u"{}<e:Panel ".format(prefix)
    content += u'x="{}" '.format(x)
    content += u'y="{}" '.format(y)
    content += u'width="{}" '.format(width)
    content += u'height="{}" '.format(height)
    content += u'skinName="{}" '.format(id + "Skin")
    content += u'/>'
    content += u'\n'
    return content


#解析其他命名group，扩展group的功能，允许自定义
def parseCommonGroup(group,depth,depthPath,root=False):
    name = group.name[1:]
    nameList = name.split(r"_")
    cls = nameList[0]
    id = nameList[1]
    x, y, width, height = getDimension(group)
    prefix = depth * u"    "
    content = u""
    content += u"{0}<n:{1} ".format(prefix,cls)
    content += u'id="{}" '.format(id)
    content += u'x="{}" '.format(x)
    content += u'y="{}" '.format(y)
    content += u'width="{}" '.format(width)
    content += u'height="{}" '.format(height)
    content += u'/>'
    content += u'\n'
    return content

#解析特殊的图层组，根据命名规则，生成对应的信息
def parseSpecialGroup(group,depth,depthPath,root=False):
    name = group.name[1:]
    nameList = name.split(r"_")
    if len(nameList) == 2:
        cls = nameList[0]
        if cls == "Skin":
            return parseSkinGroup(group,depth,depthPath,root)
        else:
            return parseCommonGroup(group,depth,depthPath,root)
    else:
        raise ValueError(u"图层组命名错误:  " + name)
    return ""

#解析psd图层组
def parseGroup(group,depth,depthPath,root=False):
    assert isinstance(group,Group) or isinstance(group,PSDImage)
    if hasattr(group,"name"):
        if root == False and group.name.startswith(r"$"):
            return parseSpecialGroup(group,depth,depthPath,root)

    content = u""
    prefix = depth * u"    "
    if root == False:
        content += u'{}<e:Group x="0" y="0" width="100%" height="100%">'.format(prefix)
        content += u'\n'
    layers = group.layers
    layers.reverse()
    for layer in layers:
        if isinstance(layer,Layer):
            content += parseLayer(layer,depth+1,depthPath[:])
        elif isinstance(layer,Group):
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
    name = layer.name
    x,y,width,height = getDimension(layer)
    visible = layer.visible
    alpha = 1 if layer.opacity != 255 else layer.opacity / 255

    if isLabel:
        content += u'{}<e:Label '.format(prefix)
        content += u'x="{}" '.format(x)
        content += u'y="{}" '.format(y)
        content += u'fontFamily="Microsoft YaHei" '
        content += u'text="{}" '.format(name)
        if not visible:
            content += u'visible="false" '
        if alpha != 1:
            content += u'alpha="{}" '.format(alpha)
        content += u'/>'
    else:
        content += u'{}<e:Image '.format(prefix)
        content += u'x="{}" '.format(x)
        content += u'y="{}" '.format(y)
        content += u'width="{}" '.format(width)
        content += u'height="{}" '.format(height)
        if not visible:
            content += u'visible="false" '
        if alpha != 1:
            content += u'alpha="{}" '.format(alpha)
        src = r"{}_png".format(name)
        if intelligent:
            length = len(depthPath)
            if length > 0:
                parentFolder = depthPath[length-1]
                src = getIntelligentSource(src,parentFolder)
        content += u'source="{}" '.format(src)
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
            print u"解析default.res.json文件 failed......"
            print e.message
    else:
        print u'无法找到default.res.json文件 ......'

#智能选择图片的最优source，减少drawcall
def getIntelligentSource(sourceName,parentFolder):
    global resNameMap
    try:
        if resNameMap.has_key(sourceName):
            folders = resNameMap[sourceName]
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
            print u"找不到图片: {}".format(sourceName.replace(r"_png",r".png"))
            return sourceName
    except Exception,e:
        print u"智能寻找贴图错误: " + e.message
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
    try:
        opts, args = getopt.getopt(argv, "p:i:s:r:", ["psdDir=", "imgDir=","skinDir=","genImg","genFontImg","resFile=","intelligent","force"])
    except getopt.GetoptError:
        print 'usage python convertPsd.py -p <psdDir> -s <skinDir>    -i <imgDir> --genImg --genFontImg   -r resFile --intelligent --force'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'usage python convertPsd.py -p <psdDir> -s <skinDir>    -i <imgDir> --genImg --genFontImg   -r resFile --intelligent --force'
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

    if intelligent:
        parseResourceFile()
    parse()

def main2():
    '''
    not use, for debug
    :return:
    '''
    psd = PSDImage.load(r'E:\study\code\EgretProjects\psd\common\test1.psd')

    print psd

if __name__ == '__main__':
    #main2()
    main(sys.argv[1:])
