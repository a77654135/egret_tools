module SoundManager{

    var soundCache = {};
    var currentMusic: BaseSound = null;
    var currentMusicPath: string = "";  

    var playingSounds: BaseSound[] = [];  
    
    var musicStatus: boolean = true;
    var soundStatus: boolean = true;

    export function initialize(){
        var stage = Global.getStage();
        stage.addEventListener(egret.Event.ACTIVATE, this.onActive, this);
        stage.addEventListener(egret.Event.DEACTIVATE, this.onDeactive, this);
    }    

    export function onActive(){
        if(musicStatus)
            playMusic(currentMusicPath);
    }

    export function onDeactive(){
        stopMusic();
        stopSound();
    }

    /**
     * 设置背景音乐的开关
     */
    export function setMusicStatus(value: boolean){
        if(value){
            if(!Utils.isNullOrEmpty(currentMusicPath)){
                playMusic(currentMusicPath);
            }
        }else{
            stopMusic();
        }
        musicStatus = value;
    }

    /**
     * 设置音效开关
     */
    export function setSoundStatus(value: boolean){
        if(value == false){
            stopSound();
        }
        soundStatus = value;
    }

    /**
     * 播放背景音乐
     */
    export function playMusic(path: string){     
        currentMusicPath = path;
        if(Utils.isNullOrEmpty(path) || musicStatus == false){
            stopMusic();
            return;
        }   
        if(path === currentMusicPath){
            if(currentMusic){
                //要播放的背景音乐和当前正在播放的背景音乐一样
                return;
            }else{
                currentMusic = getSound(path, SoundType.MUSIC);
                currentMusic.play();
            }
        }else{
            if(currentMusic)
                currentMusic.stop();
            currentMusic = getSound(path, SoundType.MUSIC);
            currentMusic.play();
        }
    }

    /**
     * 停止背景音乐
     */
    export function stopMusic(){
        if(currentMusic)
            currentMusic.stop();
            currentMusic = null;
    }


    /**
     * 播放音效
     */
    export function playSound(path: string){
        if(soundStatus == false){
            return;
        }
        var sound = getSound(path, SoundType.SOUND);
        sound.play();
        playingSounds.push(sound);
    }

    /**
     * 停止音乐
     */
    export function stopSound(){
        while(playingSounds.length){
            playingSounds.pop().stop();
        }
    }

    function putSound(sound: BaseSound){
        var soundList = soundCache[sound.path];        
        if(soundList){
            soundList.push(sound);
        }else{
            soundCache[sound.path] = [sound];
        }

        var idx = playingSounds.indexOf(sound);
        if(idx !== -1){
            playingSounds.splice(idx,1);
        }
    }

    function getSound(path: string, type: SoundType): BaseSound{
        var soundList = soundCache[path];
        if(soundList){
            return soundList.shift();
        }else{
            return new BaseSound(path,type);
        }
    }
}