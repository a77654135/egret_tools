#-.-coding:utf-8

import os
import getopt
import sys
import traceback
import json
from psd_tools import PSDImage,Layer,Group

psdDir = ""
jsonDir = ""
info = {}


#获得图层或图层组的尺寸信息
def getDimension(layer):
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

def parseLayer(layer):
    assert isinstance(layer,Layer)
    x,y,w,h = getDimension(layer)
    global info
    name = layer.name.strip().split(" ")[0]
    if not info.has_key(name):
        info[name] = []
    info[name].append("{},{},{},{}".format(x,y,w,h))


def parseGroup(group):
    for layer in group.layers:
        if isinstance(layer,Layer):
            parseLayer(layer)
        elif isinstance(layer,Group):
            parseGroup(layer)


def parse():
    global psdDir
    global jsonDir
    global info
    for f in [x for x in os.listdir(os.path.abspath(psdDir)) if os.path.splitext(x)[-1] == ".psd"] :
        psd = PSDImage.load(os.path.join(os.path.abspath(psdDir),f))
        info = {}
        parseGroup(psd)
        print f
        fname = os.path.splitext(f)[0] + ".json"
        with open(os.path.join(os.path.abspath(jsonDir),fname),"w") as fp:
            json.dump(info,fp,indent=4)
            print "export successfully.  " + fname


def main(argv):
    global psdDir
    global jsonDir
    try:
        opts, args = getopt.getopt(argv, "p:j:", ["psdDir=", "jsonDir="])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'convertPsd -p <psdDir> -j <jsonDir>'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'convertPsd -p <psdDir> -j <jsonDir>'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-p", "--psdDir"):
            psdDir = arg
        elif opt in ("-j", "--jsonDir"):
            jsonDir = arg

    try:
        parse()
    except:
        print traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])