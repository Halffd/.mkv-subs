@ECHO OFF
REM for %%f in (.mkv) do %mkvmerge% @options.json -o mkvmerge_out%%f %%f

:start
set t=ssa
set type=srt
copy /Y C:\Users\halff\Documents\.scriptbat\subs.bat %CD%\subs.bat
copy /Y C:\Users\halff\Documents\.scriptbat\subs.py
echo ==========
set i=1
set fn=0
dir
for %%a in (*.%t%) do (
	echo "%%a"
	set fn=%%a
        ffmpeg -i "%CD%\%%a" "%%a.%type%"
)
py subs.py
echo ===========
rem goto start
pause