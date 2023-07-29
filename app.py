from PyQt6.QtWidgets import * 
from PyQt6.QtGui import * 
from PyQt6.QtCore import *
from PyQt6.QtCore import QThread, Qt, QElapsedTimer
from qt_material import apply_stylesheet
import pyperclip, sys # clipboard
from pytube import YouTube, Playlist
from pathlib import Path
import ffmpeg, re
import urllib.request, os, logging, random, time
import threading, multiprocessing
# album
import eyed3
# my lib 
from Scripts.select_window import select_win, playlist_win
from Scripts.Circular_Queue import Circular_Queue


# 建立刪除舊日誌檔案的函式
def delDir(dir, t=259200):
    if os.path.exists(dir):
        # 獲取文件夾下所有文件和文件夾
        files = os.listdir(dir)
        now = int(time.time())  # 只需獲取一次當前時間

        for file in files:
            filePath = os.path.join(dir, file)  # 使用os.path.join來拼接路徑
            if os.path.isfile(filePath):
                # 獲取文件的最後一次修改時間
                last_modified_time = int(os.stat(filePath).st_mtime)

                # 判斷是否過期
                if now - last_modified_time >= t:
                    os.remove(filePath)
                    print(filePath + " was removed!")
            elif os.path.isdir(filePath):
                # 如果是文件夾，繼續遞迴刪除
                delDir(filePath, t)

                # 如果是空文件夾，刪除空文件夾
                if not os.listdir(filePath):
                    os.rmdir(filePath)
                    print(filePath + " was removed!")
    else:
        os.mkdir(dir)
# log黨建立
delDir('./img/', t=259200)
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s [line:%(lineno)d]'
DATE_FORMAT = '%Y%m%d %H:%M:%S'
logging.basicConfig(level=logging.INFO, filename='./img/mylog.log', filemode='a+',
                    format=LOGGING_FORMAT, datefmt=DATE_FORMAT, encoding='utf-8')

# 進度條同步更新的執行緒
class progressThread(QThread):
    def __init__(self, model, progress, it_progress, stream):
        QThread.__init__(self)
        self.model = model
        self.progress = progress
        self.it_progress = it_progress
        self.stream = stream
        self.over = False

    def __del__(self):
        self.wait()

    def run(self):
        elapsed_timer = QElapsedTimer()
        elapsed_timer.start()

        try:
            while not self.over:
                val = self.progress[self.stream]
                if val <= 100:
                    self.model.setItemData(self.it_progress.index(), {Qt.ItemDataRole.UserRole + 1000: val})
                    if val == 100:
                        self.over = True
                elapsed_time = elapsed_timer.elapsed()
                if elapsed_time < 1000:  # Delay 1 second
                    self.msleep(1000 - elapsed_time)
        except RuntimeError as e:
            self.progress[self.stream] = -1
            logging.error(e)

# 繪製進度條
class ProgressDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        progress = index.data(Qt.ItemDataRole.UserRole + 1000)

         # 確保進度在0到100的範圍內
        progress = max(0, min(100, progress))

        opt = QStyleOptionProgressBar()
        opt.rect = option.rect
        opt.minimum = 0
        opt.maximum = 100
        opt.progress = progress
        opt.text = f"{progress}%"
        opt.textVisible = True
        opt.state |= QStyle.StateFlag.State_Horizontal

        style = option.widget.style() if option.widget is not None else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ProgressBar, opt, painter, option.widget)

        
class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.output_path = Path(str(Path.home() / "Downloads"))
        self.RES = ("4320p", "2160p", "1080p", "720p", "480p")
        def get_random():
            temp = [i for i in range(1, 10000)]
            random.shuffle(temp)
            for i in temp:
                yield str(i)
        self.random_num = get_random()
        self.progress = {}
    #limit threading
        self.MAX_THREADING = 4 if multiprocessing.cpu_count() // 2 >= 4 else multiprocessing.cpu_count() // 2
        self.Qthread_queue = Circular_Queue(500)
        self.start, self.end = 0, 0 
        apply_stylesheet(self, theme='dark_pink.xml')
    # popup
        self.select_win = select_win(self.RES)
        self.playlist_win = playlist_win()
    # mainWindow setting
        self.setWindowTitle("YouTube下載器")
        self.error_dialog = QMessageBox()
        self.move(QPoint(800, 50))
        self.setFixedSize(658, 658)
        self.my_icon_size = QSize(1200, 50)
        #self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.set_up_btn()   
        # self.set_bottom_btn() 
        self.set_download_area()
        
        progress_delegate = ProgressDelegate(self.list_view)
        self.list_view.setItemDelegateForColumn(2, progress_delegate)
        self.model = QStandardItemModel(0, 3)
        self.model.setHorizontalHeaderLabels(["Image","Title", "Progress"])
        QMetaObject.connectSlotsByName(self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.start_Qthread)
        self.timer.start(500)  # this will emit every second
