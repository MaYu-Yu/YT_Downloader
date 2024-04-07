from PyQt6.QtWidgets import * 
from PyQt6.QtGui import * 
from PyQt6.QtCore import *
from qt_material import apply_stylesheet
import pyperclip, sys # clipboard
from pytube import YouTube, Playlist
from pathlib import Path
import ffmpeg, re
import urllib.request, os, logging, random, time
import threading
from mutagen.mp4 import MP4, MP4Cover
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, ID3NoHeaderError
# my lib 
from Scripts.select_window import selectWin, playlistWin

# 建立刪除舊日誌檔案的函式
def delDir(dir_path, max_age=259200):
    if os.path.exists(dir_path):
        now = int(time.time())

        for root, dirs, files in os.walk(dir_path, topdown=False):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                last_modified_time = int(os.stat(file_path).st_mtime)
                if now - last_modified_time >= max_age:
                    os.remove(file_path)
                    logging.info(f"{file_path} was removed!")

            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    os.rmdir(dir_path)
                    logging.info(f"{dir_path} was removed!")
                except OSError:
                    pass

    else:
        os.mkdir(dir_path)

# log檔案建立
delDir('./img/', max_age=259200)
delDir('./temp/', max_age=0)

LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s [line:%(lineno)d]'
DATE_FORMAT = '%Y%m%d %H:%M:%S'
logging.basicConfig(level=logging.INFO, filename='./img/mylog.log', filemode='a+',
                    format=LOGGING_FORMAT, datefmt=DATE_FORMAT, encoding='utf-8')

# 繪製進度條
class ProgressDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Extract progress value from item data
        progress = index.data(Qt.ItemDataRole.UserRole + 1000)
        
        # Ensure progress is within the 0-100 range
        progress = max(0, min(100, progress))
        
        # Create QStyleOptionProgressBar
        progress_bar_option = self.getProgressBarOption(option, progress)
        
        # Draw the progress bar
        style = option.widget.style() if option.widget else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ProgressBar, progress_bar_option, painter, option.widget)
    
    def getProgressBarOption(self, option, progress):
        progress_bar_option = QStyleOptionProgressBar()
        progress_bar_option.rect = option.rect
        progress_bar_option.minimum = 0
        progress_bar_option.maximum = 100
        progress_bar_option.progress = progress
        progress_bar_option.text = f"{progress}%"
        progress_bar_option.textVisible = True
        progress_bar_option.state |= QStyle.StateFlag.State_Horizontal
        return progress_bar_option
        
class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        apply_stylesheet(self, theme='dark_pink.xml')
        self.output_path = Path(str(Path.home() / "Downloads"))
        self.RES = ("4320p", "2160p", "1080p", "720p", "480p")
        def get_random():
            temp = [i for i in range(1, 10000)]
            random.shuffle(temp)
            for i in temp:
                yield str(i)
        self.random_num = get_random()
        self.progress = {}
        self.Qthread_queue = []
    # popup
        self.select_win = selectWin(self.RES)
        self.playlist_win = playlistWin()
    # mainWindow setting
        self.setWindowTitle("YouTube下載器")
        self.error_dialog = QMessageBox()
        self.move(QPoint(800, 50))
        self.setFixedSize(658, 658)
        self.my_icon_size = QSize(1200, 50)
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.set_up_btn()   
        self.set_download_area()
        
        progress_delegate = ProgressDelegate(self.list_view)
        self.list_view.setItemDelegateForColumn(2, progress_delegate)
        self.model = QStandardItemModel(0, 3)
        self.model.setHorizontalHeaderLabels(["Image","Title", "Progress"])
        QMetaObject.connectSlotsByName(self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.start_Qthread)
        self.timer.start(1000)  # this will emit every second
    def start_Qthread(self):
        """ start & control Qthread"""
        if self.Qthread_queue:
            print(self.Qthread_queue)
            thread = self.Qthread_queue.pop(0)
            thread.start()
    def add_thread(self, t):
        """ add to thread the queue"""
        self.Qthread_queue.append(t)
