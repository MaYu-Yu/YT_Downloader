import urllib.request, os, time
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from pathlib import Path
def get_pixmap(url):
    img_name = str(round(time.time()))+".jpg"
    img = Path(img_name)
    if not img.exists():
        urllib.request.urlretrieve(url, img) # download img
    pixmap = QPixmap(img_name)
    pixmap.scaled(25,25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
# delete
    if img.exists():
        os.remove(img)
    return pixmap