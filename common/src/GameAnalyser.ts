function decodeString(str) {
    var count = str.length;
    var ret = "";

    let date = Date.now();
    for (var i = 0; i < count; i++) {
        ret += String.fromCharCode(str.charCodeAt(i) + 4);
    }
    console.log("using time:..................." + (Date.now() - date));
    return ret;
}

class OAnalyser extends RES.JsonAnalyzer {
    public analyzeData(resItem: RES.ResourceItem, data: any): void {
        let name: string = resItem.name;
        if (this.fileDic[name] || !data) {
            return;
        }
        try {
            let str: string = <string>data;

            let s = decodeString(str);

            this.fileDic[name] = JSON.parse(s);
        }
        catch (e) {
            egret.$warn(1017, resItem.url, data);
        }
    }
}

class PAnalyser extends RES.SheetAnalyzer {

    public analyzeConfig(resItem: RES.ResourceItem, data: string): string {
        let name: string = resItem.name;
        let config: any;
        let imageUrl: string = "";
        try {
            let str: string = <string>data;

            let s = decodeString(str);

            config = JSON.parse(s);
        }
        catch (e) {
            egret.$warn(1017, resItem.url, data);
        }
        if (config) {
            this.sheetMap[name] = config;
            imageUrl = this.getRelativePath(resItem.url, config["file"]);
        }
        return imageUrl;
    }
}


class QAnalyser extends RES.FontAnalyzer {

    public analyzeData(resItem: RES.ResourceItem, data: any): void {
        let name: string = resItem.name;
        if (this.fileDic[name] || (data != "" && !data)) {
            return;
        }
        try {
            let str: string = <string>data;

            let s = decodeString(str);

            this.fileDic[name] = JSON.parse(s);
        }
        catch (e) {
            egret.$warn(1017, resItem.url, data);
        }
    }

    public analyzeConfig(resItem:RES.ResourceItem, data:string):string {
            let name:string = resItem.name;
            let config:any;
            let imageUrl:string = "";
            try {
                let str:string = <string> data;
                let s = decodeString(str);
                config = JSON.parse(s);
            }
            catch (e) {
            }
            if (config) {
                imageUrl = this.getRelativePath(resItem.url, config["file"]);
            }
            else {
                config = <string> data;
                imageUrl = (<any>this).getTexturePath(resItem.url, config);
            }
            this.sheetMap[name] = config;
            return imageUrl;
        }
}
