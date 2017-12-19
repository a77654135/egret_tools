#-.-coding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import collections
import os
import json
import shutil
import time


buildingasset_json = r"F:\work\n5\roll\document\表单\json\buildingasset_n5.json"
level_json = r"F:\work\n5\roll\document\表单\json\level_n5.json"
imgInfo_json = r"F:\work\n5\roll\art\resources\game\building\imgInfo.json"
buildingPositionData_json = r"F:\work\n5\roll\document\表单\json\buildingPositionData_n5.json"


baseImgDir = r"F:\work\n5\roll\art\resources\game\building"
dstImgDir = r"F:\work\n5\roll\client\client\resource\assets\game\building"
skinNames = ["normal","ktv","space","sugar","huoguo"]
techIds = [100,200,300,400,500,600,700,800,9999]
techNames = ["home","police","bank","bus","draw","steal","card_1","card_2","god"]
othersDir = r"F:\work\n5\roll\art\resources\game\others"

buildingData = collections.OrderedDict()
levelData = collections.OrderedDict()
imgInfoData = collections.OrderedDict()
buildingPositionData = collections.OrderedDict()

needPackDirs = []
levelImgs = []

def getMaxLevel():
    global levelData
    maxlevel = 0
    for k,v in levelData.iteritems():
        if int(k) > maxlevel:
            maxlevel = int(k)
    return maxlevel

def getTechId(techName):
    if techName == "home":
        return 100
    elif techName == "police":
        return 300
    elif techName == "bank":
        return 500
    elif techName == "bus":
        return 700
    elif techName == "steal":
        return 800
    elif techName == "draw":
        return 200
    elif techName == "card_1":
        return 400
    elif techName == "card_2":
        return 600
    elif techName == "god":
        return 9999
    return 100


def copyNormalImgs(skin,level,skinDir):
    global techIds
    global buildingData
    global imgInfoData
    global buildingPositionData
    global levelImgs

    for bid,binfo in buildingData.iteritems():
        bid = int(bid)
        rid = bid
        if bid > 1000 and bid < 10000:
            rid = bid / 10
        elif bid >= 10000:
            rid = bid / 100
        lr = "l" if rid >= 500 else "r"
        if bid not in techIds:
            imgkey = binfo.get("level_{}".format(level),None)
            if imgkey:
                name,lv = imgkey.split("_")
                # if bid > 300 and bid < 700:
                #     imgkey = "{}_bei_{}".format(name,level)
                if rid > 300 and rid < 700:
                    bname = "{}_{}_bei_{}_{}".format(skin,name,lv,lr)
                else:
                    bname = "{}_{}_{}".format(skin,imgkey,lr)

                bdData = buildingPositionData.get(bname,None)
                if not bdData:
                    print u"找不到资源：" + bname
                else:
                    imgName = bdData["s"]
                    nameLst = imgName.split("_")
                    sk = nameLst[0]
                    nameLst = nameLst[1:]
                    nameLst = "_".join(nameLst)
                    nameLst = nameLst.replace("_png","")

                    imgLst = imgInfoData[sk]
                    imgName = imgLst.get(nameLst,None)
                    if imgName:
                        path,fname = os.path.split(imgName)
                        if fname not in levelImgs:
                            newName = os.path.join(skinDir, fname)
                            shutil.copyfile(imgName, newName)
                            levelImgs.append(fname)
                    else:
                        print u"找不到资源：" + nameLst


def getTechLevel(techname,homelv):
    global levelData
    techInfo = levelData[str(homelv)]["tech"]
    for item in techInfo:
        if item[0] == techname:
            return int(item[1])
    return 0


