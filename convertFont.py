#-.-coding:utf-8

import os
import getopt
import sys
import traceback
import json
import shutil
import collections

fontDir = ""
refFile = ""
data = {}


'''
layer_image = layer.as_PIL()
layer_image.save(pngFile)
'''

#获得文件的名字和扩展名
def getNameAndExt(fileName):
    list = fileName.split(r".")
    length = len(list)
    ext = list[length - 1]
    name = r".".join(list[0:length-1])
    return name,ext

def parseFnt(path,fname):
    print "parseFnt:   " + path + "  " + fname
    global data
    name,_ = getNameAndExt(fname)
    ref = {}
    if data.has_key(name):
        ref = data[name]
    newContent = collections.OrderedDict()
    with open(path,"r") as f:
        content = json.load(f)
        #print content
        newContent["file"] = content["file"]
        newContent["frames"] = collections.OrderedDict()
        for k,v in content["frames"].iteritems():
            newK = k.replace("_png","")
            if ref.has_key(newK):
                newK = ref[newK]
            newContent["frames"][newK] = content["frames"][k]
    with open(path,"w") as f:
        json.dump(newContent, f,indent=4)
        print "parseFnt successful.   " + fname

def walkDir(dir):
    for f in [x for x in os.listdir(dir) if os.path.splitext(x)[1] == ".fnt"]:
        path = os.path.join(dir,f)
        parseFnt(path,f)

def parse():
    global fontDir
    walkDir(os.path.abspath(fontDir))

def parseReferenceFile():
    global refFile
    global data
    if refFile:
        with open(refFile,"r") as f:
            data = json.load(f)
            print "load ref success:  "
            print data


def main(argv):
    global fontDir
    global refFile
    try:
        opts, args = getopt.getopt(argv, "f:r:", ["fontDir=", "refFile="])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'convertPsd -f <fontDir> - <refFile>'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'convertPsd -f <fontDir> - <refFile>'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-f", "--fontDir"):
            fontDir = arg
        elif opt in ("-r", "--refFile"):
            refFile = arg

    # fontDir = r"F:\work\n5\roll\client\client\resource\assets\font"
    # refFile = r"F:\work\n5\roll\client\client\tools\source\fontRef.json"

    try:
        parseReferenceFile()
        parse()
    except:
        print traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])