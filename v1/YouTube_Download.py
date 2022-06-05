
import os, ffmpeg, re, time
from pytube import YouTube, Playlist
from pathlib import Path
import threading
class YouTube_Download:
    DEFAULT_PATH = Path(str(Path.home() / "Downloads"))
    def __init__(self, output_path=DEFAULT_PATH):
        self.__output_path = output_path
        self.stream_dict = {}
        self.info = {}
        self.progress = {}
       # .stat().st_size
    def my_progress_bar(self, stream, chunk, data_remaining):
        """progress_callback to use"""
        
        total_size = stream.filesize
        current = 2*int(50*((total_size - data_remaining) / total_size)) - 1
        self.progress[stream] = current
        print(stream, self.progress[stream])
        #status = '█' * self.progress + '-' * (50 - self.progress)
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
        self.stream_dict.update({"8787":{ "obj":audio_obj, 
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
        
# re
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
        pass#https://www.youtube.com/watch?v=aWSaIdLUE0Y&list=PLrkROcixCaaxXUVn7ATqbqAZMIO_4IXrH&index=1
    def get_playlist_url(self, url):
        playlist = Playlist(url)
        return playlist.video_urls
        
            
    # def download_playlist(self, url, download_type):
    #     """Download all files in playlist from YouTube"""
        
    #     if not self.is_YouTube_playlist_URL(url): return None
    #     playlist = Playlist(url)
    #     print("playlist length =  ", str(len(playlist.video_urls)))
    #     for url in playlist.video_urls:
    #         if download_type == "8787":
    #             self.download_audio(url)
    #         else:
    #             self.download_video(url, download_type)
    #     return True
    def download_thread(self, url, res):
        if res == "8787":
            t = threading.Thread(target=self.download_audio, args =(url,))
        else:
            t = threading.Thread(target=self.download_video, args =(url,res,))
        t.start()
    def download_video(self, url, res):
        """Download a video from YouTube"""
        def merge(out, video, audio):
            """Merge audio & video"""
            try: 
                ffvideo = ffmpeg.input(video)
                ffaudio = ffmpeg.input(audio)
                ffmpeg.concat(ffvideo, ffaudio, v=1, a=1) \
                    .output(out) \
                    .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
                os.remove(video)
                os.remove(audio)
            except ffmpeg.Error as e:
                print("[ERROR] Merge audio & video error.")
                #print(e.stdout)
                #print(e.stderr)
            print("Merge Output:", out)
        try:
            if not self.is_YouTube_URL(url): return
            stream = self.stream_dict[res]["obj"]
            self.progress.update({stream: 0})
            out = stream.download(output_path=self.__output_path, skip_existing=True)
            if stream.includes_video_track: # only video
                video_out = Path(self.__output_path / (str(round(time.time()))+"_video.mp4"))
                if video_out.exists():
                    os.remove(video_out)
                video_out = str(video_out)
                os.rename(out, video_out)
                audio_out = self.download_audio(url, Flag_temp=True)
                merge(out, video_out, audio_out)
            self.progress[stream] = 100
            return out
        except Exception as e:
            print(e)
            print("[ERROR] Download video Failed.")
            return None
    def download_audio(self, url, Flag_temp=False):
        """Download a audio from YouTube"""
        if not self.is_YouTube_URL(url): return
        try:
            stream = self.stream_dict["8787"]["obj"] 
            self.progress.update({stream: 0})
            if Flag_temp:
                temp_name = Path(str(round(time.time()))+"_audio.mp4")
                if (self.__output_path / temp_name).exists(): 
                    os.remove(self.__output_path / temp_name)
                out = stream.download(output_path=self.__output_path,
                                        filename=str(temp_name))
            else:
                out = stream.download(output_path=self.__output_path, 
                                        filename=self.info["title"].replace('/', '')+'.mp3', skip_existing=True)
                self.progress[stream] = 100
            print(out)
            return out
        except Exception as e:
            print(e)
            print("[ERROR] Download audio Failed.")
            return None
        