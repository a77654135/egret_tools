#encoding:utf-8
import os,json,getopt,sys,traceback,time,re,hashlib


zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
kuohao_patten = re.compile(u'[()]')

def contain_error(word):
    '''
    判断传入字符串是否包含中文
    :param word: 待判断字符串
    :return: True:包含中文  False:不包含中文
    '''
    #word = word.decode()
    global zh_pattern
    match = zh_pattern.search(word)
    match2 = kuohao_patten.search(word)

    return match or match2


class Utils:

    resType = {
        "json": "json",
        "jpg": "image",
        "txt": "text",
        "png": "image",
        "mp3": "sound",
        "ogg": "sound",
        "wav": "sound",
        "xml": "xml",
        "fnt": "font",
        "mp4": "bin",
        "js": "bin"
    }
	
    ignoreFiles = [
		"default.thm.json",
		"default.res.json"
	]

    @staticmethod
    def getFileNameAndExt(filename):
        pieces = filename.split(r".")
        length = len(pieces)
        if length == 2:
            return (pieces)
        elif length == 1:
            return (pieces,"")
        else:
            return (r".".join(pieces[0:length-1]),pieces[-1])

    @staticmethod
    def getFileExt(filename):
        pieces = filename.split(r'.')
        if len(pieces) >= 2:
            return pieces[-1]
        return ""

    @staticmethod
    def getFileType(filename):
        ext = Utils.getFileExt(filename)
        return Utils.resType[ext] if ext in Utils.resType else ""

    @staticmethod
    def getResName(filename):
        name,ext = Utils.getFileNameAndExt(filename)
        if ext:
            return r"{}_{}".format(name,ext)
        return name

