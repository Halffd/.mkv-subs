set /p subtitle_ass_file="subtitles.ass "
set /p video_to_hardsub="video.mp4 "
set constant_rate_factor=20

ffmpeg.exe -i %video_to_hardsub% -crf %constant_rate_factor% -vf ass=%subtitle_ass_file% subtitled.mp4
pause