# GUI建立及擺設
    def set_download_area(self):
        self.download_area = QScrollArea(self.centralwidget)
        self.download_area.setGeometry(QRect(10, 80, 640, 500))
        self.download_area.setWidgetResizable(True)
        self.scroll_area = QWidget()
        self.scroll_area.setGeometry(QRect(0, 0, 640, 500))
        self.list_view = QTableView(self.scroll_area)
        self.list_view.setGeometry(QRect(0, 0, 640, 500))
        self.list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.list_view.horizontalHeader().setStretchLastSection(True)
        self.list_view.setIconSize(self.my_icon_size)
        self.list_view.verticalHeader().setDefaultSectionSize(50)
        self.download_area.setWidget(self.scroll_area) 
    def set_up_btn(self):
        self.horizontal_layout_widget = QWidget(self.centralwidget)
        self.horizontal_layout_widget.setGeometry(QRect(10, 10, 641, 61))
        self.horizontal_layout = QHBoxLayout(self.horizontal_layout_widget)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        
        self.download_audio_btn = QPushButton(self.horizontal_layout_widget)
        self.download_video_btn = QPushButton(self.horizontal_layout_widget)
        self.select_output_btn = QPushButton(self.horizontal_layout_widget)
        self.download_playlist_btn = QPushButton(self.horizontal_layout_widget)
        
        self.horizontal_layout.addWidget(self.download_audio_btn)
        self.horizontal_layout.addWidget(self.download_video_btn)
        self.horizontal_layout.addWidget(self.select_output_btn)
        self.horizontal_layout.addWidget(self.download_playlist_btn)

        
        self.sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.sizePolicy.setHorizontalStretch(0)
        self.sizePolicy.setVerticalStretch(0)
        self.sizePolicy.setHeightForWidth(self.download_audio_btn.sizePolicy().hasHeightForWidth())        
        self.sizePolicy.setHeightForWidth(self.download_video_btn.sizePolicy().hasHeightForWidth())        
        self.sizePolicy.setHeightForWidth(self.select_output_btn.sizePolicy().hasHeightForWidth())
        self.sizePolicy.setHeightForWidth(self.download_playlist_btn.sizePolicy().hasHeightForWidth())
        self.download_audio_btn.setSizePolicy(self.sizePolicy)
        self.download_video_btn.setSizePolicy(self.sizePolicy)
        self.select_output_btn.setSizePolicy(self.sizePolicy)
        self.download_playlist_btn.setSizePolicy(self.sizePolicy)
        
        self.download_audio_btn.clicked.connect( \
            lambda:self.download_audio_event())
        self.download_video_btn.clicked.connect( \
            lambda:self.download_video_event())
        self.select_output_btn.clicked.connect( \
            lambda:self.select_output_event())
        self.download_playlist_btn.clicked.connect( \
            lambda:self.download_playlist_event())
        
        self.download_audio_btn.setText("下載音訊")
        self.download_video_btn.setText("下載影片")
        self.select_output_btn.setText("輸出資料夾")
        self.download_playlist_btn.setText("下載播放清單")
    
# GUI事件
    def select_output_event(self):
        """set output path use QFileDialog.getExistingDirectory"""
        self.output_path = Path(QFileDialog.getExistingDirectory(self, "Select Directory")) 
        logging.info("set output path : {}".format(self.output_path))
    def download_audio_event(self):
        info_dict, streams_dict = self.get_yt_info(audio_only=True)
        if info_dict is not None:
            self.download(self.output_path, info_dict, streams_dict, 8787)
    def download_video_event(self):
        info_dict, streams_dict = self.get_yt_info()
        if info_dict is not None:  
            res = self.select_win.start(info_dict, streams_dict)
            if res == None:
                return
            self.download(self.output_path, info_dict, streams_dict, res)
# 下載播放清單GUI建立            
    def download_playlist_event(self):
        def get_playlist_ID(url):
            """It will return YouTube's Playlist ID"""
            youtube_regex = r"[?&]list=(?P<list_ID>([^&]+))"
            sreMatch = re.search(youtube_regex, url)
            if sreMatch is not None:
                return sreMatch.group("list_ID")
            else: 
                logging.warning("Not a YouTube's PlayList URL.")
                return None
        url = pyperclip.paste()
        if get_playlist_ID(url) is None:
            self.error_dialog.critical(self, "錯誤", "此視頻無播放清單")
            return
        res = self.playlist_win.start()
        if res == None:
            return 
        t = threading.Thread(target=self.playlist_thread, args =(url,res,))
        t.daemon=True
        self.add_thread(t)
