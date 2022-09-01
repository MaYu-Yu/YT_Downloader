# 快取path更改、紀錄
from PyQt6.QtWidgets import * 
from PyQt6.QtGui import * 
from PyQt6.QtCore import *
from qt_material import apply_stylesheet
import pyperclip, sys # clipboard
from pytube import YouTube, Playlist
from pathlib import Path
import ffmpeg, re
import urllib.request, os, logging, random, time
import threading, multiprocessing
# album
import eyed3
from eyed3.id3.frames import ImageFrame
# my lib 
from Scripts.select_window import select_win, playlist_win
from Scripts.Circular_Queue import Circular_Queue
from Scripts.delete_temp import delDir
# global
delDir('./img/', t=259200)
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s [line:%(lineno)d]'
DATE_FORMAT = '%Y%m%d %H:%M:%S'
logging.basicConfig(level=logging.INFO, filename='./img/mylog.log', filemode='a+',
                    format=LOGGING_FORMAT, datefmt=DATE_FORMAT, encoding='utf-8')

# progress sync update
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
        # your logic here
        try:
            while not self.over:      
                val = self.progress[self.stream]
                if val <= 100:
                    self.model.setItemData(self.it_progress.index(),
                        {Qt.ItemDataRole.UserRole+1000:val}) # let my progress item reflash
                    if val == 100: 
                        self.over = True
                time.sleep(1)
        except RuntimeError as e :   
            self.progress[self.stream] = -1
            logging.error(e) 
            self.exit()
        self.exit()
