from PySide6.QtGui import QPixmap,Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QSlider
from pathlib import Path


class ImageViewer(QWidget):
    def __init__(self, file, parent):
        super().__init__(parent)
        self.file = Path(file).__str__()

        layout = QVBoxLayout()
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.updateImageSize()

        scrollArea = QScrollArea()
        scrollArea.setWidget(self.imageLabel)
        scrollArea.setWidgetResizable(True)
        scrollArea.setStyleSheet("border: 0px; margin: 0; padding: 0px; background: white;")


        layout.addWidget(scrollArea)


        self.setLayout(layout)

    def updateImageSize(self):
        image = QPixmap(self.file)
        if image.width() > self.parent().width() or image.height() > self.parent().height():
            self.image = image.scaled(self.parent().width()-28, (self.parent().height() - 50), Qt.KeepAspectRatio)
        else:
            self.image = image
        self.imageLabel.setPixmap(self.image)