def copyTechImgs(skin,level,skinDir):
    global techNames
    global buildingData
    global imgInfoData
    global levelData

    global levelImgs

    for techName in techNames:
        techLv = getTechLevel(techName,level)
        techId = getTechId(techName)
        techInfo = buildingData.get(str(techId),None)
        if techInfo:
            techKey = techInfo.get("level_{}".format(techLv),None)
            if techKey:
                imgPath = imgInfoData["other"].get(techKey,None)
                if imgPath:
                    if techKey not in levelImgs:
                        path,fname = os.path.split(imgPath)
                        newName = os.path.join(skinDir,fname)
                        levelImgs.append(techKey)
                        shutil.copyfile(imgPath,newName)
                else:
                    print u"找不到资源：" + techKey


def copyOtherImgs(skin,level,skinDir):
    global baseImgDir
    global othersDir
    commonDir = os.path.join(baseImgDir,"bd_common")
    stealLv = getTechLevel("steal",level)
    c1Lv = getTechLevel("card_1",level)
    c2Lv = getTechLevel("card_2",level)
    drawLv = getTechLevel("draw",level)
    if stealLv:
        f = r"other_200_1.png"
        ofile = os.path.join(commonDir, f)
        nfile = os.path.join(skinDir, f)
        shutil.copyfile(ofile, nfile)
    if c1Lv or c2Lv:
        f = r"other_400_600_1.png"
        ofile = os.path.join(commonDir, f)
        nfile = os.path.join(skinDir, f)
        shutil.copyfile(ofile, nfile)
    if drawLv:
        f = r"other_800_1.png"
        ofile = os.path.join(commonDir, f)
        nfile = os.path.join(skinDir, f)
        shutil.copyfile(ofile, nfile)

    for f in os.listdir(othersDir):
        ofile = os.path.join(othersDir,f)
        nfile = os.path.join(skinDir,f)
        shutil.copyfile(ofile,nfile)


def packSkinLevelImg(skin,level):
    global baseImgDir
    global dstImgDir

    skinDir = os.path.join(dstImgDir, "pack")
    skinDir = os.path.join(skinDir,skin)
    skinDir = os.path.join(skinDir,"{}_lv{}".format(skin,level))
    if not os.path.exists(skinDir):
        os.makedirs(skinDir)
        needPackDirs.append(skinDir)

    global levelImgs
    levelImgs = []

    copyNormalImgs(skin,level,skinDir)
    if level > 1:
        copyNormalImgs(skin, level-1, skinDir)
    copyTechImgs(skin,level,skinDir)
    copyOtherImgs(skin,level,skinDir)
    print "{}_lv{}  OK!".format(skin,level)


def packSkinImg(skin):
    for l in range(1,getMaxLevel() + 1):
        packSkinLevelImg(skin,l)

def packSkins():
    global skinNames
    global dstImgDir

    skinDir = os.path.join(dstImgDir, "pack")
    if os.path.exists(skinDir):
        shutil.rmtree(skinDir,True)

    time.sleep(2)

    for skin in skinNames:
        packSkinImg(skin)


def parseData():
    global buildingData
    global levelData
    global imgInfoData
    global buildingPositionData
    global buildingasset_json
    global level_json
    global imgInfo_json
    global buildingPositionData_json

    with open(buildingasset_json.decode("utf-8"),"r") as f:
        buildingData = json.load(f)
    with open(level_json.decode("utf-8"),"r") as f:
        levelData = json.load(f)
    with open(imgInfo_json.decode("utf-8"),"r") as f:
        imgInfoData = json.load(f)
    with open(buildingPositionData_json.decode("utf-8"),"r") as f:
        buildingPositionData = json.load(f)

def packExec():
    global needPackDirs
    for dir in needPackDirs:
        path,name = os.path.split(dir)
        os.system(r"TextureMerger.exe -p {} -o {}".format(dir,os.path.join(path,"{}.json".format(name))))
        print "packTexture: {}.json".format(name)


def rmTempFiles():
    global needPackDirs

    time.sleep(2)

    for dir in needPackDirs:
        shutil.rmtree(dir,True)

def main():
    try:
        parseData()
        #packImg()
        packSkins()
        packExec()
        rmTempFiles()
    except Exception,e:
        import traceback
        print traceback.print_exc()


if __name__ == "__main__":
    main()