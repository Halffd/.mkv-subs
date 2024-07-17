@ECHO OFF
REM for %%f in (.mkv) do %mkvmerge% @options.json -o mkvmerge_out%%f %%f

:start
set t=ass
set type=srt
echo ==========
set i=1
set fn=0
dir
for %%a in (*.%t%) do (
	echo "%%a"
	set fn=%%a
        ffmpeg -i "%CD%\%%a" "%%a.%type%"
)
copy /Y C:\Users\halff\OneDrive\Documents\.scriptbat\subs.py %CD%\subs.py
py subs.py
echo ===========
rem goto start
pauseE:\UchoutenKazoku	