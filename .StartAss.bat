@ECHO OFF
REM for %%f in (.mkv) do %mkvmerge% @options.json -o mkvmerge_out%%f %%f
rem for %%f in (*.mkv) do (
rem		echo "%%f"
rem		C:\Users\halff\OneDrive\Documents\.bat\mkvinfo.exe "%%f" > info.txt
rem		start "D:\Program Files\Sublime Text 3\sublime_text.exe" info.txt
rem		goto start
rem)
:start

copy /Y "C:\Users\halff\OneDrive\Documents\.scriptbat\subs.py"
copy /Y "C:\Users\halff\OneDrive\Documents\.scriptbat\quicksrt=-ass.bat"
copy /Y "C:\Users\halff\OneDrive\Documents\.scriptbat\subsdelay.bat"
copy /Y "C:\Users\halff\OneDrive\Documents\.scriptbat\quickdefault.bat"

set type=ass
echo ==========
set i=1
dir
for %%f in (*.mkv) do (
    echo "%%f"
    if "%track%" EQU "-1" ( 
        C:\Users\halff\OneDrive\Documents\.bat\mkvinfo.exe "%%f" > info.txt
        start "D:\Program Files\Sublime Text 3\sublime_text.exe" info.txt
        goto start
    ) else (
        for /f "usebackq tokens=2,* delims=:" %%a in (`C:\Users\halff\OneDrive\Documents\.bat\mkvinfo.exe "%%f" ^| findstr /C:"mkvextract: "`) do (
            echo id: %%a
            for /f "usebackq tokens=1,2,* delims=: " %%x in (`C:\Users\halff\OneDrive\Documents\.bat\mkvinfo.exe "%%f" -t %%b ^| findstr /C:"subtitles"`) do (
                echo subs: %%v
                C:\Users\halff\OneDrive\Documents\.bat\mkvextract.exe "%%f" tracks %%a:"%%~nf.%%a.%type%"
                ffmpeg -i "%%~nf.%%a.%type%" "%%~nf.%%a.srt"
            )
        )
    )
)

:startc
set t=ass
set type=srt
echo ==========
set i=1
dir
echo ===========
rem goto start
call quicksrt=-ass.bat
echo ===========
rem goto start
pause
