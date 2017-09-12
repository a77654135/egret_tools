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
span = 10
count = 0

#获得文件的名字和扩展名
def getNameAndExt(fileName):
    list = fileName.split(r".")
    length = len(list)
    ext = list[length - 1]
    name = r".".join(list[0:length-1])
    return name,ext




def getName():
    global count
    count += 1
    return r"img_{}.png".format(count)


# aaa.png
def parsePng(fileName):
    global imgDir
    global span
    name,ext = getNameAndExt(fileName)
    path = os.path.join(imgDir,name)
    os.makedirs(path)


def parse():
    global imgDir
    for n in os.listdir(imgDir):
        name,ext = getNameAndExt(n)
        if ext == "png":
            parsePng(n)


def main(argv):
    global imgDir
    global span
    try:
        opts, args = getopt.getopt(argv, "i:s:", ["imgDir=", "span="])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'usage: python convertPsd.py -i <imgDir> -s <span>'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'usage: python convertPsd.py -i <imgDir> -s <span>'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-s", "--span"):
            span = int(arg)
        elif opt in ("-i", "--imgDir"):
            imgDir = os.path.abspath(arg)


    try:
        parse()
    except Exception,e:
        print u"出错咯： " + e.message


if __name__ == '__main__':
    #parse()
    main(sys.argv[1:])