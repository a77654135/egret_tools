declare var testcase;
module test {

    testcase.register("roll", function (arg1, arg2) {
        Net.sendMessage(CmdConst.ADVICE, { "text": "~roll," + arg1 });
    });

    testcase.register("clean", function (arg1, arg2) {
        Net.sendMessage(CmdConst.ADVICE, { "text": "~clean,1" });
    });

    
}