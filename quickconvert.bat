@ECHO OFF
REM for %%f in (.mkv) do %mkvmerge% @options.json -o mkvmerge_out%%f %%f

:start
copy /Y C:\Users\halff\OneDrive\Documents\.scriptbat\subs.py
copy /Y C:\Users\halff\OneDrive\Documents\.scriptbat\quicksrt=-ass.bat %CD%\quicksrt=-ass.bat
copy /Y C:\Users\halff\OneDrive\Documents\.scriptbat\subsdelay.bat %CD%\subsdelay.bat
copy /Y C:\Users\halff\OneDrive\Documents\.scriptbat\quickdefault.bat %CD%\quickdefault.bat

set /p t=Type: 
set /p type=Convert to: 
echo ==========
set i=1
dir
for %%a in (*.%t%) do (
		echo "%%a"
        E:\.bat\ffmpeg.exe -i "%f%\%%a" "%%a.%type%"
)
rem ffmpeg -i %subin% -c:s srt .\%type%
REM mkvextract --ui-language en tracks "%~dpn1.mkv" !line! ||(ECHO Demuxing error!&GOTO:eof)
echo ===========
rem goto start
pause