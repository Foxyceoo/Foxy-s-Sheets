import sys
import json
import os
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QWidget, QGridLayout, QVBoxLayout, 
                             QPushButton, QFileDialog, QMessageBox, QListWidget)
from PyQt6.QtCore import Qt, QPoint, QTimer, QEvent

# --- CLASS PLAYLISTWINDOW (Giữ nguyên) ---
class PlaylistWindow(QWidget):
    def __init__(self, parent_ctrl):
        super().__init__()
        self.parent_ctrl = parent_ctrl
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(90, 100, 200, 350)
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("QListWidget { background-color: rgba(50, 50, 50, 230); color: white; border: 1px solid #777; border-radius: 10px; }")
        layout.addWidget(self.list_widget)
        self.btn_delete = QPushButton("Xóa bài đã chọn")
        self.btn_delete.setStyleSheet("background-color: #880000; color: white; border-radius: 5px; min-height: 30px;")
        self.btn_delete.clicked.connect(self.delete_selected_song)
        layout.addWidget(self.btn_delete)

    def delete_selected_song(self):
        current_item = self.list_widget.currentItem()
        if not current_item: return
        song_name = current_item.text()
        full_path = next((p for p in self.parent_ctrl.playlist if os.path.basename(p) == song_name), "")
        if os.path.exists(full_path): os.remove(full_path)
        self.parent_ctrl.playlist.remove(full_path)
        with open(self.parent_ctrl.config_file, "w", encoding="utf-8") as f:
            for p in self.parent_ctrl.playlist: f.write(p + "\n")
        self.refresh_list(self.parent_ctrl.playlist)

    def refresh_list(self, playlist):
        self.list_widget.clear()
        for path in playlist: self.list_widget.addItem(os.path.basename(path))

# --- CLASS OVERLAYWINDOW ---
class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.target_ratio = 1.543
        
        self.container = QWidget(self)
        self.container.setStyleSheet("background-color: rgba(50, 150, 255, 50); border: 2px dashed #FFFFFF; border-radius: 10px;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)
        
        self.grid = QGridLayout(self.container)
        for i in range(15):
            dot = QWidget()
            dot.setFixedSize(20, 20)
            dot.setStyleSheet("background-color: red; border-radius: 10px;")
            self.grid.addWidget(dot, i // 5, i % 5)
        
        self.dragPos = QPoint()
        self.container.installEventFilter(self) # ĐÃ MỞ COMMENT

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragPos = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.dragPos)
            event.accept()

    def eventFilter(self, obj, event):
        if obj == self.container:
            if event.type() == QEvent.Type.MouseButtonPress:
                self.mousePressEvent(event)
                return True
            elif event.type() == QEvent.Type.MouseMove:
                self.mouseMoveEvent(event)
                return True
        return super().eventFilter(obj, event)

    def load_and_play(self, path):
        print(f"Bắt đầu chạy: {path}")

    def resizeEvent(self, event):
        new_width = self.width()
        new_height = int(new_width / self.target_ratio)
        if abs(self.height() - new_height) > 2: self.resize(new_width, new_height)
        super().resizeEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        new_width = self.width() + int(delta/5)
        if new_width > 100: self.resize(new_width, self.height())

# --- CLASS CONTROLWINDOW ---
class ControlWindow(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(20, 100, 60, 300)
        
        self.ds_path = os.path.join(str(Path.home()), "Documents", "DS")
        self.config_file = os.path.join(self.ds_path, "playlist_config.txt")
        if not os.path.exists(self.ds_path): os.makedirs(self.ds_path)
        
        self.playlist = []
        self.load_playlist_from_config()
        self.playlist_win = PlaylistWindow(self)

        layout = QVBoxLayout(self)
        self.container = QWidget(self)
        self.container.setStyleSheet("QWidget { background-color: rgba(50, 50, 50, 200); border: 2px solid #777777; border-radius: 10px; } QPushButton { background-color: #444; color: white; border-radius: 5px; min-height: 35px; }")
        container_layout = QVBoxLayout(self.container)
        
        self.btn_add = QPushButton("+")
        self.btn_add.clicked.connect(self.hide_playlist)
        self.btn_add.clicked.connect(self.import_files)
        container_layout.addWidget(self.btn_add)
        
        self.btn_list = QPushButton("≡")
        self.btn_list.clicked.connect(self.toggle_list)
        container_layout.addWidget(self.btn_list)
        
        self.btn_play = QPushButton("▶")
        self.btn_play.clicked.connect(self.play_current_song)
        container_layout.addWidget(self.btn_play)
        
        for text in ["⏱", "🔁", "👁"]:
            container_layout.addWidget(QPushButton(text))
        layout.addWidget(self.container)

    def hide_playlist(self): self.playlist_win.hide()
    def toggle_list(self):
        if self.playlist_win.isVisible(): self.playlist_win.hide()
        else:
            self.playlist_win.refresh_list(self.playlist)
            self.playlist_win.show()

    def play_current_song(self):
        selected_item = self.playlist_win.list_widget.currentItem()
        if not selected_item: return
        self.main_win.load_and_play(os.path.join(self.ds_path, selected_item.text()))

    def import_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Chọn file", "", "Data Files (*.json *.txt)")
        if files:
            for p in files:
                dest = os.path.join(self.ds_path, os.path.basename(p))
                if not os.path.exists(dest): shutil.copy2(p, dest)
                with open(self.config_file, "a", encoding="utf-8") as f: f.write(dest + "\n")
            self.load_playlist_from_config()

    def load_playlist_from_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.playlist = [l.strip() for l in f.readlines() if l.strip()]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = OverlayWindow()
    ctrl_win = ControlWindow(main_win)
    ctrl_win.show()
    main_win.resize(400, 200)
    main_win.show()
    sys.exit(app.exec())
