#-.-coding:utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import getopt
from psd_tools import PSDImage,Group,Layer

psdDir = ""
imgDir = ""
skinDir = ""

absPsdDir = ""
absImgDir = ""
absSkinDir = ""

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
    name,ext = getNameAndExt(fileName)
    content = u""
    content += u"<?xml version='1.0' encoding='utf-8'?>"
    content += u'\n'
    psd = PSDImage.load(os.path.join(os.path.join(absPsdDir,*depthPath),fileName))
    content += u'<e:Skin class="{}" width="{}" height="{}" xmlns:e="http://ns.egret.com/eui" xmlns:w="http://ns.egret.com/wing">'.format(name+"Skin",psd.header.width,psd.header.height)
    content += u'\n'
    content += parseGroup(psd,0,depthPath[:],True)
    content += u'</e:Skin>'

    exmlDir = os.path.join(absSkinDir,*depthPath)
    exmlFile = os.path.join(exmlDir,u"{}Skin.exml".format(name))
    if os.path.exists(exmlFile):
        os.unlink(exmlFile)
    if not os.path.exists(exmlDir):
        os.makedirs(exmlDir)

    try:
        with open(exmlFile, mode="w+") as f:
            f.write(content)
            print "parse PSD success: {}".format(fileName)
    except Exception,e:
        print "parse PSD failed:  {}".format(fileName)

    getImages(psd,depthPath[:])

def getImages(psd,depthPath):
    assert isinstance(psd,PSDImage)
    global absImgDir
    for emd in psd.embedded:
        filename = emd.filename
        data = emd.data
        dir = os.path.join(absImgDir,*depthPath)
        imgFile = os.path.join(dir,filename)
        if os.path.exists(imgFile):
            os.unlink(imgFile)
        if not os.path.exists(dir):
            os.makedirs(dir)
        try:
            with open(imgFile,mode="wb") as f:
                f.write(data)
        except Exception,e:
            pass


def parseGroup(group,depth,depthPath,root=False):
    assert isinstance(group,Group) or isinstance(group,PSDImage)
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

def parseLayer(layer,depth,depthPath):
    assert isinstance(layer,Layer)
    global absImgDir
    content = u""
    prefix = depth * u"    "
    isLabel = True if layer.text_data is not None else False
    name = layer.name
    box = layer.transform_bbox or layer.bbox
    x = box.x1
    y = box.y1
    width = box.width
    height = box.height
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
        content += u'source="{}" '.format(r"{}_png".format(name))
        content += u'/>'
    content += u'\n'


    # pngDir = os.path.join(absImgDir,*depthPath)
    # pngFile = os.path.join(pngDir,u"{}.png".format(name))
    # print "pngFile:  " + pngFile
    # if os.path.exists(pngFile):
    #     os.unlink(pngFile)
    # if not os.path.exists(pngDir):
    #     os.makedirs(pngDir)
    #
    # if not isLabel:
    #     layer_image = layer.as_PIL()
    #     layer_image.save(pngFile)

    return content

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




def main(argv):
    global psdDir
    global imgDir
    global skinDir
    try:
        opts, args = getopt.getopt(argv, "p:i:s::", ["psdDir=", "imgDir=","skinDir="])
    except getopt.GetoptError:
        print 'usage python convertPsd.py -p <psdDir> -i <imgDir> -s <skinDir>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'usage python convertPsd.py -p <psdDir> -i <imgDir> -s <skinDir>'
            sys.exit(2)
        elif opt in ("-p", "--psdDir"):
            psdDir = arg
        elif opt in ("-i", "--imgDir"):
            imgDir = arg
        elif opt in ("-s", "--skinDir"):
            skinDir = arg

    parse()

def main2():
    psd = PSDImage.load('test.psd')

    print psd

if __name__ == '__main__':
    #main2()
    main(sys.argv[1:])
