set artRoot=E:\study\code\EgretProjects\art
set resRoot=E:\study\code\EgretProjects\league\resource\assets

del %resRoot%\*.* /S /Q
cd %resRoot%
rd . /S /Q

xcopy /Y /R /E %artRoot%\*.* %resRoot%\

TextureMerger.exe -p %resRoot%\common -o %resRoot%\common.json
TextureMerger.exe -p %resRoot%\common_new -o %resRoot%\common_new.json
TextureMerger.exe -p %resRoot%\hall -o %resRoot%\hall.json
TextureMerger.exe -p %resRoot%\login -o %resRoot%\login.json

rd %resRoot%\common /S /Q
rd %resRoot%\common_new /S /Q
rd %resRoot%\hall /S /Q
rd %resRoot%\login /S /Q

pause