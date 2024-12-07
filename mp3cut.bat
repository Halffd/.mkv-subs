@echo on

set /p start="Enter the start time (hh:mm:ss): "
set /p end="Enter the duration time (hh:mm:ss): "

REM Convert start and end times to seconds
for /f "tokens=1-3 delims=:" %%a in ("%start%") do (
  set /a "start_sec=%%a*3600 + %%b*60 + %%c"
)
for /f "tokens=1-3 delims=:" %%a in ("%end%") do (
  set /a "end_sec=%%a*3600 + %%b*60 + %%c"
)
echo %start_sec$ $end_sec%
REM Iterate over every MP3 file in the directory
for %%F in (*.mp3) do (
  echo Processing: %%F
  ffmpeg -ss %start_sec% -t %end_sec% -i "%%F" -codec:a libmp3lame "output_%%F"
)

echo Trimming complete.
pause