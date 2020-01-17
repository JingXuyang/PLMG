@echo off

set CURRENT_DIR=%cd%

rem "cd /d %~sdp0" 就表示进入批处理文件所在的文件夹中
cd /d %~dp0
rem "cd .." 返回上级目录
cd ..

set XSYH_ROOT_PATH=%cd%
set XSYH_THIRDPARTY_PATH=%XSYH_ROOT_PATH%\thirdparty
set PROJECT_ROOT_PATH=C:\projects

cd /d %CURRENT_DIR%

set DATABASE=CGTeamwork

set PYTHONPATH=%XSYH_ROOT_PATH%;%XSYH_ROOT_PATH%\main;%XSYH_THIRDPARTY_PATH%;

rem TODO: %* 测试传参数的问题
%~sdp0\python.bat %XSYH_ROOT_PATH%\main %*