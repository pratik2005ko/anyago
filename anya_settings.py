from PyQt5.QtCore import Qt, QTimer
from app_discovery import discover_apps
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys

ALIASES_PATH = os.path.expanduser("~/anyago/aliases.json")

def load_aliases():
    try:
        with open(ALIASES_PATH, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_aliases(aliases):
    with open(ALIASES_PATH, 'w') as f:
        json.dump(aliases, f, indent=4)

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anya Settings")
        self.setFixedSize(500, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: monospace;
            }
            QLineEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QPushButton {
                background-color: #7c3aed;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6d28d9;
            }
            QScrollArea {
                border: none;
            }
        """)

        self.apps = discover_apps()
        self.aliases = load_aliases()
        self.inputs = {}

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # title
        title = QLabel("⚙  Anya Settings — App Hotwords")
        title.setFont(QFont("monospace", 14))
        title.setStyleSheet("color: #cba6f7; margin-bottom: 8px;")
        main_layout.addWidget(title)

        # header
        header = QHBoxLayout()
        header.addWidget(QLabel("App"))
        header.addStretch()
        header.addWidget(QLabel("Hotword"))
        main_layout.addLayout(header)

        # scrollable list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(8)

        # reverse aliases — app_name → hotword
        reverse_aliases = {v: k for k, v in self.aliases.items()}

        for app_name, cmd in sorted(self.apps.items()):
            row = QHBoxLayout()

            label = QLabel(app_name)
            label.setFixedWidth(280)
            label.setStyleSheet("color: #a6adc8; font-size: 12px;")

            inp = QLineEdit()
            inp.setFixedWidth(140)
            inp.setPlaceholderText("hotword...")

            # prefill if alias exists
            if app_name in reverse_aliases:
                inp.setText(reverse_aliases[app_name])

            self.inputs[app_name] = inp

            row.addWidget(label)
            row.addStretch()
            row.addWidget(inp)
            container_layout.addLayout(row)

        container_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # save button
        self.save_btn = QPushButton("Save Hotwords")
        self.save_btn.clicked.connect(self.save)
        main_layout.addWidget(self.save_btn)

    def save(self):
        new_aliases = {} 
        for app_name, inp in self.inputs.items():
            hotword = inp.text().strip().lower()
            if hotword:
                new_aliases[hotword] = app_name
        save_aliases(new_aliases)
        self.save_btn.setText("✓ Saved!")
        QTimer.singleShot(2000, lambda: self.save_btn.setText("Save Hotwords"))

app = QApplication(sys.argv)
window = SettingsWindow()
window.show()
sys.exit(app.exec_())