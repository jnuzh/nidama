@echo off

if exist "%DCSDK_HOME%\upgrade_temp\upgrade.rdy" goto upgrade
goto end


:upgrade
rd /S /Q %DCSDK_HOME%\conf
rd /S /Q %DCSDK_HOME%\db
rd /S /Q %DCSDK_HOME%\lib
rd /S /Q %DCSDK_HOME%\logs

move /Y %DCSDK_HOME%\upgrade_temp\upgrade_unziped\DC_SDK\conf  %DCSDK_HOME%\conf
move /Y %DCSDK_HOME%\upgrade_temp\upgrade_unziped\DC_SDK\db  %DCSDK_HOME%\db
move /Y %DCSDK_HOME%\upgrade_temp\upgrade_unziped\DC_SDK\lib  %DCSDK_HOME%\lib
move /Y %DCSDK_HOME%\upgrade_temp\upgrade_unziped\DC_SDK\logs  %DCSDK_HOME%\logs

rd /S /Q %DCSDK_HOME%\upgrade_temp


:end 