# 下載播放清單執行緒
    def playlist_thread(self, url, res):
        """ download playlist thread"""
        save_path = self.output_path
        
        for u in Playlist(url).video_urls:
            info_dict, streams_dict = self.get_yt_info(u, audio_only=True, playlist=True) if res == 8787 else self.get_yt_info(u, playlist=True)
            if info_dict is not None:
                if res != 8787:
                    res = next(iter(streams_dict))
                t = threading.Thread(target=self.download, args =(save_path, info_dict, streams_dict, res, True,))
                t.daemon=True
                self.add_thread(t)
# 下載GUI建立                
    def download(self, save_path, info_dict, streams_dict, res, isPlaylist=False):
        """ add download gui and call download_thread"""
        stream = streams_dict[res]
    # 重複過濾
        stream_file = Path(save_path / stream.default_filename) if res != 8787 else \
            Path(save_path / (stream.default_filename[:-4]+".mp3"))
        if stream_file.exists():
            if not isPlaylist:
                self.error_dialog.warning(self, "錯誤", "重複下載\n{}".format(str(stream_file)))
        else:
        # add_QTableView_item    
            pixmap = QPixmap(info_dict["thumbnail_path"])
            pixmap.scaled(25,25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
            it_image = QStandardItem(QIcon(pixmap), '')
            it_image.setSizeHint(self.my_icon_size)
            it_title = QStandardItem(info_dict["title"])

            it_progress = QStandardItem()
            it_progress.setData(0, Qt.ItemDataRole.UserRole+1000)
            self.progress.update({stream: it_progress})
            self.model.appendRow([it_image, it_title, it_progress])
            self.list_view.setModel(self.model)
        # thread
            t = threading.Thread(target=self.download_thread, args =(save_path, info_dict, streams_dict, res,))
            t.daemon=True
            self.add_thread(t)
# 下載執行緒
    def download_thread(self, save_path, info_dict, streams_dict, res):
        """ download thread"""
        try:
            audio_path = streams_dict[8787].download(output_path="temp", 
                                    filename_prefix=next(self.random_num), skip_existing=False)
            if res == 8787:
                output_filename = streams_dict[8787].default_filename
                output_path = os.path.join(save_path, output_filename.replace(".mp4", ".mp3"))
                if not os.path.exists(output_path):
                    self.convert_to_mp3(audio_path, output_path)
                else:
                    logging.info(f"File [{output_path}] already exists. Skipping download.")
            else:
                video_path = streams_dict[res].download(output_path="temp", filename_prefix=next(self.random_num),
                                                skip_existing=False)
                output_filename = streams_dict[res].default_filename
                output_path = os.path.join(save_path, output_filename)
                if not os.path.exists(output_path):
                    self.merge_audio_and_video(audio_path, video_path, output_path)
                else:
                    logging.info(f"File [{output_path}] already exists. Skipping download.")
                os.remove(video_path)
            os.remove(audio_path)
            self.add_info(output_path, info_dict)    
        except Exception as e:
            logging.error("Download Thread error.")
            logging.error(e)
            os.remove(audio_path)
            os.remove(video_path)
            os.remove(output_path)
# 音樂轉成mp3
    def convert_to_mp3(self, input_path, output_path):
        try:
            ffmpeg.input(input_path).output(output_path).run(overwrite_output=True)
        except ffmpeg.Error as e:
            os.remove(input_path)
            os.remove(output_path)
            logging.error("convert_to_mp3 error.")
            logging.error(f"Error(stdout): {e.stdout}")
            logging.error(f"Error(stderr): {e.stderr}")
            
# 因為yt最高畫質跟音樂是分開下載的 所以需要合併它們
    def merge_audio_and_video(self, audio_path, video_path, output_path):
        try:
            audio = ffmpeg.input(audio_path)
            video = ffmpeg.input(video_path)
            ffmpeg.output(audio, video, output_path, acodec='aac').run(overwrite_output=True)
        except ffmpeg.Error as e:
            os.remove(video)
            os.remove(audio)
            os.remove(output_path)
            logging.error("merge_audio_and_video error.")
            logging.error(f"Error(stdout): {e.stdout}")
            logging.error(f"Error(stderr): {e.stderr}")
# 實時更新progress bar
    def my_progress_bar(self, stream, chunk, data_remaining):
        """progress_callback to use"""
        total_size = stream.filesize
        percent = 2*int(50*((total_size - data_remaining) / total_size))
        self.model.setItemData(self.progress[stream].index(), {Qt.ItemDataRole.UserRole + 1000: percent})
# 獲取影片ID
    def get_video_ID(self, url):
        """It will return YouTube's ID
        Args:
            url (_str_): YouTube's url

        Returns:
            _str_: video_ID or None
        """
        youtube_regex = r"^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))(?P<video_ID>(\w|-)[^&]+)(?:\S+)?$"
        sreMatch = re.match(youtube_regex, url)
        if sreMatch is not None:
            return sreMatch.group("video_ID")
        else: 
            logging.warning("Not a YouTube's URL.")
            return None 
# 獲取影片的基本資訊
    def get_yt_info(self, url='', audio_only=False, playlist=False):
        """get Video info

        Args:
            url (str, optional): YouTube's url. Defaults to ''.
            audio_only (bool, optional): if: audio only just get audio stream, else: get video stream. Defaults to False.

        Returns:
            _Dict_: info_dict[title, thumbnail_path, author, captions, publish_date, views, play_len]
            _Dict_: streams_dict["4320", "2160", "1080", "720", "480", "8787"--is audio]
        """
        if url == '':
            url = pyperclip.paste()
        id = self.get_video_ID(url)
        if id is None: 
            self.error_dialog.warning(self, "錯誤", "YouTube網址錯誤")
            return None, None
        yt = YouTube(url, on_progress_callback=self.my_progress_bar)
    
        img = Path("./img/"+id+".jpg")
        streams_dict = {}
        try:
            if not img.exists():
                urllib.request.urlretrieve(yt.thumbnail_url, img) # download img
            info_dict ={
                    "title": yt.title, 
                    "thumbnail_path": str(img),
                    "author": yt.author,
                    #"captions": yt.captions,# 字幕
                    "publish_date": yt.publish_date,
                    "views": yt.views,
                    "play_len": yt.length
                    }
            if not audio_only:
                for res in self.RES:
                    video_obj = yt.streams.filter(adaptive=True, mime_type="video/mp4", res=res).first()
                    if video_obj != None:
                        streams_dict.update({int(res[:-1]): video_obj})
                    if playlist: break
            streams_dict.update({8787: yt.streams.filter(mime_type="audio/mp4").last() }) # audio
            
        except Exception as e:
            logging.error("get_yt_info error.")
            logging.error(e)
            return None, None
        return info_dict, streams_dict
# 使用mutagen更改下載的音樂資訊
    def add_info(self, file_name, info_dict):
        _, file_extension = os.path.splitext(file_name.lower())
        if file_extension == '.mp3':
            self.add_info_mp3(file_name, info_dict)
        elif file_extension == '.mp4':
            self.add_info_mp4(file_name, info_dict)

    def add_info_mp3(self, file_name, info_dict):
        try:
            audio = ID3(file_name)
        except ID3NoHeaderError as e:
            audio = ID3()
            logging.error("add_info_mp3 error.")
            logging.error(e)
        audio.delete()
        audio.add(TIT2(encoding=3, text=info_dict["title"]))
        audio.add(TPE1(encoding=3, text=info_dict["author"]))
        audio.add(TALB(encoding=3, text=info_dict["author"]))
        with open(info_dict["thumbnail_path"], 'rb') as f:
            cover_data = f.read()
            audio.add(APIC(3, 'image/jpeg', 3, 'Front cover', cover_data))
        audio.save(file_name)

    def add_info_mp4(self, file_name, info_dict):
        mp4 = MP4(file_name)
        mp4.delete()
        mp4["\xa9nam"] = info_dict["title"]
        mp4["\xa9ART"] = info_dict["author"]
        mp4["\xa9alb"] = info_dict["author"]
        with open(info_dict["thumbnail_path"], 'rb') as f:
            cover_data = f.read()
            mp4["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]
        mp4.save()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = mainWindow()
    myWin.show()
    
    sys.exit(app.exec())