# thread控制
    def start_Qthread(self):
        """ start & control Qthread"""
        try:
            if not self.Qthread_queue.isEmpty() and threading.active_count() <= self.MAX_THREADING: # cpu_percent
                t = self.Qthread_queue.deQueue()
                t.start()
        except Exception as e:
            logging.error("Qthread start error.")
            logging.warn(e)
    def addThread(self, t):
        """ add thread the queue, if the queue is full, wait until the queue is free"""
        while self.Qthread_queue.isFull():
            time.sleep(1)
            QCoreApplication.processEvents()
        self.Qthread_queue.enQueue(t)
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
        # self.list_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # self.list_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.list_view.verticalHeader().setDefaultSectionSize(50)
        self.download_area.setWidget(self.scroll_area) 
    def set_up_btn(self):
        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QRect(10, 10, 641, 61))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        
        self.download_audio_btn = QPushButton(self.horizontalLayoutWidget)
        self.download_video_btn = QPushButton(self.horizontalLayoutWidget)
        self.select_output_btn = QPushButton(self.horizontalLayoutWidget)
        self.download_playlist_btn = QPushButton(self.horizontalLayoutWidget)
        
        self.horizontalLayout.addWidget(self.download_audio_btn)
        self.horizontalLayout.addWidget(self.download_video_btn)
        self.horizontalLayout.addWidget(self.select_output_btn)
        self.horizontalLayout.addWidget(self.download_playlist_btn)

        
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
            if res == '':
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
        if res == 0:
            return 
        t = threading.Thread(target=self.playlistThread, args =(url,res,))
        t.daemon=True
        self.addThread(t)
# 下載播放清單執行緒
    def playlistThread(self, url, res):
        """ download playlist thread"""
        save_path = self.output_path
        
        for u in Playlist(url).video_urls:
            info_dict, streams_dict = self.get_yt_info(u, audio_only=True) if res == 8787 else self.get_yt_info(u)
            if info_dict is not None:
                #if (self.output_path / streams_dict[res]).default_filename.exists() 
                if res != 8787:
                    res = next(iter(streams_dict))
                # self.download(info_dict, streams_dict, res, True)
                t = threading.Thread(target=self.download, args =(save_path, info_dict, streams_dict, res, True,))
                t.daemon=True
                self.addThread(t)
# 下載GUI建立                
    def download(self, save_path, info_dict, streams_dict, res, isPlaylist=False):
        """ add download gui and call downloadThread"""
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
            self.progress.update({stream: 0})
            self.model.appendRow([it_image, it_title, it_progress])
            self.list_view.setModel(self.model)
        # thread
            p = progressThread(self.model, self.progress, it_progress, stream)
            t = threading.Thread(target=self.downloadThread, args =(save_path, info_dict, streams_dict, res,))
            t.daemon=True
            
            self.addThread(p)
            self.addThread(t)
# 下載執行緒
    def downloadThread(self, save_path, info_dict, streams_dict, res):
        """ download thread"""
        stream = streams_dict[res]
        try:
            out = str(save_path / stream.default_filename).replace('&', '_')
            temp = stream.download(output_path="temp", 
                                            filename=next(self.random_num)+".mp4", skip_existing=False)
            if res == 8787: # mp4 to mp3
                out = out[:-4]+".mp3"
                if not Path(out).exists():
                    self.mp4_to_mp3(temp, out)
                    self.add_title(out, info_dict)
                else: 
                    os.remove(temp)
            elif not stream.includes_audio_track: # video only
                audio = streams_dict[8787].download(output_path="temp", 
                                                    filename=next(self.random_num)+".mp4", skip_existing=False)
                self.progress[stream] = 87
                self.merge(temp, audio, out)
            else:
                os.rename(temp, out)
            logging.info(out)
            self.progress[stream] = 100
        except Exception as e:
            logging.error("Download Thread error.")
            logging.error(e)
            os.remove(temp)
            os.remove(audio)