# draws progress
class ProgressDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        progress = index.data(Qt.ItemDataRole.UserRole + 1000)
        
        opt = QStyleOptionProgressBar()
        opt.rect = option.rect
        opt.minimum = 0
        opt.maximum = 100
        opt.progress = progress
        opt.text = f"{progress}%"
        opt.textVisible = True
        opt.state |= QStyle.StateFlag.State_Horizontal
        style = (
            option.widget.style() if option.widget is not None else QApplication.style()
        )
        style.drawControl(
            QStyle.ControlElement.CE_ProgressBar, opt, painter, option.widget
        )
        
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
    # css
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
    def start_Qthread(self):
        try:
            if not self.Qthread_queue.isEmpty() and threading.active_count() <= self.MAX_THREADING: # cpu_percent
                t = self.Qthread_queue.deQueue()
                t.start()
        except Exception as e:
            logging.error("Qthread start error.")
            logging.warn(e)
    def addThread(self, t):
        while self.Qthread_queue.isFull():
            time.sleep(1)
            QCoreApplication.processEvents()
        self.Qthread_queue.enQueue(t)
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
    # def set_bottom_btn(self):
    #     self.horizontalLayoutWidget_1 = QWidget(self.centralwidget)
    #     self.horizontalLayoutWidget_1.setGeometry(QRect(10, 590, 641, 61))
    #     self.horizontalLayout_1 = QHBoxLayout(self.horizontalLayoutWidget_1)
    #     self.horizontalLayout_1.setContentsMargins(0, 0, 0, 0)
        
    #     self.delete_btn = QPushButton(self.horizontalLayoutWidget_1)
    #     self.clear_btn = QPushButton(self.horizontalLayoutWidget_1)

    #     self.horizontalLayout_1.addWidget(self.delete_btn)
    #     self.horizontalLayout_1.addWidget(self.clear_btn)
    #     self.sizePolicy_1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
    #     self.sizePolicy_1.setHorizontalStretch(0)
    #     self.sizePolicy_1.setVerticalStretch(0)
    #     self.sizePolicy_1.setHeightForWidth(self.delete_btn.sizePolicy().hasHeightForWidth())        
    #     self.sizePolicy_1.setHeightForWidth(self.clear_btn.sizePolicy().hasHeightForWidth())        
    #     self.delete_btn.setSizePolicy(self.sizePolicy_1)
    #     self.clear_btn.setSizePolicy(self.sizePolicy_1)
    #     self.delete_btn.clicked.connect( \
    #         lambda:self.delete_rows_event())
    #     self.clear_btn.clicked.connect( \
    #         lambda:self.clear_event())    
        
    #     self.delete_btn.setText("刪除")
    #     self.clear_btn.setText("清空")
    # def delete_rows_event(self):
        # select_row = []                                                      
        # for model_index in self.list_view.selectionModel().selectedIndexes():       
        #     index = QPersistentModelIndex(model_index)         
        #     select_row.append(index)        
        # for index in select_row:          
        #     self.model.removeRow(index.row())
    def clear_event(self):
        self.model.removeRows(0, self.model.rowCount())
    def select_output_event(self):
        """set output path use QFileDialog.getExistingDirectory"""
        self.output_path = Path(QFileDialog.getExistingDirectory(self, "Select Directory"))
        logging.info("set output path : {}".format(self.output_path))
        
    def download_audio_event(self):
        info_dict, streams_dict = self.get_yt_info(audio_only=True)
        if info_dict != None:
            self.download(info_dict, streams_dict, 8787)
    def download_video_event(self):
        info_dict, streams_dict = self.get_yt_info()
        if info_dict != None:  
            res = self.select_win.start(info_dict, streams_dict)
            if res == '': return
            self.download(info_dict, streams_dict, res)
            
    def download_playlist_event(self):
        def get_playlist_ID(url):
            """It will return YouTube's Playlist ID"""
            youtube_regex = r"[?&]list=(?P<list_ID>([^&]+))"
            sreMatch = re.search(youtube_regex, url)
            if sreMatch != None:
                return sreMatch.group("list_ID")
            else: 
                logging.warning("Not a YouTube's PlayList URL.")
                return None
        url = pyperclip.paste()
        if get_playlist_ID(url) == None:
            self.error_dialog.critical(self, "錯誤", "此視頻無播放清單")
            return
        res = self.playlist_win.start()
        if res == 0: return 
        t = threading.Thread(target=self.playlistThread, args =(url,res,))
        t.setDaemon(True)
        self.addThread(t)
    def playlistThread(self, url, res):
        for u in Playlist(url).video_urls:
            info_dict, streams_dict = self.get_yt_info(u, audio_only=True) if res == 8787 else self.get_yt_info(u)
            if info_dict != None:
                if res != 8787:
                    res = next(iter(streams_dict))
                self.download(info_dict, streams_dict, res)
                
    def download(self, info_dict, streams_dict, res):
    # add_QTableView_item
        stream = streams_dict[res]
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
        t = threading.Thread(target=self.downloadThread, args =(info_dict, streams_dict, res,))
        t.setDaemon(True)
        self.addThread(p)
        self.addThread(t)

    def downloadThread(self, info_dict, streams_dict, res):
        """ Download YouTube"""
    # download
        stream = streams_dict[res]
        try:
            if res != '':
                out = str(self.output_path / stream.default_filename)
                if not Path(out).exists():
                    temp = stream.download(output_path=self.output_path, 
                                                    filename=next(self.random_num)+".mp4", skip_existing=False)
                    if res == 8787: # mp4 to mp3
                        out = out[:-4]+".mp3"
                        if not Path(out).exists():
                            self.mp4_to_mp3(temp, str(out))
                            self.add_title(out, info_dict)
                        else: 
                            os.remove(temp)
                    elif not stream.includes_audio_track: # video only
                        audio = streams_dict[8787].download(output_path=self.output_path, 
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
# progress 
    def my_progress_bar(self, stream, chunk, data_remaining):
        """progress_callback to use"""
        total_size = stream.filesize
        percent = 2*int(50*((total_size - data_remaining) / total_size)) - 1
        self.progress[stream] = percent
# yt
    def get_video_ID(self, url):
        """It will return YouTube's ID"""
        youtube_regex = r"^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))(?P<video_ID>(\w|-)[^&]+)(?:\S+)?$"
        sreMatch = re.match(youtube_regex, url)
        if sreMatch != None:
            return sreMatch.group("video_ID")
        else: 
            logging.warning("Not a YouTube's URL.")
            return None 
    def get_yt_info(self, url='', audio_only=False):
        if url == '': url=pyperclip.paste()
        id = self.get_video_ID(url)
        if id == None: 
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
                    # "captions": yt.captions,# 字幕
                    "publish_date": yt.publish_date,
                    "views": yt.views,
                    "play_len": yt.length
                    }
            if not audio_only:
                for res in self.RES:
                    video_obj = yt.streams.filter( mime_type="video/mp4", res=res).first()
                    if video_obj != None:
                        streams_dict.update({int(res[:-1]): video_obj})
            streams_dict.update({8787: yt.streams.filter( mime_type="audio/mp4").order_by('abr').desc().first() }) # audio
        except Exception as e:
            logging.error("get_yt_info error.")
            logging.error(e)
            return None, None
        return info_dict, streams_dict
    def add_title(self, file_name, info_dict):
        audioFile = eyed3.load(file_name)
        if (audioFile.tag == None):
            audioFile.initTag()
        audioFile.tag.title = info_dict["title"]
        audioFile.tag.artist = info_dict["author"]
        audioFile.tag.album = info_dict["author"]
        audioFile.tag.images.set(ImageFrame.FRONT_COVER, open(info_dict["thumbnail_path"],'rb').read(), 'image/jpeg')
        audioFile.tag.save()
    def mp4_to_mp3(self, mp4, file_name):
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
    def merge(self, video, audio, out):
        """Merge audio & video"""
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
            logging.error("Merge audio & video error.")
            #print(e.stdout.decode("utf-8") )
            #print(e.stderr.decode("utf-8") ) 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = mainWindow()
    myWin.show()
    sys.exit(app.exec())