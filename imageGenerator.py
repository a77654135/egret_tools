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


def main(argv):
    global imgDir
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


    try:
        parse()
    except Exception,e:
        print u"出错咯： " + e.message


if __name__ == '__main__':
    #parse()
    main(sys.argv[1:])