
import os
from pytube import YouTube
from pytube import Playlist
import ffmpeg
import re, time
from pathlib import Path
import threading
class YouTube_Download:
    DEFAULT_PATH = Path(str(Path.home() / "Downloads"))
    def __init__(self, output_path=DEFAULT_PATH):
        self.__output_path = output_path
        self.stream_dict = {}
        self.info = {}
        self.progress = [0]*100
        self.num = 0
    def add_num(self):
        self.num = self.num if self.num < 100 else 0
        
    def my_progress_bar(self, stream, chunk, data_remaining):
        """progress_callback to use"""
        
        total_size = stream.filesize
        current = ((total_size - data_remaining) / total_size)
        #percent = ('{0:.1f}').format(current*100)
        self.progress[self.num] = int(50*current) - 1
        #status = '█' * self.progress[self.num] + '-' * (50 - self.progress[self.num])
        #print(' ↳ |{bar}| {percent}%\r'.format(bar=status, percent=percent), end='', flush=True)
 
    def set_YouTube(self, url):
        if not self.is_YouTube_URL(url): return 
        self.yt = YouTube(url, on_progress_callback=self.my_progress_bar)
        self.info.update({"title":self.yt.title, 
                        "thumbnail_url": self.yt.thumbnail_url,
                        "author": self.yt.author,
                        # "captions": self.yt.captions,# 字幕
                        "publish_date": self.yt.publish_date,
                        "views": self.yt.views,
                        "play_len": self.yt.length
                        })
        for res in ["4320p", "2160p", "1080p", "720p", "480p"]:
            video_obj = self.yt.streams.filter(mime_type="video/mp4",res=res).first()
            if video_obj != None:
                self.stream_dict.update({res.replace("p", ""):{"obj":video_obj, 
                                                            "file_size": video_obj.filesize
                                                            }})
        audio_obj = self.yt.streams.get_audio_only() 
        self.stream_dict.update({"audio":{ "obj":audio_obj, 
                                                "abr": audio_obj.abr,
                                                "file_size": video_obj.filesize
                                                }})
            
    def set_output_path(self, path):
        """Vaild path"""
        
        path = Path(path)
        #path = Path(filedialog.askdirectory())
        if path.exists():
            self.__output_path = path
        else:
            print("The Path is not exist.\n Default Download Path is ", self.__output_path)
# vaild
    def is_YouTube_URL(self, url):
        """Vaild YouTube's URL."""
        
        if self.get_video_ID(url) != None:
            return True 
        else: 
            print("[ERROR] Not a YouTube URL... Please enter the correct YouTube URL...")
            return False
    def is_YouTube_playlist_URL(self, url):
        """Vaild YouTube's playlist URL."""
        
        if self.get_playlist_ID(url) != None:
            return True 
        else: 
            print("[ERROR] Not a YouTube playlist URL... Please enter the correct YouTube URL...")
            return False
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
    def add_download_json(self):
        pass


    def download_playlist(self, url, num, download_type="audio"):
        """Download all files in playlist from YouTube"""
        
        if not self.is_YouTube_playlist_URL(url): return None
        playlist = Playlist(url)
        for url in playlist.video_urls:
            self.add_num()
            print("Download "+str(num)+" from playlist.")
            if download_type == "audio":
                self.download_audio(url, num)
            else:
                self.download_video(url, num, download_type)
        return True
    def download_video_thread(self, url, num, res):
        t = threading.Thread(target=self.download_video, args =(url,num,res,))
        t.start()
    def download_video(self, url, num, res):
        """Download a video from YouTube"""
        
        def check_audio(file_name):
            """Check if video have audio or not"""
            
            p = ffmpeg.probe(file_name, select_streams='a')
            return p['streams']
        def merge(out, video, audio, num):
            """Merge audio & video"""
            self.progress[num] = 99
            ffvideo = ffmpeg.input(video)
            ffaudio = ffmpeg.input(audio)
            ffmpeg.concat(ffvideo, ffaudio, v=1, a=1) \
                .output(out) \
                .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            os.remove(video)
            os.remove(audio)
            print("Merge Output:", self.__output_path)
        try:
            if not self.is_YouTube_URL(url): return
            self.add_num()
            if res == "8787": 
                out = self.stream_dict["audio"]["obj"].download(output_path=self.__output_path, skip_existing=True)#audio
            else:
                out = self.stream_dict[res]["obj"].download(output_path=self.__output_path, skip_existing=True)

            if not check_audio(out):
            # provent duplicate name https://www.youtube.com/watch?v=Z2RYzmU6pV0&list=LL&index=1
                video_out = Path(self.__output_path / ("temp_video"+str(num)+".mp4"))

                if video_out.exists():
                    os.remove(video_out)
                video_out = str(video_out)
                os.rename(out, video_out)
                audio_out = self.download_audio(url, num, Flag_temp=True)
                merge(out, video_out, audio_out, num)
            self.progress[num] = 100
            time.sleep(1)
            return out
        except ffmpeg.Error as e:
            print(e.stdout)
            print(e.stderr)
            return None
        # except Exception as e:
        #     print(e)
        #     print("[ERROR] Download video Failed.")
        #     return None
    def download_audio_thread(self, url, num):
        t = threading.Thread(target=self.download_audio, args =(url,num,))
        t.start()
    def download_audio(self, url, num=0, Flag_temp=False):
        """Download a audio from YouTube"""
        if not self.is_YouTube_URL(url): return
        try:
            self.add_num()
            if Flag_temp:
                temp_name = Path(str(num)+"temp_audio.mp4")
                if (self.__output_path / temp_name).exists(): 
                    os.remove(self.__output_path / "temp_audio.mp4")
                out = self.stream_dict["audio"]["obj"].download(output_path=self.__output_path,
                                                                filename=str(temp_name))
            else:
                self.set_YouTube(url)
                out = self.stream_dict["audio"]["obj"].download(output_path=self.__output_path, 
                                                                filename=self.info["title"].replace('/', '')+'.mp3', skip_existing=True)
            print(out)
            self.progress[num] = 100
            time.sleep(1)
            return out
        except Exception as e:
            print(e)
            print("[ERROR] Download audio Failed.")
            return None
        