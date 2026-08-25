import sys, os, psutil
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QScrollArea, QFrame,
                             QProgressBar, QFileDialog)
from PySide6.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent
from PySide6.QtCore import QThread, Signal, Qt, QTimer
from agent_engine import AgentEngine

class AgentWorker(QThread):
    finished = Signal(object)

    def __init__(self, user_input):
        super().__init__()
        self.user_input = user_input
        self.engine = AgentEngine()

    def run(self):
        result = self.engine.process_user_intent(self.user_input)
        self.finished.emit(result)

class CommercialAgentUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("APEX AI - Advanced Neural Workspace")
        self.resize(1020, 740)
        self.setStyleSheet("""
            QWidget { background-color: #0A0D14; color: #E2E8F0; font-family: 'Segoe UI', sans-serif; }
            QFrame#sidebar { background-color: #0F141C; border-right: 1px solid #1E293B; }
            QPushButton.chip_btn { background-color: #172030; border: 1px solid #2B394E; border-radius: 6px; padding: 10px; color: #94A3B8; font-weight: bold; text-align: left; }
            QPushButton.chip_btn:hover { background-color: #26334D; color: #38BDF8; border-color: #38BDF8; }
            QLineEdit { background-color: #172030; border: 1px solid #2B394E; border-radius: 8px; padding: 14px; font-size: 14px; color: #FFF; }
            QLineEdit:focus { border: 1px solid #6366F1; }
            QPushButton#exec_btn { background: linear-gradient(90deg, #6366F1, #8B5CF6); border: none; border-radius: 8px; padding: 14px 24px; font-weight: bold; color: white; font-size: 14px; }
            QPushButton#exec_btn:hover { background-color: #4F46E5; }
            QScrollArea { border: 1px solid #1E293B; border-radius: 10px; background-color: #0C1017; }
            QProgressBar { border: 1px solid #1E293B; border-radius: 4px; text-align: center; font-size: 10px; font-weight: bold; height: 14px; background-color: #172030; color: #FFF; }
            QProgressBar::chunk { background-color: #6366F1; border-radius: 3px; }
        """)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        side_layout = QVBoxLayout()
        side_layout.setContentsMargins(15, 20, 15, 20)

        logo = QLabel("🤖 APEX AI STUDIO")
        logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #818CF8; letter-spacing: 1px;")
        side_layout.addWidget(logo)

        sub_logo = QLabel("Neural Processing Engine")
        sub_logo.setStyleSheet("font-size: 11px; color: #64748B; margin-bottom: 15px;")
        side_layout.addWidget(sub_logo)

        # Hardware Gauges
        telemetry_box = QFrame()
        telemetry_box.setStyleSheet("background-color: #131A26; border: 1px solid #1E293B; border-radius: 8px; padding: 10px;")
        tb_layout = QVBoxLayout()
        
        self.cpu_label = QLabel("CPU Load: 0%")
        self.cpu_label.setStyleSheet("font-size: 11px; color: #94A3B8;")
        tb_layout.addWidget(self.cpu_label)
        self.cpu_bar = QProgressBar()
        tb_layout.addWidget(self.cpu_bar)

        self.ram_label = QLabel("RAM Usage: 0%")
        self.ram_label.setStyleSheet("font-size: 11px; color: #94A3B8; margin-top: 6px;")
        tb_layout.addWidget(self.ram_label)
        self.ram_bar = QProgressBar()
        tb_layout.addWidget(self.ram_bar)

        telemetry_box.setLayout(tb_layout)
        side_layout.addWidget(telemetry_box)

        tools_heading = QLabel("AI QUICK SUITE")
        tools_heading.setStyleSheet("font-size: 10px; font-weight: bold; color: #475569; margin-top: 15px; margin-bottom: 6px;")
        side_layout.addWidget(tools_heading)

        ai_chips = [
            ("🌐 AI Web Researcher", "summarize https://news.ycombinator.com"),
            ("💻 Write Python Script", "write a python script to download YouTube videos"),
            ("🎨 Cyberpunk Art Studio", "generate a futuristic cybernetic city skyline, cyberpunk style"),
            ("📝 Analyze Document", "Drop a document file into chat"),
            ("🌐 Open YouTube Tab", "open youtube")
        ]

        for label, cmd in ai_chips:
            btn = QPushButton(label)
            btn.setProperty("class", "chip_btn")
            btn.clicked.connect(lambda _, c=cmd: self.trigger_quick_command(c))
            side_layout.addWidget(btn)

        side_layout.addStretch()
        sidebar.setLayout(side_layout)
        main_layout.addWidget(sidebar)

        # Workspace
        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)

        self.status_label = QLabel("⚡ Neural AI Engine Online | Gemini 1.5 Flash")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #34D399; margin-bottom: 8px;")
        content_layout.addWidget(self.status_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_container.setLayout(self.chat_layout)
        self.scroll_area.setWidget(self.chat_container)
        content_layout.addWidget(self.scroll_area)

        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 10, 0, 0)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask AI to research URLs, write code, or create FLUX art...")
        self.input_field.returnPressed.connect(self.send_command)
        input_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("Generate")
        self.send_btn.setObjectName("exec_btn")
        self.send_btn.clicked.connect(self.send_command)
        input_layout.addWidget(self.send_btn)

        content_layout.addLayout(input_layout)
        content.setLayout(content_layout)
        main_layout.addWidget(content)

        self.setLayout(main_layout)

        # Timer Refresh
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_telemetry)
        self.timer.start(2000)

    def update_telemetry(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        self.cpu_bar.setValue(int(cpu))
        self.ram_bar.setValue(int(ram))
        self.cpu_label.setText(f"CPU Load: {cpu}%")
        self.ram_label.setText(f"RAM Usage: {ram}%")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path:
                self.input_field.setText(f"Analyze content from this file path: '{file_path}'")
                self.status_label.setText(f"📁 Dropped File Loaded: {os.path.basename(file_path)}")

    def trigger_quick_command(self, cmd_text):
        self.input_field.setText(cmd_text)
        self.send_command()

    def send_command(self):
        text = self.input_field.text().strip()
        if not text: return

        self.add_message(f"**User:** {text}", color="#818CF8")
        self.input_field.clear()
        self.status_label.setText("⚙️ AI Synthesizing Output...")

        self.worker = AgentWorker(text)
        self.worker.finished.connect(self.handle_response)
        self.worker.start()

    def add_message(self, text, color="#FFFFFF"):
        lbl = QLabel(text)
        lbl.setTextFormat(Qt.MarkdownText)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl.setStyleSheet(f"background-color: #172030; border-radius: 8px; padding: 12px; margin: 4px; color: {color}; font-size: 14px; line-height: 1.4;")
        self.chat_layout.addWidget(lbl)
        self.scroll_to_bottom()

    def handle_response(self, response):
        if isinstance(response, dict) and response.get("type") == "image":
            self.render_image_message(response)
        else:
            self.add_message(f"**APEX AI:**\n{str(response)}", color="#34D399")
        self.status_label.setText("⚡ Neural AI Engine Online")

    def render_image_message(self, payload):
        card = QFrame()
        card.setStyleSheet("background-color: #172030; border: 1px solid #2B394E; border-radius: 10px; padding: 14px; margin: 6px;")
        card_layout = QVBoxLayout()

        img_bytes = payload["image_bytes"]
        q_img = QImage()
        q_img.loadFromData(img_bytes)
        pixmap = QPixmap.fromImage(q_img)

        img_label = QLabel()
        img_label.setPixmap(pixmap.scaledToWidth(520, Qt.SmoothTransformation))
        img_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(img_label)

        info_lbl = QLabel(f"**Prompt:** {payload['raw_prompt']}")
        info_lbl.setTextFormat(Qt.MarkdownText)
        info_lbl.setWordWrap(True)
        info_lbl.setStyleSheet("color: #94A3B8; font-size: 13px; margin-top: 8px;")
        card_layout.addWidget(info_lbl)

        save_btn = QPushButton("💾 Save Artwork")
        save_btn.setStyleSheet("background: #059669; color: white; font-weight: bold; padding: 10px; border-radius: 6px; border: none; margin-top: 6px;")
        save_btn.clicked.connect(lambda: self.save_image_dialog(img_bytes, payload['raw_prompt']))
        card_layout.addWidget(save_btn)

        card.setLayout(card_layout)
        self.chat_layout.addWidget(card)
        self.scroll_to_bottom()

    def save_image_dialog(self, img_bytes, prompt_name):
        default_filename = f"APEX_{prompt_name[:20].replace(' ', '_')}.jpg"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", default_filename, "JPEG Image (*.jpg);;PNG Image (*.png)")
        if file_path:
            with open(file_path, "wb") as f:
                f.write(img_bytes)
            self.status_label.setText(f"✅ Saved artwork to: {file_path}")

    def scroll_to_bottom(self):
        QApplication.processEvents()
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CommercialAgentUI()
    window.show()
    sys.exit(app.exec())