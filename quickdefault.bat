@ECHO OFF
REM for %%f in (.mkv) do %mkvmerge% @options.json -o mkvmerge_out%%f %%f

for %%f in (*.mkv) do (
		echo "%%f"
		C:\Users\halff\OneDrive\Documents\.bat\mkvinfo.exe "%%f" > info.txt
		start "D:\Program Files\Sublime Text 3\sublime_text.exe" info.txt
		goto start
)
:start
copy /Y C:\Users\halff\OneDrive\Documents\.scriptbat\subs.py
copy /Y C:\Users\halff\OneDrive\Documents\.scriptbat\quicksrt=-ass.bat %CD%\quicksrt=-ass.bat
copy /Y C:\Users\halff\OneDrive\Documents\.scriptbat\subsdelay.bat %CD%\subsdelay.bat
copy /Y C:\Users\halff\OneDrive\Documents\.scriptbat\quickdefault.bat %CD%\quickdefault.bat

set /p track=Track: 
echo ==========
set i=1
dir
for %%f in (*.mkv) do (
		echo "%%f"
		if %track% EQU -1 ( 
			C:\Users\halff\OneDrive\Documents\.bat\mkvinfo.exe "%%f" > info.txt
			start "D:\Program Files\Sublime Text 3\sublime_text.exe" info.txt
			goto start
		) else (
			C:\Users\halff\OneDrive\Documents\.bat\mkvmerge.exe -o "%%f.mkv" --atracks %track% "%%f"
			rem C:\Users\halff\OneDrive\Documents\.bat\mkvmerge.exe -o "%%f.mkv" --default-track %track%:yes "%%f"
			REM --default-track 4:yes --default-track 3:no --default-track 2:no --default-track 1:no "%%f"
		)
)
:startc
REM mkvextract --ui-language en tracks "%~dpn1.mkv" !line! ||(ECHO Demuxing error!&GOTO:eof)
echo ===========
pause