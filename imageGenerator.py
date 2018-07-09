#-.-coding:utf-8

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import getopt
import xml.sax
import re
import json
import datetime
from PIL import Image
import traceback

# img = Image.open("img.png",mode="r")
# r,g,b,a = img.split()
# pixel = img.getpixel((20,20))
# print r,g,b,a
#
# width,height = img.width,img.height
# img1 = Image.new("RGBA",(width,height),(0,0,0,0))
# for x in range(0,width):
#     for y in range(0,height):
#         pixel = img.getpixel((x,y))
#         if not pixel[3]:
#             continue
#         newPixel = (pixel[0] + 100,pixel[1],pixel[2],pixel[3])
#         img1.putpixel((x,y),newPixel)
#
# img1.save("newImg.png","PNG")


imgDir = ""
newDir = ""
span = 50
spanCount = 2
count = 0

#获得文件的名字和扩展名
def getNameAndExt(fileName):
    list = fileName.split(r".")
    length = len(list)
    ext = list[length - 1]
    name = r".".join(list[0:length-1])
    return name,ext




def getName(name=None):
    global count
    count += 1
    n = "img" if name is None else name
    return r"{}_{}.png".format(n,count)


# aaa.png
def parsePng(fileName):
    global imgDir
    global span
    global spanCount
    global count
    count = 0
    name,ext = getNameAndExt(fileName)
    path = os.path.join(imgDir,name)
    if os.path.exists(path):
        return
    os.makedirs(path)

    imgFile = os.path.join(imgDir,fileName)
    img = Image.open(imgFile, mode="r")

    offset = [0,]
    for i in range(1,spanCount + 1):
        offset.append(-1 * i * span)
        offset.append(i * span)

    for rf in offset:
        for gf in offset:
            for bf in offset:
                newImg = Image.new("RGBA",(img.width,img.height),(0,0,0,0))
                nm = getName(name)
                newImgFile = os.path.join(path,nm)

                for x in range(0, img.width):
                    for y in range(0, img.height):
                        pixel = img.getpixel((x, y))
                        if not pixel[3]:
                            continue
                        newPixel = (pixel[0] + rf, pixel[1] + gf, pixel[2] + bf, pixel[3])
                        newImg.putpixel((x, y), newPixel)
                newImg.save(newImgFile,"PNG")
                print u"生成文件： " + nm

def parse():
    global imgDir
    for n in os.listdir(imgDir):
        name,ext = getNameAndExt(n)
        if ext == "png":
            parsePng(n)

def clamp(v,minv,maxv):
    return max(min(maxv,v),minv)

def parsePng1(pngFile,newPngFile):
    print "parse png:  " + pngFile
    img = Image.open(pngFile, mode="r")
    newImg = Image.new("RGBA", (img.width, img.height), (0, 0, 0, 0))

    for x in range(0, img.width):
        for y in range(0, img.height):
            pixel = img.getpixel((x, y))
            if not pixel:
                continue
            if not pixel[3]:
                continue
            # vColor = (pixel[0] / 255.0,pixel[1] / 255.0,pixel[2] / 255.0,pixel[3] / 255.0)
            # texColor = (vColor[0] / vColor[3], vColor[1] / vColor[3], vColor[2] / vColor[3], vColor[3])
            # locColor = (clamp(texColor[0] * 5 + 5 / 255,0,1),clamp(texColor[1] * 5 + 5 / 255,0,1),clamp(texColor[2] * 1 + 1 / 255,0,1),clamp(texColor[3] * 1 + 1 / 255,0,1))
            # locColor = (locColor[0] * locColor[3],locColor[1] * locColor[3],locColor[2] * locColor[3],locColor[3])
            # fColor = (locColor[0] * vColor[0],locColor[1] * vColor[1],locColor[2] * vColor[2],locColor[3])
            # fColor = (int(fColor[0] * 255),int(fColor[1] * 255),int(fColor[2] * 255),int(fColor[3] * 255))
            # r = min(5 / 255 + newPixel[0], 1)
            # g = min(5 / 255 + newPixel[1], 1)
            # b = newPixel[2]
            # a = newPixel[3]
            # newPixel = (r * 255, g * 255, b * 255, a * 255)
            # print pixel

            #变金色
            r = clamp(pixel[0] * 5,0,255)
            g = clamp(pixel[1] * 5,0,255)
            newPixel = (int(r), int(g), pixel[2], pixel[3])
            newImg.putpixel((x, y), tuple(newPixel))

            # 灰度化
            grey = clamp(int(pixel[0] * 0.22 + pixel[1] * 0.707 + pixel[2] * 0.071), 0, 255)
            newPixel = (grey, grey, grey, pixel[3])
            newImg.putpixel((x, y), tuple(newPixel))

    newImg.save(newPngFile, "PNG")
    print u"生成文件： " + newPngFile

def walkPath(dirname,newDir):
    for n in os.listdir(dirname):
        path = os.path.join(dirname,n)
        if os.path.isdir(path):
            newPath = os.path.join(newDir,n)
            if not os.path.exists(newPath):
                os.makedirs(newPath)
            walkPath(path,newPath)
        elif os.path.splitext(n)[-1] == ".png":
            newFile = os.path.join(newDir,n.replace("ktv","grey"))
            parsePng1(path,newFile)

def parse1():
    global imgDir
    global newDir
    walkPath(imgDir,newDir)


def main(argv):
    global imgDir
    global newDir
    global span
    global spanCount
    try:
        opts, args = getopt.getopt(argv, "i:s:c:", ["imgDir=", "span=","spanCount="])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'convertPsd -i <imgDir> -s <span> -c <spanCount>'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'convertPsd -i <imgDir> -s <span> -c <spanCount>'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-s", "--span"):
            span = int(arg)
        elif opt in ("-i", "--imgDir"):
            imgDir = os.path.abspath(arg)
        elif opt in ("-c", "--spanCount"):
            spanCount = int(arg)

    imgDir = os.path.abspath(r"F:\work\n5\roll\art\resources\game\building\bd_ktv")
    newDir = os.path.abspath(r"F:\work\n5\roll\art\resources\game\building\bd_grey")


    try:
        # parse()
        parse1()
    except Exception,e:
        print traceback.print_exc()


if __name__ == '__main__':
    #parse()
    main(sys.argv[1:])