class Scanner:
    resources = []
    contents = {}
    oldValues = {}
    def __init__(self,argv):
        self.resDir = os.getcwd()
        self.scanDirName = ""
        self.outputFile = "default.res.json"
        self.argv = argv
        self.resNames = []

    def parseArgv(self):
        try:
            opts,args = getopt.getopt(self.argv,"hd:o:s:",["dir=","outputFile=","scanDirName="])
        except getopt.GetoptError:
            print "scanRes -d resDir -o outputFile -s scanDirName"
            sys.exit(2)

        for k,v in opts:
            if k in ("-h","--help"):
                print "scanRes -d resDir -o outputFile -s scanDirName"
                sys.exit(2)
            elif k in ("-d","--dir"):
                self.resDir = os.path.abspath(v)
            elif k in ("-o","--outputFile"):
                self.outputFile = os.path.realpath(v)
            elif k in ("-s","--scanDirName"):
                self.scanDirName = v

    def scan(self):
        self.getInfo()
        self.readDir(self.resDir,[],isRoot=True)
        self.filterContent()
        self.restore()
        self.addVersion()

    def getInfo(self):
        cont = {}
        try:
            fp = file(self.outputFile,"r")
            cont = json.load(fp,"utf-8")
            fp.close()
        except Exception,e:
            print "read resource file error:" + e.message
        finally:
            Scanner.contents = cont
            if "resources" in cont:
                for res in cont["resources"]:
                    for k,v in  res.iteritems():
                        if k not in ("url","type","name","subkeys"):
                            #print "find :   " + k + "   " + v
                            name = res["name"]
                            if name not in self.oldValues:
                                self.oldValues[name] = {}
                            self.oldValues[name][k] = v

    def filterContent(self):
        if "groups" in Scanner.contents:
            #print Scanner.contents["groups"]
            for grp in Scanner.contents["groups"]:
                keys = grp.get("keys","")
                if keys:
                    keyList = keys.split(r",")
                    lst = [k for k in keyList if k in self.resNames]
                    keys = r",".join(lst) if len(lst) else ""
                    grp["keys"] = keys


    def readDir(self,absDir,tempPath,isRoot = False):
        #print r"readdir:  {}    {}".format(absDir,r"/".join(tempPath))
        names = os.listdir(absDir)
        dirs = []
        files = []
        jsonFiles = []
        pngFiles = []
        otherFiles = []
        excludePng = []

        for name in names:
            if name in Utils.ignoreFiles:
                continue
            if name != self.scanDirName and isRoot:
                continue
            if contain_error(name):
                raise Exception("illegal resource name:" + name)
            f = os.path.join(absDir,name)
            if os.path.isdir(f):
                tp = tempPath[:]
                tp.append(name)
                dirs.append((f,tp))
            elif os.path.isfile(f):
                tp = tempPath[:]
                files.append((f,tp,name))

        for f in files:
            ext = Utils.getFileExt(f[2])
            if ext == "json":
                jsonFiles.append(f)
            elif ext == "png":
                pngFiles.append(f)
            else:
                otherFiles.append(f)

        for f in jsonFiles:
            #print f[0]
            try:
                fp = file(f[0])
                content = json.load(fp,"utf-8")
                fp.close()
            except:
                #print "json file load error:  {}".format(f[0])
                name = Utils.getResName(f[2])
                url = r"/".join(f[1]) + r"/" + f[2] if f[1] else f[2]
                item = {"name": name, "type": "json", "url": url}
                if name in self.oldValues:
                    for k in self.oldValues[name]:
                        item[k] = self.oldValues[name][k]
                Scanner.resources.append(item)
                if name in self.resNames:
                    print "name: {} already exists... ".format(name)
                self.resNames.append(name)
                continue

            if "file" in content and "frames" in content:
                #excludePng.append(content["file"])
                name = Utils.getResName(f[2])
                #type = Utils.getFileType(f[2])
                url = r"/".join(f[1]) + r"/" + f[2] if f[1] else f[2]
                subkeys = []
                for f in content["frames"]:
                    subkeys.append(f)

                item = {"name":name,"type":"sheet","url":url,"subkeys":r",".join(subkeys)}
                if name in self.oldValues:
                    for k in self.oldValues[name]:
                        item[k] = self.oldValues[name][k]
                Scanner.resources.append(item)
                if name in self.resNames:
                    print "name: {} already exists... ".format(name)
                self.resNames.append(name)
            else:
                name = Utils.getResName(f[2])
                url = r"/".join(f[1]) + r"/" + f[2] if f[1] else f[2]

                item = {"name": name, "type": "json", "url": url}
                if name in self.oldValues:
                    for k in self.oldValues[name]:
                        item[k] = self.oldValues[name][k]
                Scanner.resources.append(item)
                if name in self.resNames:
                    print "name: {} already exists... ".format(name)
                self.resNames.append(name)

        for f in pngFiles:
            tempPath = f[1]
            fileName = f[2]
            if fileName in excludePng:
                continue
            else:
                name = Utils.getResName(fileName)
                url = r"/".join(tempPath) + r"/" + fileName if f[1] else f[2]
                item = {"name": name, "type": "image", "url": url}
                if name in self.oldValues:
                    for k in self.oldValues[name]:
                        item[k] = self.oldValues[name][k]
                Scanner.resources.append(item)
                if name in self.resNames:
                    print "name: {} already exists... ".format(name)
                self.resNames.append(name)

        for f in otherFiles:
            tempPath = f[1]
            fileName = f[2]

            ext = Utils.getFileExt(fileName)

            if ext not in Utils.resType:
                #print "ext not in exts:   " + ext + "   fileName:   " + fileName
                continue

            if fileName in excludePng:
                #print "fileName in excludePng:   " + type + "   fileName:   " + fileName
                continue

            name = Utils.getResName(fileName)
            #type = Utils.getFileType(fileName)
            url = r"/".join(tempPath) + r"/" + fileName if f[1] else f[2]
            item = {"name": name, "type": Utils.resType[ext], "url": url }
            if name in self.oldValues:
                for k in self.oldValues[name]:
                    item[k] = self.oldValues[name][k]
            Scanner.resources.append(item)
            if name in self.resNames:
                print "name: {} already exists... ".format(name)
            self.resNames.append(name)

        for d in dirs:
            self.readDir(d[0],d[1])

    def restore(self):
        Scanner.contents["resources"] = self.resources
        try:
            fp = file(os.path.join(self.resDir, self.outputFile), "w+")
            fp.truncate()
            json.dump(Scanner.contents, fp,indent=4)
            fp.close()
        except Exception,e:
            print "dump json file error: " + e.message
            print traceback.print_exc()

    def genVersion(self,url):
        urls = url.split(r"/")
        absPath = os.path.join(self.resDir, *urls)
        with open(absPath,"rb") as f:
            content = f.readlines()
            md5 = hashlib.md5()
            md5.update("".join(content))
            version = md5.hexdigest()
        return version[5:10]



    def addVersion(self):
        with open(os.path.join(self.resDir,self.outputFile),"r") as f:
            content = json.load(f)
        resources = content.get("resources",None)
        if resources:
            for item in resources:
                url = item.get("url",None)
                if url:
                    version = self.genVersion(url)
                    item["url"] = "{}?v={}".format(url,version)

        with open(os.path.join(self.resDir,self.outputFile),"w") as f:
            json.dump(content,f,indent=4)



def main(argv):
    scanner = Scanner(argv)
    scanner.parseArgv()

    print r"resDir:  {}   file:  {}".format(scanner.resDir,scanner.outputFile)

    scanner.scan()



if __name__ == '__main__':
    main(sys.argv[1:])