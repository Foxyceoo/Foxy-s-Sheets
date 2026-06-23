import sys
import json
import os
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QWidget, QGridLayout, QVBoxLayout, 
                             QPushButton, QFileDialog, QListWidget)
from PyQt6.QtCore import Qt, QPoint, QTimer, QEvent

# --- 1. LỚP DANH SÁCH NHẠC ---
class PlaylistWindow(QWidget):
    def __init__(self, parent_ctrl):
        super().__init__()
        self.parent_ctrl = parent_ctrl
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(90, 100, 200, 350)
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        self.btn_delete = QPushButton("Xóa bài")
        self.btn_delete.clicked.connect(self.delete_selected)
        layout.addWidget(self.btn_delete)

    def delete_selected(self):
        item = self.list_widget.currentItem()
        if item:
            self.parent_ctrl.remove_song(item.text())
            self.refresh_list(self.parent_ctrl.playlist)

    def refresh_list(self, playlist):
        self.list_widget.clear()
        for path in playlist: self.list_widget.addItem(os.path.basename(path))

# --- 2. LỚP CHÍNH (OVERLAY) ---
class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.timers = [] # Khởi tạo danh sách quản lý nốt nhạc
        
        self.container = QWidget(self)
        self.container.setStyleSheet("background-color: rgba(50, 150, 255, 50); border: 2px dashed #FFF; border-radius: 10px;")
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.container)
        
        self.grid = QGridLayout(self.container)
        for i in range(15):
            dot = QWidget()
            dot.setFixedSize(20, 20)
            dot.setStyleSheet("background-color: red; border-radius: 10px;")
            self.grid.addWidget(dot, i // 5, i % 5)
        self.container.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            self.dragPos = event.globalPosition().toPoint() - self.pos()
            return True
        elif event.type() == QEvent.Type.MouseMove and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.dragPos)
            return True
        return super().eventFilter(obj, event)

    def load_and_play(self, path):
        self.stop_playing()
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for note in data[0].get("songNotes", []):
                t = QTimer(); t.setSingleShot(True)
                t.timeout.connect(lambda k=note["key"]: self.play_animation(k))
                t.start(note["time"])
                self.timers.append(t)

    def stop_playing(self):
        for t in self.timers: t.stop()
        self.timers.clear()

    def play_animation(self, key_name):
        try:
            parts = key_name.replace("Key", " ").split()
            col, row = int(parts[0]) - 1, int(parts[1]) % 3
            w = self.grid.itemAtPosition(row, col).widget()
            if w:
                w.setStyleSheet("background-color: yellow; border-radius: 10px;")
                QTimer.singleShot(150, lambda: w.setStyleSheet("background-color: red; border-radius: 10px;"))
        except: pass

# --- 3. LỚP ĐIỀU KHIỂN ---
class ControlWindow(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        self.ds_path = os.path.join(str(Path.home()), "Documents", "DS")
        self.config_file = os.path.join(self.ds_path, "playlist.txt")
        os.makedirs(self.ds_path, exist_ok=True)
        self.playlist = []
        self.load_playlist()
        self.playlist_win = PlaylistWindow(self)
        
        layout = QVBoxLayout(self)
        for text, func in [("+", self.import_files), ("≡", self.toggle_list), ("▶", self.play_song), ("⏹", self.main_win.stop_playing)]:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            layout.addWidget(btn)

    def load_playlist(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f: self.playlist = [l.strip() for l in f if l.strip()]

    def remove_song(self, name):
        self.playlist = [p for p in self.playlist if os.path.basename(p) != name]
        with open(self.config_file, "w") as f: f.write("\n".join(self.playlist))

    def import_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Chọn file", "", "JSON (*.json)")
        for f in files:
            dest = os.path.join(self.ds_path, os.path.basename(f))
            shutil.copy2(f, dest)
            self.playlist.append(dest)
        with open(self.config_file, "w") as f: f.write("\n".join(self.playlist))

    def toggle_list(self):
        if self.playlist_win.isVisible(): self.playlist_win.hide()
        else: self.playlist_win.refresh_list(self.playlist); self.playlist_win.show()

    def play_song(self):
        item = self.playlist_win.list_widget.currentItem()
        if item: self.main_win.load_and_play(os.path.join(self.ds_path, item.text()))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = OverlayWindow()
    ctrl_win = ControlWindow(main_win)
    ctrl_win.show()
    main_win.show()
    sys.exit(app.exec())
