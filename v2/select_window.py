from qt_material import apply_stylesheet
from PyQt6.QtWidgets import * 
from PyQt6.QtGui import * 
from PyQt6.QtCore import *
import pyperclip# clipboard
# my lib
class select_win(QDialog):
    def __init__(self, res):
        QDialog.__init__(self)
        self.setFixedSize(550, 350)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        apply_stylesheet(self, theme='dark_pink.xml')
        self.res_list = list()
        for r in res:
            self.res_list.append(int(r.replace("p", "")))
        self.res = None
        
        self.gridLayoutWidget = QWidget(self)
        self.gridLayoutWidget.setGeometry(QRect(70, 240, 450, 61))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0) 
        self.set_QDialogButtonBox()
        self.set_yt_ui()
        
        self.set_radio()
        self.set_static_txt()

    def set_yt_info(self, info_dict, streams_dict):
        pixmap = QPixmap(info_dict.get("thumbnail_path"))
        pixmap.scaled(25,25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setPixmap(pixmap)
        
        self.title.setText(info_dict.get("title"))
        self.author.setText(info_dict.get("author"))
        self.publish_date.setText(str(info_dict.get("publish_date")))
        self.views.setText(str(info_dict.get("views")))
        self.play_len.setText("{}分 : {}秒".format(info_dict.get("play_len") // 60, info_dict.get("play_len") % 60))
        
        best = True
        for i in range(len(self.res_list)):
            if streams_dict.get(self.res_list[i]):
                if best:
                    self.radio_list[i].setChecked(best)
                    best = False
                self.radio_list[i].setHidden(False)
            else:
                self.radio_list[i].setHidden(True)
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
        self.radio_list = [QRadioButton(self.gridLayoutWidget) for _ in range(len(self.res_list))]
        self.radio_group = QButtonGroup(self)
        for i in range(len(self.res_list)):
            self.radio_group.addButton(self.radio_list[i], self.res_list[i])
            self.radio_list[i].setText(str(self.res_list[i]))
            self.gridLayout.addWidget(self.radio_list[i], 1, i, 1, 1)
        # audio
        # self.radio_group.addButton(self.radio_list[-1], 8787)
        # self.radio_list[5].setText("Audio")
        # self.gridLayout.addWidget(self.radio_list[-1], 1, 5, 1, 1)        
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
    def start(self, info_dict, streams_dict):
        self.set_yt_info(info_dict, streams_dict)
        r =self.exec()
        if r:
            return self.res
        return None
    def accept(self):
        self.res = self.radio_group.checkedId()
        super().accept()
    def reject(self):
        self.res = ''
        super().accept()      
        
class playlist_win(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(1250, 200, 200, 150)
        self.msg_box = QMessageBox(self)
        self.msg_box.setIcon(QMessageBox.Icon.Question)
        self.msg_box.setWindowTitle('下載播放清單')
        self.msg_box.setText('選擇視頻或是音樂')
        self.audio_btn = self.msg_box.addButton('音樂', QMessageBox.ButtonRole.AcceptRole)
        self.video_btn = self.msg_box.addButton('視頻', QMessageBox.ButtonRole.YesRole)
        self.cancel_btn = self.msg_box.addButton(QMessageBox.StandardButton.Cancel)
        self.cancel_btn.setHidden(True)
    def start(self):
        self.msg_box.exec()
        if self.msg_box.clickedButton() == self.audio_btn:
            return 8787
        elif self.msg_box.clickedButton() == self.video_btn:
            return 1
        else:
            return 0