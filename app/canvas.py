from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QImageReader, QPainter, QPixmap
from PyQt6.QtWidgets import QWidget

__antialiasing__ = QPainter.RenderHint.Antialiasing
__pixmap_transform__ = QPainter.RenderHint.SmoothPixmapTransform


class Canvas(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.pixmap = QPixmap()

    def _get_max_scale(self):
        if self.pixmap.isNull():
            return 1.0

        canvas = super().size()
        image = self.pixmap

        canvas_aspect = canvas.width() / canvas.height()
        image_aspect = image.width() / image.height()

        if canvas_aspect < image_aspect:
            return canvas.width() / image.width()

        return canvas.height() / image.height()

    def _get_center_offset(self):
        canvas = super().size()
        image = self.pixmap

        scale = self._get_max_scale()
        offset_x = (canvas.width() - image.width() * scale) / 2
        offset_y = (canvas.height() - image.height() * scale) / 2

        return int(offset_x), int(offset_y)

    def load_image(self, image_path):
        image = QImageReader(image_path).read()
        self.pixmap = QPixmap.fromImage(image)

        self.update()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHints(__antialiasing__ | __pixmap_transform__)

        painter.translate(QPoint(*self._get_center_offset()))
        painter.scale(*[self._get_max_scale()] * 2)

        painter.drawPixmap(0, 0, self.pixmap)