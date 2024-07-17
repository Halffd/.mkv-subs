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
copy /Y "C:\Users\halff\OneDrive\Documents\.scriptbat\quicksrt=-ass.bat" %CD%\convert.bat
copy /Y C:\Users\halff\OneDrive\Documents\.scriptbat\subsdelay.bat %CD%\subsdelay.bat
copy /Y C:\Users\halff\OneDrive\Documents\.scriptbat\quickdefault.bat %CD%\quickdefault.bat
set /p track=Track: 
set type=srt
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
			C:\Users\halff\OneDrive\Documents\.bat\mkvextract.exe "%%f" tracks %track%:"%%f.%type%"
		)
)

echo ===========
rem goto start
pause
