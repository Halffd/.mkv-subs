@ECHO OFF
REM for %%f in (.mkv) do %mkvmerge% @options.json -o mkvmerge_out%%f %%f

:start
set /p folder=Folder: 
echo ==========
set i=1
cd /D %folder%
dir
for %%f in (*.avi) do (
		echo "%%f"
		C:\Users\halff\OneDrive\Documents\.bat\ffmpeg.exe -i "%%f" "%%f.mp3"
)
for %%f in (*.mp4) do (
		echo "%%f"
		C:\Users\halff\OneDrive\Documents\.bat\ffmpeg.exe -i "%%f" "%%f.mp3"
)
for %%f in (*.m4a) do (
		echo "%%f"
		C:\Users\halff\OneDrive\Documents\.bat\ffmpeg.exe -i "%%f" "%%f.mp3"
)
for %%f in (*.mkv) do (
		echo "%%f"
		D:\Gustavo\Arquivos\Downloads\Videos\Anm\.bat\ffmpeg.exe -i "%%f" "%%f.mp3"
)

REM mkvextract --ui-language en tracks "%~dpn1.mkv" !line! ||(ECHO Demuxing error!&GOTO:eof)
echo ===========
pause
