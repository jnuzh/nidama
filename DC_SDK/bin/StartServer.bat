@echo off

setlocal

set DCSDK_HOME=%~dp0..

for %%x in ("%DCSDK_HOME%") do set DCSDK_HOME=%%~sx

if not exist "%DCSDK_HOME%\upgrade_temp\upgrade.rdy" goto start
call "Upgrade.bat"

:start
set TEMP_JAVA_HOME=%DCSDK_HOME%\jre

if exist "%TEMP_JAVA_HOME%\bin\java.exe" set JAVA_HOME=%TEMP_JAVA_HOME%
if exist "%JAVA_HOME%\bin\java.exe" goto JavaFound
echo JAVA_HOME does not point at a JDK or JRE.  Either set the JAVA_HOME environment variable or specify a JDK.
goto end 

:JavaFound
set JETTY_HOME=%DCSDK_HOME%\lib\jetty
set JAVA_OPTS=-DDCSDK_HOME=%DCSDK_HOME% -Dfile.encoding=GBK -Dmain.class=com.taobao.dc.sdk.Main -DSTART=%DCSDK_HOME%\conf\start.config
 
for %%a in (%JETTY_HOME%\start*.jar) do  set START_JAR=%%a
if not "%START_JAR%"=="" goto StartJarFound
echo start.jar was not found.  Check your SDK installation.
goto end 

:StartJarFound
set JETTY_OPTS=-jar %START_JAR%  %DCSDK_HOME%\conf\jetty.xml
goto JettyOptsSet

:JettyOptsSet
if defined JAVA_OPTS set JETTY_OPTS=%JAVA_OPTS% %JETTY_OPTS%

set PWD=%CD%
cd /d "%JETTY_HOME%"

"%JAVA_HOME%\bin\java.exe" %JETTY_OPTS% 

cd /d "%PWD%"

goto end 

:end
