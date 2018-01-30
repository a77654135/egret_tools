# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     publish
   Author :       talus
   date：          2018/1/28 0028
   Description :
-------------------------------------------------

"""
__author__ = 'talus'


import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import getopt
import re
import json
import datetime
import traceback
import shutil
import time

projectDir = ""
releaseDir = ""
updateConfig = False
configData = {}


class Utils():
    @staticmethod
    def minJson(jsonFile):
        '''
        压缩json文件
        :param jsonFile:
        :return:
        '''
        with open(jsonFile,"r") as f:
            content = json.load(f)
        with open(jsonFile,"w") as f:
            json.dump(content,f)



def updateReleaseCode():
    '''
    把发布目录代码更新到最新，防止提交时冲突
    然后删除所有文件，方便提交最新的文件
    :return:
    '''
    global releaseDir
    global configData

    os.system(r"svn revert -R {}".format(releaseDir))
    os.system(r"svn update {}".format(releaseDir))
    print u"目录更新成功"

    #保留配置文件内容
    configFile = os.path.join(releaseDir,*["resource","config_avu.json"])
    if os.path.exists(configFile):
        with open(configFile,"r") as f:
            configData = json.load(f)
    else:
        print u"没有找到 config_avu.json"

    # print ""
    # print configData
    # print ""

    #保留原skin文件
    path = os.path.dirname(releaseDir)
    skin1 = os.path.join(releaseDir,*["resource","skin.js"])
    skin2 = os.path.join(releaseDir,*["resource","skin.min.js"])
    if os.path.exists(skin1):
        shutil.copyfile(skin1,os.path.join(path,"skin.js"))
    else:
        print u"没有找到 skin.js"
    if os.path.exists(skin2):
        shutil.copyfile(skin2,os.path.join(path,"skin.min.js"))
    else:
        print u"没有找到 skin.min.js"



def runPublish():
    '''
    egret publish
    :return:
    '''
    global projectDir
    global releaseDir

    os.chdir(projectDir)
    version = str(datetime.datetime.now())[:10]

    tempDir = os.path.join(projectDir,*[r"bin-release",r"web",version])
    if os.path.exists(tempDir):
        shutil.rmtree(tempDir)

    os.system(r"egret publish --version {}".format(version))
    print u"编译成功"

    u'''
    然后拷贝文件到发布目录
    '''

    if not os.path.exists(releaseDir):
        os.makedirs(releaseDir)

    #清空目录
    for f in os.listdir(releaseDir):
        fn = os.path.join(releaseDir,f)
        if re.search(r"\.svn",f):
            continue
        if os.path.isdir(fn):
            shutil.rmtree(fn)
        else:
            os.unlink(fn)

    for f in os.listdir(tempDir):
        fn = os.path.join(tempDir,f)
        if os.path.isdir(fn):
            shutil.copytree(fn,os.path.join(releaseDir,f))
        else:
            shutil.copyfile(fn,os.path.join(releaseDir,f))

    # shutil.copytree(tempDir,releaseDir)
    print u"拷贝到发布目录成功"


def parseThemeJson():
    '''
    解析default.thm.json，删掉city部分
    :return:
    '''

    global releaseDir
    thmFile = os.path.join(releaseDir,*["resource","default.thm.json"])
    with open(thmFile,"r") as f:
        content = json.load(f)
    exmls = content.get("exmls",None)
    newExmls = []
    if exmls is not None:
        for item in exmls:
            if not re.search(r"skins/city/City_",item["path"]):
                newExmls.append(item)
    content["exmls"] = newExmls

    with open(thmFile,"w") as f:
        json.dump(content,f)
    print u"解析default.thm.json成功"


def parseIndexHtml():
    '''
    替换html中的信息
    :return:
    '''
    global projectDir
    global releaseDir

    fromFile = os.path.join(projectDir,*[r"template","web","index.html"])
    toFile = os.path.join(releaseDir,"index.html")

    with open(fromFile,"r") as f:
        lines = f.readlines()

    # 替换版本号
    version = str(datetime.datetime.now())[0:16]
    newlines = []
    for line in lines:
        l = line.replace(r"{{version}}",version)
        newlines.append(l)
    print u"替换版本号成功"

    with open(toFile,"w") as f:
        f.writelines(newlines)


def restoreFile():
    '''
    删除一些不用的文件
    保留原来的一些文件
    :return:
    '''
    global releaseDir
    global configData

    for f in os.listdir(os.path.join(releaseDir,"resource")):
        if f.startswith("config_avu"):
            os.unlink(os.path.join(releaseDir,*["resource",f]))

    time.sleep(1)

    #恢复原配置
    if configData.has_key("xml_ver"):
        if isinstance(configData["xml_ver"],int):
            configData["xml_ver"] = configData["xml_ver"] + 1
    if configData.has_key("notice_ver"):
        if isinstance(configData["notice_ver"],int):
            configData["notice_ver"] = configData["notice_ver"] + 1
    if configData.has_key("json_ver"):
        if isinstance(configData["json_ver"],int):
            configData["json_ver"] = configData["json_ver"] + 1
    if configData.has_key("res_ver"):
        if isinstance(configData["res_ver"],int):
            configData["res_ver"] = configData["res_ver"] + 1

    # print ""
    # print configData
    # print ""
    with open(os.path.join(releaseDir,*["resource","config_avu.json"]),"w") as f:
        json.dump(configData,f)

    skin1 = os.path.join(os.path.dirname(releaseDir),"skin.js")
    skin2 = os.path.join(os.path.dirname(releaseDir),"skin.min.js")
    if os.path.exists(skin1):
        shutil.copyfile(skin1,os.path.join(releaseDir,*["resource","skin.js"]))
    if os.path.exists(skin2):
        shutil.copyfile(skin2,os.path.join(releaseDir,*["resource","skin.min.js"]))

    print u"恢复原来的配置成功"


def updateSVN():
    u'''
    更新项目中的代码
    :return:
    '''
    global updateConfig
    global projectDir

    os.chdir(projectDir)
    os.system(r"svn update {}".format(projectDir))
    print u"更新代码成功"

    if not updateConfig:
        return
    os.system(r"gulp json-zip")
    print u"更新配置成功"



def parse():
    updateSVN()
    updateReleaseCode()
    runPublish()
    parseThemeJson()
    parseIndexHtml()
    restoreFile()


def main(argv):
    global projectDir
    global releaseDir
    global updateConfig

    try:
        opts, args = getopt.getopt(argv, "p:r:u", ["projectDir=", "releaseDir=","updateConfig",])
    except getopt.GetoptError:
        print "--------------------------------------------"
        print 'publish -p <projectDir> -r <releaseDir>  --updateConfig'
        print "--------------------------------------------"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "--------------------------------------------"
            print 'publish -p <projectDir> -r <releaseDir>  --updateConfig'
            print "--------------------------------------------"
            sys.exit(2)
        elif opt in ("-p", "--projectDir"):
            projectDir = os.path.abspath(arg)
        elif opt in ("-r", "--releaseDir"):
            releaseDir = os.path.abspath(arg)
        elif opt in ("-u", "--updateConfig"):
            updateConfig = True

    # projectDir = r"F:\work\n5\roll\client\client"
    # releaseDir = r"F:\work\n5\roll\roll2"

    try:
        parse()
    except Exception,e:
        print traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])