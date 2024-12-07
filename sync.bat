@echo off
setlocal enabledelayedexpansion

set "FFMPEG_PATH=ffmpeg"
set "FFS_PATH=ffs"
set "DIRECTORY=%CD%"

set count=0
mkdir Backup
for %%F in ("%DIRECTORY%\*.srt") do (
    set /a count+=1
    echo %%F !count!
    copy "%%F" "%CD%\Backup\%%~nxF"
    rename "%%F" "!count!.srt"
)
pause
set count=0
for %%F in ("%DIRECTORY%\*.mkv") do (
    set /a count+=1
    set "MKV_FILE=%%F"
    
    rem Construct the corresponding SRT filename
    set "SRT_FILE=!DIRECTORY!\!count!.srt"
    
    if exist "!SRT_FILE!" (
        echo Running FFS for !MKV_FILE!
        "%FFS_PATH%" "!MKV_FILE!" -i "!SRT_FILE!" -o "!SRT_FILE!_sync.srt"
        rem "%FFS_PATH%" "%FFMPEG_PATH%" -i "!MKV_FILE!" -s "!SRT_FILE!"
    ) else (
        echo No SRT file found for !MKV_FILE!
    )
)

endlocal
pause