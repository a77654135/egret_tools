function decodeString(str) {
    var count = str.length;

    let date = Date.now();
    let ary = new Array();
    for (var i = 0; i < count; i++) {
        ary.push(String.fromCharCode(str.charCodeAt(i) + 4));
    }
    console.log("using time:..................." + (Date.now() - date));
    return ary.join("");
}

function createBitmapData(data: ArrayBuffer, callback?: Function) {
    if (egret.Capabilities.runtimeType === egret.RuntimeType.WEB) {
        let base64 = egret.Base64Util.encode(data as ArrayBuffer);
        let imageType = "image/png";//default value       
        let img: HTMLImageElement = new Image();
        img.src = "data:" + imageType + ";base64," + base64;
        img.crossOrigin = '*';
        img.onload = function () {
            callback(new egret.BitmapData(img));
        }
    }
    else {
        let native_texture = egret_native.Texture.createTextureFromArrayBuffer(data);
        callback(new egret.BitmapData(native_texture));
    }
}

class AnalyzerRequest extends egret.HttpRequest {

    public onReadyStateChange(): void {
        let xhr = (<any>this)._xhr;
        if (xhr.readyState == 4) {// 4 = "loaded"
            let ioError = (xhr.status >= 400 || xhr.status == 0);
            let url = (<any>this)._url;
            let self = this;
            window.setTimeout(function (): void {
                if (ioError) {//请求错误
                    if (DEBUG && !self.hasEventListener(egret.IOErrorEvent.IO_ERROR)) {
                        egret.$error(1011, url);
                    }
                    self.dispatchEventWith(egret.IOErrorEvent.IO_ERROR);
                }
                else {
                    self.dispatchEventWith("io_complete");
                }
            }, 0)

        }
    }
}

class OAnalyzer extends RES.JsonAnalyzer {
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

class PAnalyzer extends RES.SheetAnalyzer {

    private recycle2 = [];
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

    public onLoadFinish(event: egret.Event): void {
        let request = event.target;
        let data: any = this.resItemDic[request.$hashCode];
        delete this.resItemDic[request.hashCode];
        let resItem: RES.ResourceItem = data.item;
        let compFunc: Function = data.func;
        resItem.loaded = (event.type == egret.Event.COMPLETE);
        if (resItem.loaded) {
            if (request instanceof egret.HttpRequest) {
                resItem.loaded = false;
                let imageUrl: string = this.analyzeConfig(resItem, request.response);
                if (imageUrl) {
                    // if (resItem.type == "image") {
                    //     (<any>this).loadImage(imageUrl, data);
                    // } else {
                    //     this.loadImage2(imageUrl, data);
                    // }
                    this.loadImage2(imageUrl, data);
                    this.recycler.push(request);
                    return;
                }
            }
            else {
                let texture: egret.Texture = new egret.Texture();
                texture._setBitmapData(request.data);
                this.analyzeBitmap(resItem, texture);
            }
        }
        if (request instanceof egret.HttpRequest) {
            this.recycler.push(request);
        }
        else {
            (<any>this).recyclerIamge.push(request);
        }
        compFunc.call(data.thisObject, resItem);
    }

    private loadImage2(url: string, data: any): void {
        let request: AnalyzerRequest = <any>this.getRequest2();
        this.resItemDic[request.hashCode] = data;

        request.open(RES.$getVirtualUrl(RES.$getVirtualUrl(url)));
        request.send();
    }

    private getRequest2() {
        let request: AnalyzerRequest = this.recycle2.pop();
        if (!request) {

            request = new AnalyzerRequest();

            request.addEventListener("io_complete", this.onLoadFinish2, this);
            request.addEventListener(egret.IOErrorEvent.IO_ERROR, this.onLoadFinish2, this);
        }
        request.responseType = egret.HttpResponseType.ARRAY_BUFFER;
        return request;
    }

