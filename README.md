# Write a YouTube downloader in python

https://user-images.githubusercontent.com/59922656/188065052-f87725e8-decd-4d33-a816-a99e9cbcbf99.mp4

pytube API: https://pytube.io/en/latest/

pyQt6 : https://doc.qt.io/qtforpython/index.html

學習pyQt6 : https://blog.csdn.net/weixin_42290927/article/details/112918767#t0

打包使用庫: pip freeze -l > requirements.txt

下載使用庫: pip install -r requirements.txt

打包資料: pyinstaller app.py --onedir --noconsole --icon="icon/i.ico"

打包參考: https://tw.coderbridge.com/@WeiHaoEric/0b2ced0696cc4c38a62d7b26fa7bbea0

IF ffmpeg console跑出來 ： https://stackoverflow.com/questions/62968888/how-to-hide-console-output-of-ffmpeg-in-python/71741286#71741286
ffmpeg中找到_probe.py _run.py

p = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

return subprocess.Popen(
    args, shell=True, stdin=subprocess.PIPE, stdout=stdout_stream, stderr=stderr_stream
)

下載失敗BUG#1 參考:https://github.com/pytube/pytube/issues/1707

pytube庫中找到cipher.py

r'var {nfunc}\s*=\s*(\[.+?\]);'.format(

去掉分號：

r'var {nfunc}\s*=\s*(\[.+?\])'.format(

下載失敗BUG#2 參考:https://github.com/pytube/pytube/pull/2023

pytube庫中找到cipher.py

r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'

改成：

r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&.*?\|\|\s*([a-z]+)',
r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',  