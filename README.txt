#need ffmpeg.exe#

pyinstaller app.py --onedir --noconsole --icon="icon/i.ico"
pip freeze -l > requirements.txt

參考資料: https://tw.coderbridge.com/@WeiHaoEric/0b2ced0696cc4c38a62d7b26fa7bbea0