# 音樂轉成mp3
    def mp4_to_mp3(self, mp4, file_name):
        """mp4 to mp3

        Args:
            mp4 (_type_): mp4 file_name
            file_name (_type_): output file_name
        """
        # mp4 to mp3
        try:
            ffmp4 = ffmpeg.input(mp4)
            audio = ffmp4.audio
            go = ffmpeg.output(audio, file_name, q='1')
            ffmpeg.run(go, overwrite_output=True, cmd=r'ffmpeg.exe')
            logging.info("mp4 to mp3 successed.")
            os.remove(mp4)
        except ffmpeg.Error as e:
            logging.error("mp4 to mp3 error.")
            os.remove(mp4)
            os.remove(file_name)
            #print(e.stdout.decode("utf-8") )
            #print(e.stderr.decode("utf-8") )
            
# 因為yt最高畫質跟音樂是分開下載的 所以需要合併它們
    def merge(self, video, audio, out):
        """Merge audio & video

        Args:
            video (_type_): video file_name
            audio (_type_): audio file_name
            out (_type_): output file_name

        Returns:
            _type_: output file_name
        """
        try: 
            ffvideo = ffmpeg.input(video)
            ffaudio = ffmpeg.input(audio)
            ffmpeg.concat(ffvideo, ffaudio, v=1, a=1) \
                .output(out, q='1') \
                .run(overwrite_output=True, cmd=r'ffmpeg.exe')#capture_stdout=False, capture_stderr=True)
            os.remove(video)
            os.remove(audio)
            logging.info("Merge successed.")
            return out
        except ffmpeg.Error as e:
            os.remove(video)
            os.remove(audio)
            os.remove(out)
            logging.error("Merge audio & video error., {}")
            #print(e.stdout.decode("utf-8") )
            #print(e.stderr.decode("utf-8") ) 
            
# 實時更新progress bar
    def my_progress_bar(self, stream, chunk, data_remaining):
        """progress_callback to use"""
        total_size = stream.filesize
        percent = 2*int(50*((total_size - data_remaining) / total_size)) - 1
        self.progress[stream] = percent
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
    def get_yt_info(self, url='', audio_only=False):
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
        Path("./img/").mkdir(parents=True, exist_ok=True)
        img = Path("./img/"+id+".jpg")
        streams_dict = {}
        try:
            if not img.exists():
                urllib.request.urlretrieve(yt.thumbnail_url, img) # download img
            info_dict ={
                    "title": yt.title, 
                    "thumbnail_path": str(img),
                    "author": yt.author,
                    "captions": yt.captions,# 字幕
                    "publish_date": yt.publish_date,
                    "views": yt.views,
                    "play_len": yt.length
                    }
            if not audio_only:
                for res in self.RES:
                    video_obj = yt.streams.filter( mime_type="video/mp4", res=res).first()
                    if video_obj is not None:
                        streams_dict.update({int(res[:-1]): video_obj})
            streams_dict.update({8787: yt.streams.filter( mime_type="audio/mp4").order_by('abr').desc().first() }) # audio
            
        except Exception as e:
            logging.error("get_yt_info error.")
            logging.error(e)
            return None, None
        return info_dict, streams_dict
# 使用eyed3更改下載的音樂資訊
    def add_title(self, file_name, info_dict):
        """add info in mp3

        Args:
            file_name (_type_): mp3 file_name
            info_dict (_str_): info dict
        """
        audioFile = eyed3.load(file_name)
        if audioFile.tag is None:
            audioFile.initTag()
        audioFile.tag.title = info_dict["title"]
        audioFile.tag.artist = info_dict["author"]
        audioFile.tag.album = info_dict["author"]
        audioFile.tag.images.set(eyed3.id3.frames.ImageFrame.FRONT_COVER, open(info_dict["thumbnail_path"],'rb').read(), 'image/jpeg')
        audioFile.tag.save()

            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = mainWindow()
    myWin.show()
    sys.exit(app.exec())  # Use QApplication.exec() instead of app.exec_()