    /**
     * 一项加载结束
     */
    public onLoadFinish2(event: egret.Event): void {
        let request: AnalyzerRequest = <AnalyzerRequest>(event.target);
        let data: any = this.resItemDic[request.hashCode];
        delete this.resItemDic[request.hashCode];
        let resItem: RES.ResourceItem = data.item;
        let compFunc: Function = data.func;
        resItem.loaded = (event.type == "io_complete");
        if (resItem.loaded) {

            let data_src = new Uint8Array(request.response);

            let h = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52];
            let e = [0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82];
            let totalLength = data_src.byteLength + 28;
            let buffer = new Uint8Array(totalLength);
            for (let i = 0, count = h.length; i < count; i++) {
                buffer[i] = h[i];
            }
            for (let i = 0, count = data_src.byteLength; i < count; i++) {
                buffer[i + 16] = data_src[i];
            }
            for (let i = 0, count = e.length; i < count; i++) {
                buffer[totalLength - 12 + i] = e[i];
            }

            (function (this_, request) {
                createBitmapData(buffer, (bmData) => {
                    request.dispatchEventWith(egret.Event.COMPLETE);
                    let texture: egret.Texture = new egret.Texture();
                    texture._setBitmapData(bmData);
                    this_.analyzeBitmap(resItem, texture);

                    this_.recycle2.push(request);
                    compFunc.call(data.thisObject, resItem);
                });
            })(this, request);
        }

    }
}


class QAnalyzer extends RES.FontAnalyzer {

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
        }
        if (config) {
            imageUrl = this.getRelativePath(resItem.url, config["file"]);
        }
        else {
            config = <string>data;
            imageUrl = (<any>this).getTexturePath(resItem.url, config);
        }
        this.sheetMap[name] = config;
        return imageUrl;
    }
}

class MAnalyzer extends RES.ImageAnalyzer {
    public loadFile(resItem: RES.ResourceItem, compFunc: Function, thisObject: any): void {
        if (this.fileDic[resItem.name]) {
            compFunc.call(thisObject, resItem);
            return;
        }
        let request: AnalyzerRequest = <any>this.getRequest();
        this.resItemDic[request.hashCode] = { item: resItem, func: compFunc, thisObject: thisObject };

        request.open(RES.$getVirtualUrl(resItem.url));
        request.send();
    }

    private getRequest(): AnalyzerRequest {
        let request: AnalyzerRequest = <any>this.recycler.pop();
        if (!request) {
            request = new AnalyzerRequest();
            request.addEventListener("io_complete", this.onLoadFinish, this);
            request.addEventListener(egret.IOErrorEvent.IO_ERROR, this.onLoadFinish, this);
        }
        request.responseType = egret.HttpResponseType.ARRAY_BUFFER;
        return request;
    }

    public onLoadFinish(event: egret.Event): void {
        let request: egret.HttpRequest = <egret.HttpRequest>(event.target);
        let data: any = this.resItemDic[request.hashCode];
        delete this.resItemDic[request.hashCode];
        let resItem: RES.ResourceItem = data.item;
        let compFunc: Function = data.func;
        resItem.loaded = (event.type == "io_complete");
        if (resItem.loaded) {

            let data_src = new Uint8Array(request.response);

            let h = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52];
            let e = [0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82];
            let totalLength = data_src.byteLength + 28;
            let buffer = new Uint8Array(totalLength);
            for (let i = 0, count = h.length; i < count; i++) {
                buffer[i] = h[i];
            }
            for (let i = 0, count = data_src.byteLength; i < count; i++) {
                buffer[i + 16] = data_src[i];
            }
            for (let i = 0, count = e.length; i < count; i++) {
                buffer[totalLength - 12 + i] = e[i];
            }

            (function (this_, request) {
                createBitmapData(buffer, (bmData) => {
                    request.dispatchEventWith(egret.Event.COMPLETE);
                    let texture: egret.Texture = new egret.Texture();
                    texture._setBitmapData(bmData);
                    this_.analyzeData(resItem, texture);

                    compFunc.call(data.thisObject, resItem);
                    this_.recycler.push(<any>request);
                });
            })(this, request);
        }

    }
}
