#!/usr/bin/env python3
import sys
import os
import signal
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout
from PyQt6.QtGui import QPainter, QPainterPath, QPixmap, QColor, QPen, QCursor, QImageReader, QImage
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty, QEasingCurve, QSize, QThread, pyqtSignal, QParallelAnimationGroup, QPoint

# возвращаем стандартное поведение Ctrl+C в терминале
signal.signal(signal.SIGINT, signal.SIG_DFL)

# твой путь к обоям
WALLS_DIR = os.path.expanduser("~/Documents/walls/walls-catppuccin-mocha")

class ImageLoader(QThread):
    loaded = pyqtSignal(int, QImage)

    def __init__(self, paths):
        super().__init__()
        self.paths = paths

    def run(self):
        # грузим картинки под размер раскрытой карточки
        for i, path in enumerate(self.paths):
            reader = QImageReader(path)
            reader.setAutoTransform(True)
            orig_size = reader.size()
            
            if orig_size.isValid():
                orig_ratio = orig_size.width() / orig_size.height()
                new_h = 600
                new_w = int(new_h * orig_ratio)
                reader.setScaledSize(QSize(new_w, new_h))
            
            img = reader.read()
            if not img.isNull():
                self.loaded.emit(i, img)

class SlantedCard(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.slant = 80
        self.progress = 0.0
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # заглушка цвета catppuccin
        self.pixmap = QPixmap(600, 600)
        self.pixmap.fill(QColor(24, 24, 37))

    def set_image(self, img):
        self.pixmap = QPixmap.fromImage(img)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        path = QPainterPath()
        path.moveTo(self.slant, 0)
        path.lineTo(self.width(), 0)
        path.lineTo(self.width() - self.slant, self.height())
        path.lineTo(0, self.height())
        path.closeSubpath()

        painter.setClipPath(path)
        
        # вписываем картинку
        scale = max(self.width() / self.pixmap.width(), self.height() / self.pixmap.height())
        draw_w = self.pixmap.width() * scale
        draw_h = self.pixmap.height() * scale
        x = (self.width() - draw_w) / 2
        y = (self.height() - draw_h) / 2
        painter.drawPixmap(int(x), int(y), int(draw_w), int(draw_h), self.pixmap)

        # затемняем неактивные
        painter.setClipping(False)
        if self.progress < 1.0:
            painter.fillPath(path, QColor(0, 0, 0, int(150 * (1 - self.progress))))

        # Обводка есть всегда: у неактивных прозрачная (alpha=60), у активной сплошная (alpha=255)
        alpha = int(60 + 195 * self.progress)
        pen = QPen(QColor(255, 255, 255, alpha))
        pen.setWidth(2)
        painter.strokePath(path, pen)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            os.system(f"plasma-apply-wallpaperimage '{self.image_path}' &")
            QApplication.quit()

class WallPicker(QWidget):
    def __init__(self):
        super().__init__()
        # Убрали Tool, чтобы wayland не резал фуллскрин
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.screen_rect = QApplication.primaryScreen().geometry()
        self.setGeometry(self.screen_rect)

        # Новые габариты для карточек (стали шире)
        self.narrow_w = 180
        self.expanded_w = 600
        self.card_height = 500
        self.slant = 80

        self.bg = QWidget(self)
        self.bg.setGeometry(self.screen_rect)
        self.bg.setStyleSheet("background: rgba(30, 30, 46, 0.85);")
        self.bg.lower()

        valid_ext = ('.jpg', '.jpeg', '.png', '.webp')
        walls = [os.path.join(WALLS_DIR, f) for f in os.listdir(WALLS_DIR) if f.lower().endswith(valid_ext)]
        walls.sort()

        self.cards = []
        self.h_layout = QHBoxLayout() # заглушка для совместимости со старым кодом
        for w in walls:
            card = SlantedCard(w, self)
            card.show()
            self.cards.append(card)

        self._scroll_offset = 0.0
        self.target_index = 0
        
        self.anim = QPropertyAnimation(self, b"scroll_offset")
        self.anim.setEasingCurve(QEasingCurve.Type.OutExpo)
        self.anim.setDuration(400)

        self.loader = ImageLoader(walls)
        self.loader.loaded.connect(self.on_image_loaded)
        self.loader.start()

        self.update_layout()

    def showEvent(self, event):
        super().showEvent(event)
        self.activateWindow()
        self.setFocus()

    def on_image_loaded(self, index, img):
        if index < len(self.cards):
            self.cards[index].set_image(img)

    @pyqtProperty(float)
    def scroll_offset(self):
        return self._scroll_offset

    @scroll_offset.setter
    def scroll_offset(self, val):
        self._scroll_offset = val
        self.update_layout()

    def update_layout(self):
        if not self.cards: return

        x_pos = [0] * len(self.cards)
        for i, card in enumerate(self.cards):
            dist = abs(i - self._scroll_offset)
            progress = max(0.0, 1.0 - dist)
            card.progress = progress
            w = int(self.narrow_w + (self.expanded_w - self.narrow_w) * progress)
            card.setFixedSize(w, self.card_height)

            if i > 0:
                x_pos[i] = x_pos[i-1] + self.cards[i-1].width() - self.slant - 1

        focal_index = int(self._scroll_offset)
        fraction = self._scroll_offset - focal_index

        c1 = x_pos[focal_index] + self.cards[focal_index].width() / 2
        if focal_index + 1 < len(self.cards):
            c2 = x_pos[focal_index + 1] + self.cards[focal_index + 1].width() / 2
            focal_x = c1 + (c2 - c1) * fraction
        else:
            focal_x = c1

        screen_center = self.width() / 2
        offset_x = screen_center - focal_x
        y_pos = int((self.height() - self.card_height) / 2)

        sorted_indices = sorted(range(len(self.cards)), key=lambda i: -abs(i - self._scroll_offset))
        for i in sorted_indices:
            card = self.cards[i]
            card.move(int(x_pos[i] + offset_x), y_pos)
            card.raise_()

    def set_target_index(self, index):
        if not self.cards: return
        self.target_index = max(0, min(index, len(self.cards) - 1))
        self.anim.stop()
        self.anim.setEndValue(float(self.target_index))
        self.anim.start()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta == 0:
            delta = event.angleDelta().x()
        
        if delta > 0:
            self.set_target_index(self.target_index - 1)
        elif delta < 0:
            self.set_target_index(self.target_index + 1)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()
        elif event.key() in (Qt.Key.Key_Right, Qt.Key.Key_D):
            self.set_target_index(self.target_index + 1)
        elif event.key() in (Qt.Key.Key_Left, Qt.Key.Key_A):
            self.set_target_index(self.target_index - 1)
        elif event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            os.system(f"plasma-apply-wallpaperimage '{self.cards[self.target_index].image_path}' &")
            QApplication.quit()

if __name__ == '__main__':
    # принудительно говорим qt использовать wayland
    os.environ["QT_QPA_PLATFORM"] = "wayland"

    app = QApplication(sys.argv)
    app.setDesktopSettingsAware(False)

    if not os.path.exists(WALLS_DIR):
        print(f"Ошибка: папка с обоями не найдена ({WALLS_DIR})")
        sys.exit(1)
        
    picker = WallPicker()
    picker.showFullScreen()
    picker.raise_()
    picker.activateWindow()
    sys.exit(app.exec())
