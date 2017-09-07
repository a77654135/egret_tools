/**
 * 通用bmfont类，和eui.BitmapLabel完全一样的用法
 * 提供一个source属性，使用指定字体资源
 */
class CommonBitmapLabel extends eui.BitmapLabel{
    private _source: string | egret.Texture;

    public constructor(){
        super();        
    }

    public get source(): string | egret.Texture{
        return this._source;        
    }

    public set source(value: string | egret.Texture){
        if(value === this._source){
            return;
        }
        this._source = value;
    }
    

    $setFontData (value: egret.BitmapFont) {
        if (!value || value == this.$BitmapText[5 /* font */]) {
            return false;
        }
        if(this._source){
            if(typeof(this._source) == "string"){
                if(RES.hasRes(this._source)){
                    RES.getResAsync(this._source,(data)=>{
                        value.$texture = data;
                    },this);
                }
            }else{
                value.$texture = this._source;
            }  
            value.getTexture = function(name: string){
                var texture = this._textureMap[name];
                if (!texture) {
                    var c = this.charList[name];
                    if (!c) {
                        return null;
                    }
                    texture = this.createTexture(name, c.x + this.$texture._bitmapX, c.y + this.$texture._bitmapY, c.w, c.h, c.offX, c.offY, c.sourceW, c.sourceH);
                    this._textureMap[name] = texture;
                }
                return texture;
            }          
        }
        this.$BitmapText[5 /* font */] = value;
        this.$invalidateContentBounds();
    }          
}