from PyQt6.QtWidgets import * 
from PyQt6.QtGui import * 
from PyQt6.QtCore import *
import pyperclip, sys# clipboard
from qt_material import apply_stylesheet 

from YouTube_Download import YouTube_Download
from select_window import MyPopup
class progress_Thread(QThread):
    _signal = pyqtSignal(int)
    def __init__(self, val):
        super(progress_Thread, self).__init__()
        self.val = val
    def set_val(self, val):
        self.val = val
    def __del__(self):
        self.wait()

    def run(self):
        try:
            while self.val < 100:
                self.sleep(1)
                self._signal.emit(1)
        except RuntimeError:
            print("RuntimeError")
            self.quit()
            pass
        self.set_val(0)
        self.quit()
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
        self.popup = MyPopup()
        self.set_stylesheet()
        self.setWindowTitle("YouTube下載器")
        #self.error_dialog.
        self.error_dialog = QMessageBox()
        
        self.yt = YouTube_Download()
        self.progress_size = -1
        self.Qthread = progress_Thread(0)
        self.Qthread_list = [] 
        self.it_progress = [] 
    # mainWindow setting
        self.move(QPoint(800, 50))
        self.setObjectName("mainWindow")
        self.setFixedSize(658, 658)
        self.my_icon_size = QSize(1200, 50)
        #self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.centralwidget = QWidget(self)
        self.set_up_btn()   
        self.set_bottom_btn() 
        self.set_download_list()
        self.setCentralWidget(self.centralwidget)
        
        progress_delegate = ProgressDelegate(self.list_view)
        self.list_view.setItemDelegateForColumn(2, progress_delegate)
        self.model = QStandardItemModel(0, 3)
        self.model.setHorizontalHeaderLabels(["Image","Title", "Progress"])
        QMetaObject.connectSlotsByName(self)
    def set_stylesheet(self):
        apply_stylesheet(self, theme='dark_pink.xml')
    
    def call_popup(self):
        
        self.popup.set_yt_info(self.yt.info["thumbnail_url"], self.yt.info["author"], str(self.yt.info["publish_date"]), 
                                str(self.yt.info["views"]), 
                                str(self.yt.info["play_len"] // 60)+ "分:" +str(self.yt.info["play_len"] % 60 + "秒"), 
                                self.yt.info["title"], self.yt.stream_dict.keys())
        
        return self.popup.start()
    
    
    def signal_accept(self, stream, num):
        try:
            progress = self.yt.progress[stream] # from Youtube_Download's pytube download thread get progress in time.
            self.model.setItemData(self.it_progress[num].index(), 
                {Qt.ItemDataRole.UserRole+1000:progress}) # let my progress item reflash
            self.Qthread_list[num].set_val(progress)
        except RuntimeError:
            print("Runtime Error")
            self.Qthread_list[num].set_val(progress)
    def set_progress(self, res):
        self.progress_size+=1
        num = self.progress_size
        
        stream = self.yt.stream_dict[res]["obj"]
        self.Qthread._signal.connect(lambda:self.signal_accept(stream, num))
        self.Qthread_list.append(self.Qthread)
        it = QStandardItem()
        it.setData(0, Qt.ItemDataRole.UserRole+1000)
        self.it_progress.append(it)
        return num
    def add_QTableView_item(self, res):
        if not bool(self.yt.info): return
        _title = self.yt.info["title"]
        if res == "8787": 
            pixmap = QPixmap("./icon/audio_icon.jpg")
        else:
            from img_pixmap import get_pixmap
            pixmap = get_pixmap(self.yt.info["thumbnail_url"])
        it_image = QStandardItem(QIcon(pixmap), '')
        it_image.setSizeHint(self.my_icon_size)
        
        # it_image = QStandardItem(QIcon(pixmap), '')
        it_title = QStandardItem(_title)
        num = self.set_progress(res)
        self.model.appendRow([it_image, it_title, self.it_progress[num]])
        self.list_view.setModel(self.model)
        
        self.Qthread_list[num].start()
    def delete_rows_event(self):
        select_row = []                                                      
        for model_index in self.list_view.selectionModel().selectedIndexes():       
            index = QPersistentModelIndex(model_index)         
            select_row.append(index)        
        for index in select_row:          
            self.model.removeRow(index.row())
    def clear_event(self):
        self.model.removeRows(0, self.model.rowCount())
        
        #self.Qthread_list[]
    def set_yt(self):
        url = pyperclip.paste()
        print("Read ClipBoard :", url)   
        if not self.yt.is_YouTube_URL(url): 
            self.error_dialog.critical(self, "錯誤", "請複製正確的YouTube網址")
            return None
        self.yt.set_YouTube(url)
        return (url)
    def download_audio_event(self):
        url = self.set_yt()
        if url == None:return
        self.add_QTableView_item("8787")
        self.yt.download_thread(url, res="8787") 
        
    def download_video_event(self):
        url = self.set_yt()
        if url == None:return
        res = self.call_popup()
        if res != '':
            self.add_QTableView_item(res)
            self.yt.download_thread(url, res)
    def download_playlist_event(self):
        url = self.set_yt()
        if url == None: return 
        if not self.yt.is_YouTube_playlist_URL(url):
            self.error_dialog.critical(self, "錯誤", "此視頻無播放清單")
            return
        res= self.call_popup()
        if res != '':
            urls = self.yt.get_playlist_url(url)
            #self.loading.show()
            for i in urls:
                self.yt.set_YouTube(i)
                self.add_QTableView_item(res)
                self.yt.download_thread(i, res)
                QCoreApplication.processEvents()
            #self.loading.stopAnimation()
    def select_output_event(self):
        path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.yt.set_output_path(path)
        print(path)
        
    def set_download_list(self):
        self.download_list = QScrollArea(self.centralwidget)
        self.download_list.setGeometry(QRect(10, 80, 640, 500))
        self.download_list.setWidgetResizable(True)
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
        self.download_list.setWidget(self.scroll_area) 
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
    def set_bottom_btn(self):
        self.horizontalLayoutWidget_1 = QWidget(self.centralwidget)
        self.horizontalLayoutWidget_1.setGeometry(QRect(10, 590, 641, 61))
        self.horizontalLayout_1 = QHBoxLayout(self.horizontalLayoutWidget_1)
        self.horizontalLayout_1.setContentsMargins(0, 0, 0, 0)
        
        self.delete_btn = QPushButton(self.horizontalLayoutWidget_1)
        self.clear_btn = QPushButton(self.horizontalLayoutWidget_1)

        self.horizontalLayout_1.addWidget(self.delete_btn)
        self.horizontalLayout_1.addWidget(self.clear_btn)
        self.sizePolicy_1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.sizePolicy_1.setHorizontalStretch(0)
        self.sizePolicy_1.setVerticalStretch(0)
        self.sizePolicy_1.setHeightForWidth(self.delete_btn.sizePolicy().hasHeightForWidth())        
        self.sizePolicy_1.setHeightForWidth(self.clear_btn.sizePolicy().hasHeightForWidth())        
        self.delete_btn.setSizePolicy(self.sizePolicy_1)
        self.clear_btn.setSizePolicy(self.sizePolicy_1)
        self.delete_btn.clicked.connect( \
            lambda:self.delete_rows_event())
        self.clear_btn.clicked.connect( \
            lambda:self.clear_event())    
        
        self.delete_btn.setText("刪除")
        self.clear_btn.setText("清空")
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = mainWindow()
    myWin.show()
    sys.exit(app.exec())
