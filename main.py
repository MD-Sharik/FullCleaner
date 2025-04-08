import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QStackedWidget, QHBoxLayout, QCheckBox, QTextEdit, QMessageBox
)
import io
import contextlib

# Real cleaning modules
import Browser as bs
import TempCleaning as tc
import Temp32Cleaning as tc32
import Recycle as rc

class MainScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        layout = QVBoxLayout()

        title = QLabel("🧹 PyCleaner")
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("Clean your PC with one click!")
        layout.addWidget(subtitle)

        full_btn = QPushButton("Full Scan")
        full_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(full_btn)

        custom_btn = QPushButton("Custom Scan")
        custom_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        layout.addWidget(custom_btn)

        self.setLayout(layout)

class ScanScreen(QWidget):
    def __init__(self, full_scan=False):
        super().__init__()
        self.full_scan = full_scan
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout()

        title = QLabel("🧹 PyCleaner - Full Scan" if self.full_scan else "🧹 PyCleaner - Custom Scan")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        self.checks = {
            "Temp": QCheckBox("Clean Temp Folder"),
            "Temp32": QCheckBox("Clean Temp (System32)"),
            "Recycle": QCheckBox("Empty Recycle Bin"),
            "Chrome": QCheckBox("Clean Chrome Cache"),
            "Edge": QCheckBox("Clean Edge Cache"),
            "Firefox": QCheckBox("Clean Firefox Cache"),
            "Brave": QCheckBox("Clean Brave Cache"),
            "Opera": QCheckBox("Clean Opera Cache")
        }

        for cb in self.checks.values():
            if self.full_scan:
                cb.setChecked(True)
            layout.addWidget(cb)

        self.runBtn = QPushButton("Run Cleaner")
        self.runBtn.clicked.connect(self.runCleaner)
        layout.addWidget(self.runBtn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc; font-family: Consolas;")
        layout.addWidget(self.output)

        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(self.goBack)
        layout.addWidget(back_btn)

        self.setLayout(layout)

    def runCleaner(self):
        self.output.clear()

        log_stream = io.StringIO()
        with contextlib.redirect_stdout(log_stream):
            if self.checks["Temp"].isChecked():
                tc.TempCleaning()
            if self.checks["Temp32"].isChecked():
                tc32.Temp32Cleaning()
            if self.checks["Recycle"].isChecked():
                rc.RecycleBin()
            if self.checks["Chrome"].isChecked():
                bs.chromeCleanup()
            if self.checks["Edge"].isChecked():
                bs.edgeCleanup()
            if self.checks["Firefox"].isChecked():
                bs.firefoxCleanup()
            if self.checks["Brave"].isChecked():
                bs.braveCleanup()
            if self.checks["Opera"].isChecked():
                bs.operaCleanup()

        log_output = log_stream.getvalue()
        self.output.setPlainText(log_output)
        QMessageBox.information(self, "Cleaning Complete", "Selected cleanups are done!")

    def goBack(self):
        self.parent().setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    stacked_widget = QStackedWidget()
    main_screen = MainScreen(stacked_widget)
    full_scan_screen = ScanScreen(full_scan=True)
    custom_scan_screen = ScanScreen(full_scan=False)

    stacked_widget.addWidget(main_screen)
    stacked_widget.addWidget(full_scan_screen)
    stacked_widget.addWidget(custom_scan_screen)

    stacked_widget.setFixedSize(520, 650)
    stacked_widget.show()

    sys.exit(app.exec_())