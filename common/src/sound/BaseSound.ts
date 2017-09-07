const enum SoundType{
    MUSIC = 0,
    SOUND = 1
}

class BaseSound extends egret.HashObject{

    private disposed: boolean = false;

    private sound: egret.Sound;
    private soundChannel: egret.SoundChannel;

    public path: string = "";
    public type: SoundType = SoundType.SOUND;
    
    private times: number = 1;
    private position: number = 0;

    public constructor(path: string, type: SoundType = SoundType.SOUND){
        super();
        this.path = path;
        this.type = type;

        this.times = type === SoundType.MUSIC ? 0 : 1;        
    }

    private onSoundComplete(e: egret.Event){
        this.stop();
    }

    private onSoundError(e: egret.Event){
        this.sound.removeEventListener(egret.IOErrorEvent.IO_ERROR,this.onSoundError,this);
        console.warn("声音解码错误:  " + this.path);
        this.dispose();
    }

    private playSound(res: any){
        this.sound = res;
        this.soundChannel = this.sound.play(0, this.times);
        this.soundChannel.addEventListener(egret.Event.SOUND_COMPLETE,this.onSoundComplete,this);
        this.sound.addEventListener(egret.IOErrorEvent.IO_ERROR,this.onSoundError,this);
    }

    /**
     * 播放
     */
    public play(){
        if(this.sound){
            this.soundChannel = this.sound.play(0, this.times);
            this.soundChannel.addEventListener(egret.Event.SOUND_COMPLETE,this.onSoundComplete,this);
            this.sound.addEventListener(egret.IOErrorEvent.IO_ERROR,this.onSoundError,this);
        }else{            
            if (RES.hasRes(this.path))
            {
                RES.getResAsync(this.path, (res:any) =>
                {
                    this.playSound(res);
                }, this);
            }
            else
            {
                RES.getResByUrl(this.path, (res:any) =>
                {
                    this.playSound(res);                    
                }, this, RES.ResourceItem.TYPE_SOUND);
            }
        }
    }

    /**
     * 恢复
     */
    public resume(){
        if(this.sound){
            this.soundChannel = this.sound.play(this.position, this.times);
            this.soundChannel.addEventListener(egret.Event.SOUND_COMPLETE,this.onSoundComplete,this);
            this.sound.addEventListener(egret.IOErrorEvent.IO_ERROR,this.onSoundError,this);
        }
    }

    /**
     * 暂停
     */
    public pause(){
        this.removeListeners();
        if(this.soundChannel){
            this.position = this.soundChannel.position;
            this.soundChannel.stop();
            this.soundChannel = null;
        }
    }

    /**
     * 停止
     */
    public stop(){
        this.removeListeners();
        if(this.soundChannel){
            this.soundChannel.stop();
            this.soundChannel = null;
        }
        (<any>SoundManager).putSound(this);
    }

    private removeListeners(){
        if(this.sound)
            this.sound.removeEventListener(egret.IOErrorEvent.IO_ERROR,this.onSoundError,this);
        if(this.soundChannel)
            this.soundChannel.removeEventListener(egret.Event.SOUND_COMPLETE,this.onSoundComplete,this);
    }

    /**
     * 销毁
     */
    public dispose(){
        if(this.disposed){
            return;
        }
        this.disposed = true;
        this.stop();
        this.sound = null;
        this.soundChannel = null;
    }
}