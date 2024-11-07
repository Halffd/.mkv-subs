@echo on
set fps=--disable-fps-guessing
set split=10
set /p video=Video 
set /p srt=Srt 
set /p out=Out Srt 
rem Subtitle Syncing
rem     alass "[video].mkv" "[subtitle].srt" "[correctedd_subtitle].srt" --disable-fps-guessing --split-penalty 10
alass %video% %srt% %out% %fps% --split-penalty %split%
rem alass "e:\pokemon 2019\[Some-Stuffs]_Pocket_Monsters_(2019)_022_(1080p)_[DB795476].mkv" "c:\Users\halff\Documents\Subs\pokemon 2019\[Some-Stuffs]_Pocket_Monsters_(2019)_022_(1080p)_[DB795476].2-some.2019_.srt-Sync.srt" 22ss.srt --disable-fps-guessing --split-penalty 10