# -*- coding: UTF-8 -*-

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import getopt
import json
import xlrd
import re


excelDir = ""
jsonDir = ""


#获得文件的名字和扩展名
def getNameAndExt(fileName):
    list = fileName.split(r".")
    length = len(list)
    ext = list[length - 1]
    name = r".".join(list[0:length-1])
    return name,ext


def parseXlsx(fm):
    global jsonDir
    global excelDir

    fileName = os.path.join(excelDir,fm)
    book = xlrd.open_workbook(fileName)
    sheet = book.sheet_by_index(0)

    len = 0
    ids = []
    comments = []
    contents = []
    fileContent = []

    for index,row in enumerate(sheet.get_rows()):
        if index == 0:
            ids = row
        elif index == 1:
            comments = row
        else:
            contents.append(row)

    for content in contents:
        fc = {}
        for idx,value in enumerate(ids):
            cv = content[idx].value
            if re.search(r"[|]",str(cv)):
                cv = str(cv).split(r"|")
            fc[ids[idx].value] = cv
        fileContent.append(fc)

    name,ext = getNameAndExt(fm)
    jsonFile = os.path.join(jsonDir,name + r".json")
    with open(jsonFile,mode="w") as f:
        json.dump(fileContent,f,indent=4,encoding="utf-8")
        print "file success:   " + jsonFile



def parse():
    global excelDir

    for nm in os.listdir(excelDir):
        name,ext = getNameAndExt(nm)
        if ext == "xlsx":
            parseXlsx(nm)


def main(argv):
    global excelDir
    global jsonDir
    try:
        opts, args = getopt.getopt(argv, "e:j:", ["excelDir=", "jsonDir="])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'usage: python convertPsd.py -e <excelDir> -j <jsonDir> '
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'usage: python convertPsd.py -e <excelDir> -j <jsonDir> '
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-e", "--excelDir"):
            excelDir = os.path.abspath(arg)
        elif opt in ("-j", "--jsonDir"):
            jsonDir = os.path.abspath(arg)

    # exmlDir = r"C:\work\N5\roll\client\client\resource\skins"
    # tsDir = r"C:\work\N5\roll\client\client\src\game\view"

    try:
        parse()
    except Exception,e:
        print u"出错咯： " + e.message


if __name__ == '__main__':
    #parse()
    main(sys.argv[1:])