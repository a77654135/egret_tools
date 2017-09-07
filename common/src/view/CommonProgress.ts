class CommonProgress extends eui.ProgressBar{

    private bg: eui.Image;
    public thumb: eui.Image;
    public labelDisplay: any;

    private _bgSource: string | egret.Texture;
    private _thumbSource: string | egret.Texture;
    private _labelSource: string | egret.Texture;

    public constructor(){
        super();
        this.skinName = CommonProgressSkin;
    }

    public get bgSource(): string | egret.Texture{
        return this._bgSource;
    }
    public set bgSource(value: string | egret.Texture){
        if(value === this._bgSource){
            return;
        }
        this._bgSource = value;
        this.bg.source = value;
    }

    public get thumbSource(): string | egret.Texture{
        return this._thumbSource;
    }
    public set thumbSource(value: string | egret.Texture){
        if(value === this._thumbSource){
            return;
        }
        this._thumbSource = value;
        this.thumb.source = value;
    }

    public get labelSource(): string | egret.Texture{
        return this._labelSource;
    }
    public set labelSource(value: string | egret.Texture){
        if(value === this._labelSource){
            return;
        }
        this._labelSource = value;
        this.labelDisplay.source = value;
    }

    public set label(value: string){
        this.labelDisplay.text = value;
    }
}