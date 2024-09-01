@echo off
echo Starting to package the application...
pyinstaller -wD --exclude scipy -i tool.ico rtt_t2.py
echo Packaging complete!
pause