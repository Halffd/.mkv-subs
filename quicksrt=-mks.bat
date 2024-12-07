@ECHO OFF
REM for %%f in (.mkv) do %mkvmerge% @options.json -o mkvmerge_out%%f %%f

:start
set t=mks
set type=srt
echo ==========
set i=1
dir
for %%a in (*.%t%) do (
		echo "%%a"
        ffmpeg -i "%CD%\%%a" "%%a.%type%"
)
rem ffmpeg -i %subin% -c:s srt .\%type%
REM mkvextract --ui-language en tracks "%~dpn1.mkv" !line! ||(ECHO Demuxing error!&GOTO:eof)
echo ===========
rem goto start
pause