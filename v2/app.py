from PyQt6.QtWidgets import * 
from PyQt6.QtGui import * 
from PyQt6.QtCore import *
from qt_material import apply_stylesheet
import pyperclip, sys# clipboard
from pytube import YouTube, Playlist
from pathlib import Path
import ffmpeg, re
import threading, urllib.request, os, logging, time
# my lib 
from select_window import select_win, playlist_win

# global
LOGGING_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
DATE_FORMAT = '%Y%m%d %H:%M:%S'
logging.basicConfig(level=logging.WARNING, #filename='mylog.log', filemode='a+',
                    format=LOGGING_FORMAT, datefmt=DATE_FORMAT)

class progressThread(QThread):
    signal = pyqtSignal(int)
    def __init__(self):
        QThread.__init__(self)
        self.over = False
    def __del__(self):
        self.wait()
    def run(self):
        # your logic here
        while not self.over:      
            self.signal.emit(1)
            time.sleep(1)
        self.exit()
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
        self.MAX_PROGRESS = 10
        self.progress_num = 0
        self.Qthread = {}
        self.progress = {}
    # css
        apply_stylesheet(self, theme='dark_pink.xml')
    # popup
        self.select_win = select_win(self.RES)
        self.playlist_win = playlist_win()
    # mainWindow setting
        self.setWindowTitle("YouTube下載器")
        #self.error_dialog.
        self.error_dialog = QMessageBox()
        self.move(QPoint(800, 50))
        self.setFixedSize(658, 658)
        self.my_icon_size = QSize(1200, 50)
        #self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.set_up_btn()   
        #self.set_bottom_btn() 
        self.set_download_area()
        
        progress_delegate = ProgressDelegate(self.list_view)
        self.list_view.setItemDelegateForColumn(2, progress_delegate)
        self.model = QStandardItemModel(0, 3)
        self.model.setHorizontalHeaderLabels(["Image","Title", "Progress"])
        QMetaObject.connectSlotsByName(self)
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
    #     select_row = []                                                      
    #     for model_index in self.list_view.selectionModel().selectedIndexes():       
    #         index = QPersistentModelIndex(model_index)         
    #         select_row.append(index)        
    #     for index in select_row:          
    #         self.model.removeRow(index.row())
    # def clear_event(self):
    #     self.model.removeRows(0, self.model.rowCount())
    def select_output_event(self):
        self.output_path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        logging.info("set output path : {}".format(self.output_path))
    def get_video_ID(self, url):
        """It will return YouTube's ID"""
        youtube_regex = r"^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))(?P<video_ID>(\w|-)[^&]+)(?:\S+)?$"
        sreMatch = re.match(youtube_regex, url)
        if sreMatch != None:
            return sreMatch.group("video_ID")
        else: 
            logging.warning("Not a YouTube's URL.")
            return None
    def download_audio_event(self):

        info_dict, streams_dict = self.get_yt_info()
        if info_dict == None: return
        self.add_QTableView_item(info_dict, streams_dict[8787])
        t = threading.Thread(target=self.download, args =(streams_dict, 8787,))
        t.setDaemon(True)
        t.start()
    def download_video_event(self):

        info_dict, streams_dict = self.get_yt_info()
        if info_dict == None: return
        res = self.select_win.start(info_dict, streams_dict)
        if res == '': return
        self.add_QTableView_item(info_dict, streams_dict[res])
        t = threading.Thread(target=self.download, args =(streams_dict, res,))
        t.setDaemon(True)
        t.start()
        #self.download_video(streams_dict, res)
        
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
        for u in Playlist(url).video_urls:
            info_dict, streams_dict = self.get_yt_info(u)
            if info_dict == None: return
            if res != 8787:
                res = next(iter(streams_dict))
            self.add_QTableView_item(info_dict, streams_dict[res])
            t = threading.Thread(target=self.download, args =(streams_dict, res,))
            t.setDaemon(True)
            t.start()
            QCoreApplication.processEvents()
                
    def signal_accept(self, it_progress, stream, maxVal):
        try:
            val = self.progress[stream]
            if val <= 100:
                self.model.setItemData(it_progress.index(),
                    {Qt.ItemDataRole.UserRole+1000:val}) # let my progress item reflash
                if val == 100: 
                    self.Qthread[stream].over = True
                    self.progress_num -= 1
        except RuntimeError as e :   
            logging.error(e) 
            self.progress[stream] = -1
            self.progress_num -= 1
                
    def add_QTableView_item(self, info_dict, stream):
        pixmap = QPixmap(info_dict["thumbnail_path"])
        pixmap.scaled(25,25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
        it_image = QStandardItem(QIcon(pixmap), '')
        it_image.setSizeHint(self.my_icon_size)
        it_title = QStandardItem(info_dict["title"])

        it_progress = QStandardItem()
        it_progress.setData(0, Qt.ItemDataRole.UserRole+1000)
        while self.progress_num == self.MAX_PROGRESS:
            logging.warning("Thread full now use [{}]. Max Size is {}".format(self.progress_num, self.MAX_PROGRESS))
            time.sleep(1)
        self.progress_num += 1
        self.progress.update({stream: 0})
        self.Qthread.update({stream: progressThread()})
        self.Qthread[stream].signal.connect(lambda:self.signal_accept(it_progress, stream,  1))
        self.model.appendRow([it_image, it_title, it_progress])
        self.list_view.setModel(self.model)
        self.Qthread[stream].start()
    def my_progress_bar(self, stream, chunk, data_remaining):
        """progress_callback to use"""
        total_size = stream.filesize
        percent = 2*int(50*((total_size - data_remaining) / total_size)) - 1
        self.progress[stream] = percent
# yt
    def get_yt_info(self, url=''):
        if url == '': url=pyperclip.paste()
        id = self.get_video_ID(url)
        if id == None: 
            self.error_dialog.critical(self, "錯誤", "YouTube網址錯誤")
            return None, None
        yt = YouTube(url, on_progress_callback=self.my_progress_bar)
        Path("./img/").mkdir(parents=True, exist_ok=True)
        img = Path("./img/"+id+".jpg")
        info_dict = {}
        streams_dict = {}
        if not img.exists():
            urllib.request.urlretrieve(yt.thumbnail_url, img) # download img
        info_dict.update({
                "title": yt.title, 
                "thumbnail_path": str(img),
                "author": yt.author,
                # "captions": yt.captions,# 字幕
                "publish_date": yt.publish_date,
                "views": yt.views,
                "play_len": yt.length
                })
        for res in self.RES:
            video_obj = yt.streams.filter(mime_type="video/mp4",res=res).first()
            if video_obj != None:
                streams_dict.update({int(res.replace("p", "")): video_obj})
        streams_dict.update({8787: yt.streams.get_audio_only() }) # audio
        return info_dict, streams_dict
    def mp4_to_mp3(self, mp4, file_name):
        # mp4 to mp3
        try:
            if not Path(file_name).exists():
                ffmp4 = ffmpeg.input(mp4)
                audio = ffmp4.audio
                go = ffmpeg.output(audio, file_name)
                ffmpeg.run(go, overwrite_output=True) #capture_stdout=False, capture_stderr=True, )
                logging.info("mp4 to mp3 successed.")
                os.remove(mp4)
        except ffmpeg.Error as e:
            logging.error("mp4 to mp3 error.")
            # print(e.stdout.decode("utf-8") )
            # print(e.stderr.decode("utf-8") )
    def download(self, streams_dict, res):
        try:
            if res != '':
                out = streams_dict[res].download(output_path=self.output_path, skip_existing=True)
                if not streams_dict[res].includes_audio_track: # video only
                    audio = streams_dict[8787].download(output_path=self.output_path, 
                                                        filename=str(round(time.time()))+".mp4", skip_existing=True)
                    self.merge(out, audio)
                if res == 8787:
                    file_name = out.replace(".mp4", ".mp3")
                    if not Path(file_name).exists():
                        self.mp4_to_mp3(out, file_name)
                logging.info(out)
                self.progress[streams_dict[res]] = 100
        except PermissionError:
            time.sleep(2)
            self.download(streams_dict, res)
    def merge(self, video, audio):
        """Merge audio & video"""
        try: 
            temp_name = Path(video).parent / (str(round(time.time())+1)+".mp4")
            os.rename(video, temp_name)
            ffvideo = ffmpeg.input(str(temp_name))
            ffaudio = ffmpeg.input(audio)
            ffmpeg.concat(ffvideo, ffaudio, v=1, a=1) \
                .output(video) \
                .run(overwrite_output=True)#capture_stdout=False, capture_stderr=True)
            os.remove(temp_name)
            os.remove(audio)
            logging.info("Merge successed.")
        except ffmpeg.Error as e:
            os.remove(temp_name)
            os.remove(audio)
            logging.error("Merge audio & video error.")
            # print(e.stdout.decode("utf-8") )
            # print(e.stderr.decode("utf-8") ) 
    # def closeEvent(self, a0: QCloseEvent):
    #     for key, thread in self.progress.items():
    #         thread.ter
    #     return super().closeEvent(a0)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = mainWindow()
    myWin.show()
    sys.exit(app.exec())
