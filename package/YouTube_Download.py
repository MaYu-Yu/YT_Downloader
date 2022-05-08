from email.mime import audio
import os
from tkinter.ttk import Progressbar

from pytube import YouTube
from pytube import Playlist
import ffmpeg
import pyperclip # clipboard
import re
from pathlib import Path

class YouTube_Download:
    DEFAULT_PATH = Path(str(Path.home() / "Downloads"))
    def __init__(self, output_path=DEFAULT_PATH):
        self.output_path = output_path
        self.stream_dict = {}
        self.yt_info = {}
# setting
    def set_YouTube(self, url="https://www.youtube.com/watch?v=dx7p3gjSn4k"):
        self.yt = YouTube(url, on_progress_callback=self.my_progress_bar)
        self.yt_info.update({"title":self.yt.title, 
                        "thumbnail_url": self.yt.thumbnail_url,
                        "play_len": self.yt.length,
                        # "author": self.yt.author,
                        # "captions": self.yt.captions,# 字幕
                        # "publish_date": self.yt.publish_date,
                        # "views": self.yt.views
                        })
        for res in ["4320p", "2160p", "1080p", "720p", "480p"]:
            video_obj = self.yt.streams.filter(mime_type="video/mp4",res=res).first()
            if video_obj != None:
                self.stream_dict.update({video_obj.resolution:{"obj":video_obj, 
                                                            "file_size": video_obj.filesize
                                                            }})
        audio_obj = self.yt.streams.get_audio_only() 
        self.stream_dict.update({"audio":{ "obj":audio_obj, 
                                                "abr": audio_obj.abr,
                                                "file_size": video_obj.filesize
                                                }})
        for key, val in self.yt_info.items():
            print(str(key), " : ", str(val))
        for key in self.stream_dict.keys():
            print("type :", self.stream_dict[key]["obj"])
            print("file_size :", str(self.stream_dict[key]["file_size"]))
            
    def set_output_path(self, path):
        """Vaild path"""
        
        path = Path(path)
        #path = Path(filedialog.askdirectory())
        if path.exists():
            self.output_path = path
        else:
            print("The Path is not exist.\n Default Download Path is ", self.output_path)
# vaild
    def is_YouTube_URL(self, url):
        """Vaild YouTube's URL."""
        
        return True if self.get_video_ID(url) != None else False
    def is_YouTube_playlist_URL(self, url):
        """Vaild YouTube's playlist URL."""
        
        return True if self.get_playlist_ID(url) != None else False
    def input_url(self, word):
        """Vaild input string"""
        # url = pyperclip.paste()
        # print("Read ClipBoard :", url)   
        while True:
            try:
                url = input(word)
            except ValueError:
                print("[ERROR] ValueError... Please enter the correct YouTube URL...")
                continue
            if self.is_YouTube_URL(url): # Vaild OK
                break
            else:
                print("[ERROR] Not a YouTube URL... Please enter the correct YouTube URL...")
        return url    
# self.yt re
    def get_playlist_ID(self, url):
        """It will return YouTube's Playlist ID"""
        
        youtube_regex = r"[?&]list=(?P<list>([^&]+))"
        sreMatch = re.search(youtube_regex, url)
        return sreMatch.group("list") if sreMatch != None else None
    def get_video_ID(self, url):
        """It will return YouTube's ID"""
            
        youtube_regex = r"^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))(?P<video_ID>(\w|-)[^&]+)(?:\S+)?$"
        sreMatch = re.match(youtube_regex, url)
        return sreMatch.group("video_ID") if sreMatch != None else None
# download    
    def my_progress_bar(self, stream, chunk, data_remaining):
        """progress_callback to use"""
        total_size = stream.filesize
        current = ((total_size - data_remaining) / total_size)
        percent = ('{0:.1f}').format(current*100)
        progress = int(50*current)
        status = '█' * progress + '-' * (50 - progress)
        print(' ↳ |{bar}| {percent}%\r'.format(bar=status, percent=percent), end='', flush=True)

    def download_playlist(self, url, download_type="video"):
        """Download all files in playlist from YouTube"""
        
        if not self.is_YouTube_playlist_URL(url): 
            print("[ERROR] Not a YouTube playlist URL... Please enter the correct YouTube URL...")
            return 
        index = 0
        playlist = Playlist(url)
        download_type = True if download_type == "video" else False # True = download Video False = download Audio
        for url in playlist.video_urls:
            index+=1
            print("Download "+str(index)+" from playlist.")
            if download_type:
                self.download_video(url)
            else:
                self.download_audio(url) 
    def download_video(self, url):
        """Download a video from YouTube"""
        
        def check_audio(file_name):
            """Check if video have audio or not"""
            
            p = ffmpeg.probe(file_name, select_streams='a')
            return p['streams']
        def merge(out, video, audio):
            """Merge audio & video"""
            
            ffvideo = ffmpeg.input(video)
            ffaudio = ffmpeg.input(audio)
            ffmpeg.concat(ffvideo, ffaudio, v=1, a=1) \
                .output(out) \
                .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            os.remove(video)
            os.remove(audio)
            print("Merge Output:", self.output_path)
        try:
            if not self.is_YouTube_URL(url): 
                print("[ERROR] Not a YouTube URL... Please enter the correct YouTube URL...")
                return
            self.set_YouTube(url)
        # Select Resolution
            while True:
                print("-"*7 + "Select Resolution" + "-"*7)
                for key in self.stream_dict.keys():
                    if key == "audio": continue
                    print(key)
                print("-"*34)
                try: 
                    res = input("Input:")
                except ValueError:
                    os.system('cls')
                    print("[ERROR] Not a accuracy select...")
                    continue
                if res in self.stream_dict.keys(): break
                
            out = self.stream_dict[res]["obj"].download(output_path=self.output_path, skip_existing=True)
            if not check_audio(out):
            # provent duplicate name
                video_out = self.output_path / "temp_video.mp4"
                if video_out.exists():
                    os.remove(video_out)
                os.rename(out, video_out)
                audio_out = self.download_audio(url, Flag_temp=True)
                merge(out, video_out, audio_out)
            return out
        except ffmpeg.Error as e:
            print(e.stdout)
            print(e.stderr)
            return None
        except Exception as e:
            print(e)
            print("[ERROR] Download video Failed.")
            return None
    def download_audio(self, url, Flag_temp=False):
        """Download a audio from YouTube"""
        if not self.is_YouTube_URL(url): 
            print("[ERROR] Not a YouTube URL... Please enter the correct YouTube URL...")
            return
        try:
            if Flag_temp:
                if (self.output_path / "temp_audio.mp4").exists(): 
                    os.remove(self.output_path / "temp_audio.mp4")
                out = self.stream_dict["audio"]["obj"].download(output_path=self.output_path,
                                                                filename="temp_audio.mp4")
            else:
                self.set_YouTube(url)
                out = self.stream_dict["audio"]["obj"].download(output_path=self.output_path, 
                                                                filename=self.yt_info["title"]+'.mp3', skip_existing=True)
            return out
        except Exception as e:
            print(e)
            print("[ERROR] Download audio Failed.")
            return None