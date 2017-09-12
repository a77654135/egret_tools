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
tsFile = ""

#获得文件的名字和扩展名
def getNameAndExt(fileName):
    list = fileName.split(r".")
    length = len(list)
    ext = list[length - 1]
    name = r".".join(list[0:length-1])
    return name,ext


def getLx(col):
    try:
        if type(float(col)) == float:
            return "number"
    except:
        pass

    if isinstance(col,float) or isinstance(col,int):
        return "number"
    if isinstance(col,unicode) or isinstance(col,str):
        return "string"
    return "any"


#fileName:  basedata.xlsx
def parseXlsx(fileName):
    global excelDir

    absFilename = os.path.join(excelDir, fileName)
    book = xlrd.open_workbook(absFilename)
    sheet = book.sheet_by_index(0)
    name,ext = getNameAndExt(fileName)
    if str(name).endswith(r"_n5"):
        name = str(name).replace(r"_n5","",1)

    ids = []
    comments = []
    contents = []
    fileContent = u""
    hasComment = False

    for index, row in enumerate(sheet.get_rows()):
        if index == 0:
            ids = row
        elif index == 1:
            comments = row
        elif index == 2:
            contents =  row

    if ids == []:
        # 空表
        print u"{} 是空表".format(fileName)
        return u""
    if comments != [] and str(comments[0].value).startswith(r"//"):
        hasComment = True
    if not hasComment and comments != []:
        contents = comments
    fileContent += u"    class %sConfig{\n" % name.capitalize()
    fileContent += u"        //configName:    %s\n" % fileName
    fileContent += u"        //path:    %s\n" % absFilename
    for index,id in enumerate(ids):
        if not id.value:
            continue
        if str(id.value).startswith(r"//"):
            continue
        com = u""
        lx = u"any"
        if hasComment:
            com = u"//" + comments[index].value
        if contents != []:
            col = contents[index].value
            lx = getLx(col)
            lst = str(col).split(r"|")
            if len(lst) > 1:
                zlx = getLx(lst[0])
                lx = u"%s[]" % zlx
        fileContent += u"        %s:%s;    %s\n" % (id.value,lx,com)
    fileContent += u"    }\n"
    fileContent += u"\n"

    return fileContent


def parse():
    global excelDir
    global tsFile

    fileContent = u""
    fileContent += u"declare namespace ConfigData{\n"

    for f in os.listdir(excelDir):
        name,ext = getNameAndExt(f)
        if ext == "xlsx":
            fileContent += parseXlsx(f)

    fileContent += u"}"
    dir = os.path.dirname(tsFile)
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(tsFile,"w") as fp:
        fp.write(fileContent)
        print "-----------------success------------------"




def main(argv):
    global excelDir
    global tsFile
    try:
        opts, args = getopt.getopt(argv, "e:t:", ["excelDir=", "tsFile="])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'usage: python convertPsd.py -e <excelDir> -t <tsFile> '
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'usage: python convertPsd.py -e <excelDir> -t <tsFile> '
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-e", "--excelDir"):
            excelDir = os.path.abspath(str(arg).decode("utf-8"))
        elif opt in ("-t", "--tsFile"):
            tsFile = os.path.abspath(arg)

    # exmlDir = r"C:\work\N5\roll\client\client\resource\skins"
    # tsDir = r"C:\work\N5\roll\client\client\src\game\view"

    try:
        parse()
    except Exception,e:
        print u"出错咯： " + e.message


def main2():
    #name = r"C:\work\N5\roll\document\building_n5.xlsx"
    # book = xlrd.open_workbook(name)
    # sheet = book.sheet_by_index(0)
    # for index,row in enumerate(sheet.get_rows()):
    #     print row
    #     if index == 3:
    #         for col in row:
    #             print type(col.value)
    global excelDir
    excelDir = r"C:\work\N5\roll\document"
    parse()

if __name__ == '__main__':
    #main2()
    main(sys.argv[1:])