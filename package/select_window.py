from PyQt6.QtWidgets import * 
from PyQt6.QtGui import * 
from PyQt6.QtCore import *
import urllib.request
from qt_material import apply_stylesheet
class MyPopup(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        apply_stylesheet(self, theme='dark_pink.xml')
        self.res_list = ["4320p", "2160p", "1080p", "720p", "480p"]
        self.res = ''
        
        self.setObjectName("select_video_window")
        self.setFixedSize(550, 350)
        self.gridLayoutWidget = QWidget(self)
        self.gridLayoutWidget.setGeometry(QRect(70, 240, 450, 61))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0) 
        self.set_QDialogButtonBox()
        self.set_yt_ui()
        
        self.set_radio()
        self.set_static_txt()

    def set_yt_info(self, thumbnail, author, publish_date, views, play_len, title, ress, num):
        urllib.request.urlretrieve(thumbnail, "./img/"+str(num)+".jpg")
        #data = urllib.request.urlopen(thumbnail).read()
        pixmap = QPixmap("./img/"+str(num)+".jpg")
        #pixmap.loadFromData(data)
        pixmap.scaled(self.thumbnail.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setPixmap(pixmap)
        
        self.title.setText(title)
        self.author.setText(author)
        self.publish_date.setText(publish_date)
        self.views.setText(views)
        self.play_len.setText(play_len)
        
        best = True
        #https://www.youtube.com/watch?v=Z2RYzmU6pV0&list=LL&index=1
        for i in range(len(self.radio_list) - 1):
            if self.res_list[i].replace("p", "") in ress:
                if best:
                    self.radio_list[i].setChecked(best)
                    best = False
                self.radio_list[i].setHidden(False)
            else:
                self.radio_list[i].setHidden(True)
                
        self.radio_list[5].setHidden(False)
    def set_yt_ui(self):
        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QRect(270, 20, 230, 150))
        self.verticalLayoutWidget_1 = QWidget(self)
        self.verticalLayoutWidget_1.setGeometry(QRect(340, 20, 230, 150))        
        
        self.thumbnail = QLabel(self)
        self.title = QLabel(self)
        self.label_3 = QLabel(self.verticalLayoutWidget)
        self.label_4 = QLabel(self.verticalLayoutWidget)
        self.label_5 = QLabel(self.verticalLayoutWidget)
        self.label_6 = QLabel(self.verticalLayoutWidget)   
        
        self.author = QLabel(self.verticalLayoutWidget_1)
        self.publish_date = QLabel(self.verticalLayoutWidget_1)
        self.views = QLabel(self.verticalLayoutWidget_1)
        self.play_len = QLabel(self.verticalLayoutWidget_1)
        
        self.thumbnail.setGeometry(QRect(10, 10, 250, 171))
        self.title.setGeometry(QRect(0, 180, 550, 70))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.addWidget(self.label_3)
        self.verticalLayout.addWidget(self.label_4)
        self.verticalLayout.addWidget(self.label_5)
        self.verticalLayout.addWidget(self.label_6)
        
        self.verticalLayout_1 = QVBoxLayout(self.verticalLayoutWidget_1)
        self.verticalLayout_1.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_1.addWidget(self.author)
        self.verticalLayout_1.addWidget(self.publish_date)
        self.verticalLayout_1.addWidget(self.views)
        self.verticalLayout_1.addWidget(self.play_len)
    def set_radio(self):
    
        self.label_ = QLabel(self.gridLayoutWidget)
        self.label_.setLineWidth(0)
        self.label_.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout.addWidget(self.label_, 0, 0, 1, 5)
        self.radio_list = [QRadioButton(self.gridLayoutWidget) for _ in range(6)]
        self.radio_group = QButtonGroup(self)
        for i in range(len(self.radio_list)-1):
            self.radio_group.addButton(self.radio_list[i], int(self.res_list[i].replace("p", "")))
            self.radio_list[i].setText(self.res_list[i])
            self.gridLayout.addWidget(self.radio_list[i], 1, i, 1, 1)
        # audio
        self.radio_group.addButton(self.radio_list[5], 8787)
        self.radio_list[5].setText("Audio")
        self.gridLayout.addWidget(self.radio_list[5], 1, 5, 1, 1)        
    def set_QDialogButtonBox(self):
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setGeometry(QRect(150, 310, 201, 41))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok) 
        self.buttonBox.accepted.connect(self.accept) # type: ignore
        self.buttonBox.rejected.connect(self.reject) # type: ignore
        QMetaObject.connectSlotsByName(self)
    def set_static_txt(self):
        self.setWindowTitle("影片畫質選擇")
        self.label_.setText("畫質選擇")
        self.label_3.setText("作者:")
        self.label_4.setText("發布日期:")
        self.label_5.setText("點閱人數:")
        self.label_6.setText("影片時間:")
    def start(self):
        r =self.exec()
        if r:
            return self.res
        return ''
    def accept(self):
        self.res = str(self.radio_group.checkedId()) 
        super().accept()
    def reject(self):
        self.res = ''
        super().accept()        
class loading_gif(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(620, 350)
        self.move(QPoint(800, 50))
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("main-widget")
        
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName("lb1")
        
        self.setCentralWidget(self.centralwidget)
        self.movie = QMovie("./img/loading.gif")
        self.label.setMovie(self.movie)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.startAnimation()
  
    def startAnimation(self):
        self.movie.start()
  
    def stopAnimation(self):
        self.movie.stop()