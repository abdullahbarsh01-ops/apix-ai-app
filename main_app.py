import sys, os
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QTextBrowser, QLineEdit, QPushButton, QLabel)
from PySide6.QtCore import QThread, Signal
from agent_engine import AgentEngine

class AgentWorker(QThread):
    finished = Signal(str)

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
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Apex Desktop Autonomous Agent")
        self.resize(650, 550)
        self.setStyleSheet("""
            QWidget { background-color: #0E1117; color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
            QTextBrowser { background-color: #1A1C23; border: 1px solid #262730; border-radius: 8px; padding: 10px; font-size: 14px; }
            QLineEdit { background-color: #161B22; border: 1px solid #30363D; border-radius: 6px; padding: 10px; font-size: 14px; color: #FFF; }
            QPushButton { background: linear-gradient(90deg, #4F46E5, #7C3AED); border: none; border-radius: 6px; padding: 10px; font-weight: bold; color: white; font-size: 14px; }
            QPushButton:hover { background-color: #4338CA; }
        """)

        layout = QVBoxLayout()

        self.status_label = QLabel("🛡️ Commercial Agent Running (Native Engine)")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #818CF8;")
        layout.addWidget(self.status_label)

        self.chat_history = QTextBrowser()
        layout.addWidget(self.chat_history)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter system command or conversation...")
        self.input_field.returnPressed.connect(self.send_command)
        layout.addWidget(self.input_field)

        self.send_btn = QPushButton("Execute Command")
        self.send_btn.clicked.connect(self.send_command)
        layout.addWidget(self.send_btn)

        self.setLayout(layout)

    def send_command(self):
        text = self.input_field.text().strip()
        if not text:
            return

        self.chat_history.append(f"<span style='color: #A5B4FC;'><b>User:</b> {text}</span>")
        self.input_field.clear()
        self.status_label.setText("⚙️ Processing command via AI Engine...")

        self.worker = AgentWorker(text)
        self.worker.finished.connect(self.handle_response)
        self.worker.start()

    def handle_response(self, response):
        self.chat_history.append(f"<span style='color: #34D399;'><b>Agent:</b> {response}</span><br>")
        self.status_label.setText("🛡️ Commercial Agent Ready")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CommercialAgentUI()
    window.show()
    sys.exit(app.exec())
