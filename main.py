# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

import sys
import os
import platform
import threading
import time

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QProgressBar, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QCheckBox, QLabel, QPushButton, QFrame

# Import cleaning modules
import TempCleaning as tc
import Temp32Cleaning as tc32
import Recycle as rc
import Browser as bs

os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

class ScanWorker(QThread):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    def __init__(self, selected_tasks):
        super().__init__()
        self.selected_tasks = selected_tasks

    def run(self):
        total_tasks = len(self.selected_tasks)
        if total_tasks == 0:
            self.log.emit("⚠️ No tasks selected.")
            self.finished.emit()
            return

        progress_increment = 100 / total_tasks

        for i, (task_name, task_func) in enumerate(self.selected_tasks, start=1):
            self.log.emit(f"🔄 Running {task_name} cleanup...")
            task_func()
            self.progress.emit(int(i * progress_increment))
            time.sleep(0.5)

        self.log.emit("✅ Scan complete! Your PC feels lighter already 😉")
        self.progress.emit(100)
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "FullCleaner"
        description = "FullCleaner"
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # Initialize scanning variables
        self.scan_mode = ""
        self.scan_running = False
        self.worker = None

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = True
        themeFile = "themes/py_dracula_dark.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)
            
            # SET HACKS
            AppFunctions.setThemeHack(self)

        # Remove unused buttons from the sidebar
        self.remove_unused_menu_buttons()

        # Set up home page layout
        self.setup_home_page()

        # Create scanning interface
        self.setup_scanning_interface()

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////
        widgets.btn_home.clicked.connect(self.buttonClick)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))

    def remove_unused_menu_buttons(self):
        # Hide or remove the unused buttons
        if hasattr(widgets, "btn_widgets"):
            widgets.btn_widgets.hide()
        
        if hasattr(widgets, "btn_new"):
            widgets.btn_new.hide()
            
        if hasattr(widgets, "btn_save"):
            widgets.btn_save.hide()
            
        if hasattr(widgets, "btn_exit"):
            widgets.btn_exit.hide()

    def setup_home_page(self):
        # Create a main layout for the home page
        home_layout = QVBoxLayout()
        home_layout.setContentsMargins(10, 10, 10, 10)
        home_layout.setSpacing(0)
        
        # Set the layout to the home page
        widgets.home.setLayout(home_layout)

    def setup_scanning_interface(self):
        # Create main scanning widget
        scan_widget = QWidget()
        scan_widget.setObjectName("scanWidget")
        scan_widget.setStyleSheet("""
            #scanWidget { 
                background-color: #1b1e23; 
                border-radius: 8px; 
                border: 2px solid #2c313c;
            }
        """)
        
        layout = QVBoxLayout(scan_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header label
        header_label = QLabel("Select Cleaning Options")
        header_label.setStyleSheet("font-size: 18px; color: white; font-weight: bold; background-color: transparent;")
        layout.addWidget(header_label)

        # Scan type buttons
        scan_type_frame = QFrame()
        scan_type_frame.setStyleSheet("background-color: #1b1e23; border: none;")
        scan_type_layout = QHBoxLayout(scan_type_frame)
        scan_type_layout.setContentsMargins(0, 10, 0, 10)
        
        self.full_scan_btn = QPushButton("Full Scan")
        self.full_scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c313c;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #3c4454;
            }
            QPushButton:pressed {
                background-color: #05B8CC;
            }
        """)
        
        self.custom_scan_btn = QPushButton("Custom Scan")
        self.custom_scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c313c;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #3c4454;
            }
            QPushButton:pressed {
                background-color: #05B8CC;
            }
        """)
        
        self.full_scan_btn.setMinimumHeight(40)
        self.custom_scan_btn.setMinimumHeight(40)
        
        self.full_scan_btn.clicked.connect(lambda: self.select_scan_mode("full"))
        self.custom_scan_btn.clicked.connect(lambda: self.select_scan_mode("custom"))
        
        scan_type_layout.addWidget(self.full_scan_btn)
        scan_type_layout.addWidget(self.custom_scan_btn)
        
        layout.addWidget(scan_type_frame)

        # Override style to remove background image
        self.styleSheet = """
        /* Hide dracula image in the main widgets */
        #scanWidget, QFrame, QWidget {
            background-image: none;
        }
        """
        self.setStyleSheet(self.styleSheet)

        # Checkboxes for cleaning options
        self.cleaning_options = [
            ("Recycle Bin", rc.RecycleBin),
            ("Temp", tc.TempCleaning),
            ("Temp32", tc32.Temp32Cleaning),
            ("Edge", bs.edgeCleanup),
            ("Firefox", bs.firefoxCleanup),
            ("Chrome", bs.chromeCleanup),
            ("Brave", bs.braveCleanup),
            ("Opera", bs.operaCleanup),
        ]

        checkbox_frame = QFrame()
        checkbox_frame.setStyleSheet("background-color: #2c313c; border-radius: 8px; padding: 10px; border: none;")
        checkbox_layout = QHBoxLayout(checkbox_frame)
        checkbox_layout.setContentsMargins(10, 10, 10, 10)
        checkbox_layout.setSpacing(15)
        
        self.checkboxes = []
        for name, _ in self.cleaning_options:
            checkbox = QCheckBox(name)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: white;
                    spacing: 5px;
                    background-color: transparent;
                }
                QCheckBox::indicator {
                    width: 15px;
                    height: 15px;
                }
                QCheckBox::indicator:unchecked {
                    background-color: #1b1e23;
                    border: 1px solid #05B8CC;
                    border-radius: 3px;
                }
                QCheckBox::indicator:checked {
                    background-color: #05B8CC;
                    border: 1px solid #05B8CC;
                    border-radius: 3px;
                }
            """)
            checkbox.setChecked(True)
            self.checkboxes.append(checkbox)
            checkbox_layout.addWidget(checkbox)
        
        layout.addWidget(checkbox_frame)

        # Progress section
        progress_label = QLabel("Progress")
        progress_label.setStyleSheet("color: white; font-size: 14px; background-color: transparent;")
        layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2c313c;
                border-radius: 5px;
                text-align: center;
                background-color: #1b1e23;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #05B8CC;
                border-radius: 4px;
            }
        """)
        self.progress_bar.setMinimumHeight(25)
        layout.addWidget(self.progress_bar)

        # Console output
        console_label = QLabel("Status")
        console_label.setStyleSheet("color: white; font-size: 14px; background-color: transparent;")
        layout.addWidget(console_label)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(150)
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #2c313c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QScrollBar:vertical {
                border: none;
                background: #2c313c;
                width: 8px;
                margin: 8px 0 8px 0;
            }
            QScrollBar::handle:vertical {
                background: #05B8CC;
                min-height: 20px;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.console)

        # Start scan button
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.setMinimumHeight(50)
        self.scan_button.setStyleSheet("""
            QPushButton {
                background-color: #05B8CC;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #04a6b8;
            }
            QPushButton:pressed {
                background-color: #038a98;
            }
            QPushButton:disabled {
                background-color: #2c313c;
                color: #6c7587;
            }
        """)
        self.scan_button.clicked.connect(self.start_scan)
        layout.addWidget(self.scan_button)

        # Add the scanning interface to the home page
        widgets.home.layout().addWidget(scan_widget)

    def select_scan_mode(self, mode):
        self.scan_mode = mode
        if mode == "full":
            self.full_scan_btn.setStyleSheet("""
                QPushButton {
                    background-color: #05B8CC;
                    color: white;
                    border-radius: 8px;
                    font-weight: bold;
                    padding: 10px;
                }
            """)
            self.custom_scan_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c313c;
                    color: white;
                    border-radius: 8px;
                    font-weight: bold;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #3c4454;
                }
                QPushButton:pressed {
                    background-color: #05B8CC;
                }
            """)
            for checkbox in self.checkboxes:
                checkbox.setChecked(True)
                checkbox.setEnabled(False)
        else:
            self.custom_scan_btn.setStyleSheet("""
                QPushButton {
                    background-color: #05B8CC;
                    color: white;
                    border-radius: 8px;
                    font-weight: bold;
                    padding: 10px;
                }
            """)
            self.full_scan_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c313c;
                    color: white;
                    border-radius: 8px;
                    font-weight: bold;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #3c4454;
                }
                QPushButton:pressed {
                    background-color: #05B8CC;
                }
            """)
            for checkbox in self.checkboxes:
                checkbox.setEnabled(True)

    def log_message(self, message):
        self.console.append(message)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def scan_finished(self):
        self.scan_running = False
        self.scan_button.setText("Start Scan")
        self.scan_button.setEnabled(True)

    def start_scan(self):
        if self.scan_mode == "":
            self.log_message("⚠️ Please select a scan mode first!")
            return

        if not self.scan_running:
            self.scan_running = True
            self.scan_button.setText("Running Scan")
            self.scan_button.setEnabled(False)
            self.progress_bar.setValue(0)
            self.console.clear()

            selected_tasks = []
            for checkbox, (name, func) in zip(self.checkboxes, self.cleaning_options):
                if checkbox.isChecked():
                    selected_tasks.append((name, func))

            self.worker = ScanWorker(selected_tasks)
            self.worker.progress.connect(self.update_progress)
            self.worker.log.connect(self.log_message)
            self.worker.finished.connect(self.scan_finished)
            self.worker.start()

    def buttonClick(self):
        btn = self.sender()
        btnName = btn.objectName()

        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec_())
