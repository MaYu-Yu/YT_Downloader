from pytube import YouTube
from YouTube_Download import YouTube_Download
if __name__ == '__main__':
    yt = YouTube_Download()
    url="https://www.youtube.com/watch?v=dx7p3gjSn4k"
    yt.download_video(url)