from package.YouTube_Download import YouTube_Download
from enum import Enum
import os
def input_select(word):
    SELECT_LIST = ["video", "audio", "playlist"]
    while True:
        select = input(word)
        if select.lower() in SELECT_LIST:
            return select.lower()
        os.system('cls')
        print("[ERROR] Not a accuracy select...")
        print(10*"-"+"Please Input"+10*"-")
        for i in SELECT_LIST:
            print(i)
        print(32*"-")
if __name__ == "__main__":
    yt = YouTube_Download()
    try:
        #yt.set_output_path(input("Input output path:"))
        yt.set_output_path(r"C:\Users\eee12\Desktop")
        url = "https://www.youtube.com/watch?v=bhkfm1dX7BM&list=PLpBqtLy3mHw07nf_D8u-g6a3_MdLWVdIc&index=1"
        #url = yt.input_url("Input YouTube URL:")
        
        select = input_select("Input donload type:")
        if select == "video":
            yt.download_video(url)
        elif select == "audio":
            yt.download_audio(url)
        elif select == "playlist" and yt.is_YouTube_playlist_URL(url):
            if input("video or audio?:").lower() == "video":
                yt.download_playlist(url, "video")
            else:
                yt.download_playlist(url, "audio")
        else:
            print("[ERROR] The URL do not have playlist.")
    except ValueError:
        print("[ERROR] ValueError...")