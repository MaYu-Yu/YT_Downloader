from ast import Delete
import sys, time
from tkinter import Label
from PyQt6.QtWidgets import * 
from PyQt6.QtGui import * 
from PyQt6.QtCore import *
from YouTube_Download import YouTube_Download
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
        opt.state |= QStyle.StateFlag.State_Horizontal # <--
        style = (
            option.widget.style() if option.widget is not None else QApplication.style()
        )
        style.drawControl(
            QStyle.ControlElement.CE_ProgressBar, opt, painter, option.widget
        )
# class ImageDelegate(QStyledItemDelegate):
#     def __init__(self, parent=None):
#         QStyledItemDelegate.__init__(self, parent)
#         #self.icon =icon
#     def paint(self, painter, option, index):
#         #painter.fillRect(option.rect, QColor(191,222,185))
#         # path = "path\to\my\image.jpg"
#         path = "1.jpg"
#         image = QImage(str(path))
#         pixmap = QPixmap.fromImage(image)
        
#         #pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio)
#         # when i test ,just use option.rect.x(), option.rect.y(), no need scaled 
#         painter.drawPixmap(0, 1, 50, 50, pixmap)#option.rect.x(), option.rect.y(),  pixmap)
        
class Ui_mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.yt = YouTube_Download()
        self.jpg = []
    # mainWindow setting
        self.setObjectName("mainWindow")
        self.setGeometry(650, 50, 658, 658)
        # mainWindow.setStyleSheet("font-family: 'Helvetica', 'Arial','LiHei Pro','黑體-繁','微軟正黑體', sans-serif; \
        #                          font-style: normal; font-size: 16pt;")
        self.setStyleSheet("""
            QWidget {
                font-size: 20px;
                color: #b1b1b1;
            }

            QPushButton {
                background-color: rgb(255, 255, 255);
                border-radius: 15px;
            }

            QPushButton:pressed {
                background-color: orange;
                color: white;

            }

            QPushButton:hover {
                border-color: orange;
                border-color: white;
            }

            QProgressBar {
                border-style: solid;
                border-color: grey;
                border-radius: 7px;
                border-width: 2px;
                text-align: center;
            }

            QProgressBar::chunk {
                width: 2px;
                background-color: #de7c09;
                margin: 3px;
            }
        """)
            
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.set_horizontalLayout()
        self.set_btn()      
        self.setEvent()
        self.set_download_list()
        self.setCentralWidget(self.centralwidget)


        self.retranslateUi()
        QMetaObject.connectSlotsByName(self)
    def setEvent(self):
        self.download_audio_btn.clicked.connect( \
            lambda:self.download_audio_event())
        self.download_video_btn.clicked.connect( \
            lambda:self.download_video_event())
        self.select_output_btn.clicked.connect( \
            lambda:self.select_output_event())
        self.download_playlist_btn.clicked.connect( \
            lambda:self.download_playlist_event())
        
        # self.download_list
        # self.scroll_area
        # self.list_view
    def download_audio_event(self):
        #self.add_item("1.jpg")
        self.add_progress_bar()
    def download_video_event(self):
        title, second = self.yt.get_YouTube_info()
        print(title, second)
    def select_output_event(self):
        self.yt.set_output_path(str(QFileDialog.getExistingDirectory(self, "Select Directory")))
        print(self.yt.output_path)
    def download_playlist_event(self):
        pass
        
    def delete_item(self):
        #self.list_view.clear()
        for item in self.list_view.selectedItems():
            self.list_view.takeItem(self.list_view.row(item))
    def add_progress_bar(self):
        progress_delegate = ProgressDelegate(self.list_view)
        #image_delegate = ImageDelegate(self.list_view)

        self.list_view.setItemDelegateForColumn(2, progress_delegate)
        model = QStandardItemModel(0, 3)
        model.setHorizontalHeaderLabels(["Image","Title", "Progress"])
        data = [("Baharak", 10), ("Darwaz", 60),
        ("Fays abad", 20), ("Ishkashim", 80), 
        ("Jurm", 100),("Baharak", 10), ("Darwaz", 60),
        ("Fays abad", 20), ("Ishkashim", 80), 
        ("Jurm", 100),("Baharak", 10), ("Darwaz", 60),
        ("Fays abad", 20), ("Ishkashim", 80), 
        ("Jurm", 100),("Baharak", 10), ("Darwaz", 60),
        ("Fays abad", 20), ("Ishkashim", 80), 
        ("Jurm", 100)]
        for _title, _progress in data:
            pixmap = QPixmap("1.jpg") \
                .scaled(QSize(55, 55), \
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.FastTransformation)
            
            it_image = QStandardItem(QIcon(pixmap), '')
            it_name = QStandardItem(_title)
            it_progress = QStandardItem()
            it_progress.setData(_progress, Qt.ItemDataRole.UserRole+1000)
            model.appendRow([it_image, it_name, it_progress])
        self.list_view.setModel(model)
    def set_download_list(self):
        self.download_list = QScrollArea(self.centralwidget)
        self.download_list.setGeometry(QRect(10, 80, 640, 500))
        self.download_list.setWidgetResizable(True)
        self.download_list.setObjectName("download_list")
        self.scroll_area = QWidget()
        self.scroll_area.setGeometry(QRect(0, 0, 640, 500))
        self.scroll_area.setObjectName("scroll_area")
        self.list_view = QTableView(self.scroll_area)
        self.list_view.setGeometry(QRect(0, 0, 640, 500))
        self.list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.list_view.setObjectName("list_view")
        self.list_view.horizontalHeader().setStretchLastSection(True)
        self.list_view.verticalHeader().setDefaultSectionSize(50)
        self.download_list.setWidget(self.scroll_area)
        
    def set_horizontalLayout(self):
        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QRect(10, 10, 641, 61))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
    def set_btn(self):
        self.download_audio_btn = QPushButton(self.horizontalLayoutWidget)
        self.download_audio_btn.setObjectName("download_audio_btn")
        self.horizontalLayout.addWidget(self.download_audio_btn)
   
        self.download_video_btn = QPushButton(self.horizontalLayoutWidget)
        self.download_video_btn.setObjectName("download_video_btn")
        self.horizontalLayout.addWidget(self.download_video_btn)
        
        self.select_output_btn = QPushButton(self.horizontalLayoutWidget)
        self.select_output_btn.setObjectName("select_output_btn")
        self.horizontalLayout.addWidget(self.select_output_btn)
        
        self.download_playlist_btn = QPushButton(self.horizontalLayoutWidget)
        self.download_playlist_btn.setObjectName("download_playlist_btn")
        self.horizontalLayout.addWidget(self.download_playlist_btn)
        self.set_sizePolicy()
    def set_sizePolicy(self):
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.download_audio_btn.sizePolicy().hasHeightForWidth())        
        sizePolicy.setHeightForWidth(self.download_video_btn.sizePolicy().hasHeightForWidth())        
        sizePolicy.setHeightForWidth(self.select_output_btn.sizePolicy().hasHeightForWidth())
        sizePolicy.setHeightForWidth(self.download_playlist_btn.sizePolicy().hasHeightForWidth())
        self.download_audio_btn.setSizePolicy(sizePolicy)
        self.download_video_btn.setSizePolicy(sizePolicy)
        self.select_output_btn.setSizePolicy(sizePolicy)
        self.download_playlist_btn.setSizePolicy(sizePolicy)
    def retranslateUi(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("mainWindow", "YouTube下載器"))
        self.download_audio_btn.setText(_translate("mainWindow", "下載音訊"))
        self.download_video_btn.setText(_translate("mainWindow", "下載影片"))
        self.select_output_btn.setText(_translate("mainWindow", "輸出資料夾"))
        self.download_playlist_btn.setText(_translate("mainWindow", "下載播放清單"))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = Ui_mainWindow()
    myWin.show()
    sys.exit(app.exec())
