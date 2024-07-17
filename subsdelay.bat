set /P dl=Delay(seconds-+>) : 
set /P t=Type: 
copy /Y C:\Users\halff\OneDrive\Documents\.scriptbat\subs.py
py subs.py %dl% %t%
pause