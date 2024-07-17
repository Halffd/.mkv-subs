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
set /p type=Type: 
echo ==========
set i=1
dir
for %%f in (*.mkv) do (
		echo "%%f"
		if %track% EQU -1 ( 
			mkvinfo.exe "%%f" > info.txt
			start "D:\Program Files\Sublime Text 3\sublime_text.exe" info.txt
			goto start
		) else (
			C:\Users\halff\OneDrive\Documents\.bat\mkvextract.exe "%%f" tracks %track%:"%%f.%type%"
		)
)
for %%f in (*.mp4) do (
		echo "%%f"
		if %track% EQU 0 ( 
			C:\Users\halff\OneDrive\Documents\.bat\mkvinfo.exe "%%f"
			goto start
		) else (
			C:\Users\halff\OneDrive\Documents\.bat\mkvextract.exe "%%f" tracks %track%:"%%f.%type%"
		)
)
:startc
set f=%folder% 
set t=%type%
set type=srt
echo ==========
REM mkvextract --ui-language en tracks "%~dpn1.mkv" !line! ||(ECHO Demuxing error!&GOTO:eof)
echo ===========
goto start
pause
