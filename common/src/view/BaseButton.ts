module ButtonStatus {
    export const UP = "up";
    export const DOWN = "down";
    export const DISABLED = "disabled";
}

class BaseButton extends eui.Component {

    private isTouch: boolean = false;
    private canTouch: boolean = true;

    private _toScale: number = 0.9;
    private _sound: string = null;

    public bg: eui.Image = null;
    public icon: eui.Image = null;
    private _bgSource: string = "";
    private _iconSource: string = "";

    private _status: string = ButtonStatus.UP;

    private _normalBgSource: string = "";
    private _normalIconSource: string = "";
    private _touchBgSource: string = "";
    private _touchIconSource: string = "";
    private _disableBgSource: string = "";
    private _disableIconSource: string = "";

    protected partAdded(partName: string, instance: any): void{
        super.partAdded(partName,instance);
        if (instance == this.bg) {
            this.bg.source = this._bgSource;
            this._normalBgSource = this._bgSource;
            this._touchBgSource = this.getImageByStatus(this._normalBgSource, "touch");
            this._disableBgSource = this.getImageByStatus(this._normalBgSource, "disable");
        }
        if (instance == this.icon) {
            this.icon.source = this._iconSource;
            this._normalIconSource = this._iconSource;
            this._touchIconSource = this.getImageByStatus(this._normalIconSource, "touch");
            this._disableIconSource = this.getImageByStatus(this._normalIconSource, "disable");
        }
    }

    private getImageByStatus(normalSource: string, prefix: string) {
        if (normalSource) {
            var path = normalSource.split(".");
            if (path.length == 1) {
                var names = path[0].split("_");
                var nameLen = names.length;
                if (nameLen > 1) {
                    names.splice(nameLen - 1, 0, prefix);
                    return names.join("_");
                } else {
                    return normalSource;
                }
            } else if (path.length == 2) {
                var names = path[1].split("_");
                var nameLen = names.length;
                if (nameLen > 1) {
                    names.splice(nameLen - 1, 0, prefix);
                    var path2 = [path[0], names.join("_")];
                    return path2.join(".");
                } else {
                    return normalSource;
                }
            } else {
                return normalSource;
            }
        } else {
            return "";
        }
    }

    public get bgSource(): string {
        return this._bgSource;
    }
    public set bgSource(value: string) {
        if (value === this._bgSource) {
            return;
        }
        this._bgSource = value;
        if (this.bg) {
            this.bg.source = value;
        }
    }

    public get iconSource(): string {
        return this._iconSource;
    }
    public set iconSource(value: string) {
        if (value === this._iconSource) {
            return;
        }
        this._iconSource = value;
        if (this.icon) {
            this.icon.source = value;
        }
    }

    public get status(): string {
        return this._status;
    }
    public set status(value: string) {
        if (value === this._status) {
            return;
        }
        this._status = value;
        this.statusChange(value);
    }

    private statusChange(value: string) {
        if (value === ButtonStatus.DOWN) {
            this.canTouch = true;
            if (this.bg && RES.hasRes(this._touchBgSource)) {
                this.bg.source = this._touchBgSource;
            }
            if (this.icon && RES.hasRes(this._touchIconSource)) {
                this.icon.source = this._touchIconSource;
            }
        } else if (value === ButtonStatus.DISABLED) {
            this.canTouch = false;
            if (this.bg && RES.hasRes(this._disableBgSource)) {
                this.bg.source = this._disableBgSource;
            }
            if (this.icon && RES.hasRes(this._disableIconSource)) {
                this.icon.source = this._disableIconSource;
            }
        } else {
            this.canTouch = true;
            if (this.bg && RES.hasRes(this._normalBgSource)) {
                this.bg.source = this._normalBgSource;
            }
            if (this.icon && RES.hasRes(this._normalIconSource)) {
                this.icon.source = this._normalIconSource;
            }
        }
    }

    public get toScale(): number {
        return this._toScale;
    }
    public set toScale(value: number) {
        if (value === this._toScale) {
            return;
        }
        this._toScale = value;
    }

    public get sound(): string {
        return this._sound;
    }
    public set sound(value: string) {
        if (value === this._sound) {
            return;
        }
        this._sound = value;
    }

    public constructor() {
        super();
        this.init();
    }

    public init() {
        this.touchEnabled = true;
        this.touchChildren = false;
        this.status = ButtonStatus.UP;
        this.addEventListener(egret.TouchEvent.TOUCH_BEGIN, this.onTouchBegin, this);
        this.addEventListener(egret.TouchEvent.TOUCH_CANCEL, this.onTouchCancel, this);
        this.addEventListener(egret.TouchEvent.TOUCH_RELEASE_OUTSIDE, this.onTouchCancel, this);
        this.addEventListener(egret.TouchEvent.TOUCH_END, this.onTouchEnd, this);
        this.addEventListener(egret.Event.REMOVED_FROM_STAGE, this.dispose, this);
    }

    private onTouchBegin(event: egret.TouchEvent) {
        if (this.isTouch || !this.canTouch) {
            return;
        }
        this.isTouch = true;
        this.status = ButtonStatus.DOWN;
        if (this._toScale != 1 && !RES.hasRes(this._touchBgSource)) {
            egret.Tween.get(this).to({ scaleX: this._toScale, scaleY: this._toScale }, 50);
        }
    }
    private onTouchCancel(event: egret.TouchEvent) {
        if (!this.isTouch) {
            return;
        }
        this.status = ButtonStatus.UP;
        if (this._toScale != 1 && !RES.hasRes(this._touchBgSource)) {
            egret.Tween.get(this).to({ scaleX: 1.0, scaleY: 1.0 }, 50);
        }
        this.isTouch = false;
    }
    private onTouchEnd(event: egret.TouchEvent) {
        if (!this.isTouch) {
            return;
        }
        this.onTouchCancel(event);
        this.dispatchEventWith(egret.TouchEvent.TOUCH_TAP);
        if (!Utils.isNullOrEmpty(this._sound))
            SoundManager.playSound(this._sound);
    }

    public dispose() {
        this.status = ButtonStatus.UP;
        egret.Tween.removeTweens(this);
        this.removeEventListener(egret.TouchEvent.TOUCH_BEGIN, this.onTouchBegin, this);
        this.removeEventListener(egret.TouchEvent.TOUCH_CANCEL, this.onTouchCancel, this);
        this.removeEventListener(egret.TouchEvent.TOUCH_RELEASE_OUTSIDE, this.onTouchCancel, this);
        this.removeEventListener(egret.TouchEvent.TOUCH_END, this.onTouchEnd, this);
        this.removeEventListener(egret.Event.REMOVED_FROM_STAGE, this.dispose, this);
        if (this.parent) {
            this.parent.removeChild(this);
        }
    }
}
