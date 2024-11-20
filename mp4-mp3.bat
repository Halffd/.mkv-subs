
echo off
for %%a in (*.mp4) do ffmpeg -i "%%a" -b:a 320K -vn "%%a.mp3"
pause