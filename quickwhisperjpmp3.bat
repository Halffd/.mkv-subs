@echo on
for %%F in (*.mp3) do (
  echo Processing: %%F
  whisper "%%F" --language ja --model large-v2 --task transcribe --output_format srt  > %%F.ja.srt
)
pause