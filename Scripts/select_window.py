from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QGridLayout, QButtonGroup, QWidget, QMessageBox, QRadioButton, QDialogButtonBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QRect, QMetaObject

from qt_material import apply_stylesheet

class selectWin(QDialog):
    def __init__(self, resolutions):
        super().__init__()
        self.setFixedSize(650, 350)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        apply_stylesheet(self, theme='dark_pink.xml')
        self.resolution_list = [int(r.replace("p", "")) for r in resolutions]
        self.selected_resolution = None

        self.setup_ui()
        self.setup_radio()

    def add_label(self, text, alignment):
        label = QLabel()
        label.setLineWidth(0)
        label.setAlignment(alignment)
        label.setText(text)
        return label

    def set_video_info(self, info_dict, streams_dict):
        pixmap = QPixmap(info_dict.get("thumbnail_path"))
        pixmap.scaled(25, 25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
        self.video_thumbnail.setScaledContents(True)
        self.video_thumbnail.setPixmap(pixmap)

        self.video_title_label.setText(info_dict.get("title"))
        self.video_author_label.setText(info_dict.get("author"))
        self.video_publish_date_label.setText(str(info_dict.get("publish_date").strftime("%Y/%m/%d")))
        self.video_views_label.setText("{} 次".format(str(info_dict.get("views"))))
        self.video_play_len_label.setText("{} 分{} 秒".format(info_dict.get("play_len") // 60, info_dict.get("play_len") % 60))

        best = True
        for i, resolution in enumerate(self.resolution_list):
            if streams_dict.get(resolution):
                if best:
                    self.resolution_radio_list[i].setChecked(True)
                    best = False
                self.resolution_radio_list[i].setHidden(False)
            else:
                self.resolution_radio_list[i].setHidden(True)

    def setup_ui(self):
        # Info 區塊
        self.info_layout_widget = QWidget(self)
        self.info_layout_widget_1 = QWidget(self)
        self.info_layout = QVBoxLayout(self.info_layout_widget)
        self.info_layout_1 = QVBoxLayout(self.info_layout_widget_1)
        # 畫質選擇按鈕區塊
        self.resolution_layout_widget = QWidget(self)
        self.resolution_layout_widget.setGeometry(QRect(70, 240, 450, 61))
        self.resolution_layout = QGridLayout(self.resolution_layout_widget)
        self.resolution_layout.setContentsMargins(0, 0, 0, 0)
        self.button_box = QDialogButtonBox(self)
        self.button_box.setGeometry(QRect(150, 310, 201, 41))
        self.button_box.setOrientation(Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        QMetaObject.connectSlotsByName(self)

        self.setWindowTitle("影片資訊")
        self.resolution_layout_label = self.add_label("畫質選擇", Qt.AlignmentFlag.AlignCenter)
        self.author_label = self.add_label("作者:", Qt.AlignmentFlag.AlignCenter)
        self.publish_date_label = self.add_label("發布日期:", Qt.AlignmentFlag.AlignCenter)
        self.views_label = self.add_label("點閱次數:", Qt.AlignmentFlag.AlignCenter)
        self.play_len_label = self.add_label("影片時間:", Qt.AlignmentFlag.AlignCenter)
        self.video_thumbnail = QLabel(self)
        self.video_title_label = QLabel(self)
        self.video_author_label = QLabel(self.info_layout_widget_1)
        self.video_publish_date_label = QLabel(self.info_layout_widget_1)
        self.video_views_label = QLabel(self.info_layout_widget_1)
        self.video_play_len_label = QLabel(self.info_layout_widget_1)
        style = "font-weight: bold; font-size: 16px;"
        style_1 = "font-weight: bold; font-size: 14px; color: aqua;"
        
        self.resolution_layout_label.setStyleSheet(style_1)
        self.author_label.setStyleSheet(style_1)
        self.publish_date_label.setStyleSheet(style_1)
        self.views_label.setStyleSheet(style_1)
        self.play_len_label.setStyleSheet(style_1)        
        
        self.video_title_label.setStyleSheet(style)
        self.video_author_label.setStyleSheet(style)
        self.video_publish_date_label.setStyleSheet(style)
        self.video_views_label.setStyleSheet(style)
        self.video_play_len_label.setStyleSheet(style)
        
        
        self.info_layout_widget.setGeometry(QRect(200, 20, 230, 150))
        self.info_layout_widget_1.setGeometry(QRect(350, 20, 230, 150))
        self.video_thumbnail.setGeometry(QRect(10, 10, 250, 171))
        self.video_title_label.setGeometry(QRect(0, 180, 550, 70))

        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.info_layout.addWidget(self.author_label)
        self.info_layout.addWidget(self.publish_date_label)
        self.info_layout.addWidget(self.views_label)
        self.info_layout.addWidget(self.play_len_label)

        self.info_layout_1.setContentsMargins(0, 0, 0, 0)
        self.info_layout_1.addWidget(self.video_author_label)
        self.info_layout_1.addWidget(self.video_publish_date_label)
        self.info_layout_1.addWidget(self.video_views_label)
        self.info_layout_1.addWidget(self.video_play_len_label)

    def setup_radio(self):
        self.resolution_layout.addWidget(self.resolution_layout_label, 0, 0, 1, 5)
        self.resolution_radio_list = [QRadioButton(self.resolution_layout_widget) for _ in range(len(self.resolution_list))]
        self.resolution_radio_group = QButtonGroup(self)
        for i, resolution in enumerate(self.resolution_list):
            self.resolution_radio_group.addButton(self.resolution_radio_list[i], resolution)
            self.resolution_radio_list[i].setText(str(resolution))
            self.resolution_radio_list[i].setHidden(True)

        for i, resolution in enumerate(self.resolution_list):
            self.resolution_layout.addWidget(self.resolution_radio_list[i], 1, i, 1, 1)

    def start(self, info_dict, streams_dict):
        self.set_video_info(info_dict, streams_dict)
        result = self.exec()
        if result:
            return self.selected_resolution
        return None

    def accept(self):
        self.selected_resolution = self.resolution_radio_group.checkedId()
        super().accept()

    def reject(self):
        self.selected_resolution = None
        super().reject()


class playlistWin(QWidget):
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
            return None