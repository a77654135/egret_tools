var testcase;
(function (testcase) {

    var list = [];

    var div = document.getElementById("testcase");
    var closeBtn = document.getElementById("testcase_close");
    var opened = true;
    closeBtn.onclick = function () {
        if (opened) {
            //关闭状态
            opened = false;
            closeBtn.innerText = "打开";
            div.style.left = "-260px";
        } else {
            //打开状态
            opened = true;
            closeBtn.innerText = "关闭";
            div.style.left = "0px";
        }
    }

    function register(name, func, ctx) {

        var length = list.length;

        //     <div id="a4" style="position: absolute; left: 0px; top: 520px; width: 100%; height: 150px; background: gray;">
        //     <p><span>arg1:</span><input id="arg1" type="text" /></p>
        //     <p><span>arg2:</span><input id="arg2" type="text" /></p>
        //     <input type="button" value="aaa" />
        // </div>

        var group = document.createElement("div");
        group.style.position = "absolute";
        group.style.left = "0px";
        group.style.top = (length * 160 + 40) + "px";
        group.style.width = "100%";
        group.style.height = "150px";
        group.style.background = "gray";
        div.appendChild(group);

        var p1 = document.createElement("p");
        group.appendChild(p1);

        var span1 = document.createElement("span");
        span1.innerText = "arg1: ";
        p1.appendChild(span1);

        var input1 = document.createElement("input");
        input1.type = "text";
        p1.appendChild(input1);

        var p2 = document.createElement("p");
        group.appendChild(p2);

        var span2 = document.createElement("span");
        span2.innerText = "arg2: ";
        p2.appendChild(span2);

        var input2 = document.createElement("input");
        input2.type = "text";
        p2.appendChild(input2);

        var btn = document.createElement("input");
        btn.type = "button";
        btn.style.position = "absolute";
        btn.style.color = "white";
        btn.style.background = "blue";
        btn.style.width = "80%";
        btn.style.left = "10%";
        btn.value = name;
        group.appendChild(btn);
        btn.onclick = function () {
            if (ctx) {
                func.call(ctx, input1.value, input2.value);
            } else {
                func(input1.value, input2.value);
            }
        };

        list.push([name, func, ctx]);
    }
    testcase.register = register;

})(testcase || (testcase = {}));