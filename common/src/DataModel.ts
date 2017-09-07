class DataModel extends egret.HashObject{
    private _props:Object = {};
    private _observers: Object = {};
    public onDispose: Function;

    public constructor(data?: Object){
        super();
        if(data)
            this.setData(data);
    }

    public getProp(name: string): any {
        return this._props[name];
    }
    public hasProp(name: string): boolean {
        return this._props.hasOwnProperty(name);
    }
    public setProp(name: string, val: any) {
        if (this._props[name] === val)
            return;
        if (this._observers[name]){
            var t = this._observers[name];
            if (Array.isArray(t)) {
                for (var i = 0; i < t.length; i++) {
                    var n = t[i];
                    n.func.call(n.ctx, val, this._props[name]);
                }
            }
            else
                t.func.call(t.ctx, val, this._props[name]);
        }
        this._props[name] = val;			
    }
    public initProp(name: string, val:any){
        this._props[name] = val;
    }
    public setData(source: any) {
        for (var p in source) {
            this.setProp(p, source[p]);               
        }
    }		
    public removeProp(name: string) {
        delete this._props[name];
    }

    public addObserver(name: string, func: (newVal: any, oldVal?: any) => void, thisArg?: any): Object {
        var t = { name: name, func: func, ctx: thisArg, _p: this };
        if (!this._observers[name]) {
            this._observers[name] = t;
        }
        else {
            var o = this._observers[name];
            if (Array.isArray(o))
                o.push(t);
            else
                this._observers[name] = [o, t];
        }
        return t;
    }

    public get disposed() {
        return this._props == null;
    }
    public clearObserver(name: string) {
        delete this._observers[name];
    }
    public removeObserver(t: Object) {
        for (var name in this._observers) {
            var o = this._observers[name];
            if (o == t) {
                delete this._observers[name];
            }else if (Array.isArray(o)) {
                for (var i = 0; i < o.length; ++i) {
                    if (o[i] == t) {
                        var obj = o.splice(i, 1);
                        return;
                    }
                }
            }
        }
    }
    public dispose() {
        this._props = null;
        this._observers = null;
        if (this.onDispose)
            this.onDispose();
    }
}