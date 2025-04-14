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
import json
import requests

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QProgressBar, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QCheckBox, QLabel, QPushButton, QFrame, QDialog, QLineEdit, QMessageBox

# Import cleaning modules
import TempCleaning as tc
import Temp32Cleaning as tc32
import Recycle as rc
import Browser as bs

os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QDialog {
                background-color: #1b1e23;
                border: 2px solid #2c313c;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #2c313c;
                color: white;
                border-radius: 5px;
                padding: 8px;
                border: 1px solid #05B8CC;
            }
            QPushButton {
                background-color: #05B8CC;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #04a6b8;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Email input
        email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        
        # Password input
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.attempt_login)
        
        # Add widgets to layout
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
        
    def attempt_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password")
            return
        
        try:
            # Connect to authentication endpoint
            response = requests.post(
                "http://localhost:3000/login",
                json={"email": email, "password": password},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Save session data
                session_data = {
                    "userId": data.get("userId", ""),
                    "email": data.get("email", ""),
                    "logged_in": True,
                    "login_time": time.time()
                }
                
                # Save to file
                with open("session.json", "w") as f:
                    json.dump(session_data, f)
                
                # Check if user has a license key
                self.check_for_license_key(data.get("userId", ""))
                
                QMessageBox.information(self, "Success", "Login successful!")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Invalid email or password")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")
            
    def check_for_license_key(self, user_id):
        try:
            # Check if user already has a license key
            response = requests.post(
                "http://localhost:3000/havekey",
                json={"id": user_id},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if "key" in data and data["key"]:
                    # User has a license key, save it
                    with open("license.json", "w") as f:
                        json.dump({"key": data["key"], "valid": True}, f)
        except Exception as e:
            print(f"Error checking license key: {str(e)}")

class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("License Activation")
        self.setFixedSize(400, 180)
        self.parent = parent
        self.setStyleSheet("""
            QDialog {
                background-color: #1b1e23;
                border: 2px solid #2c313c;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #2c313c;
                color: white;
                border-radius: 5px;
                padding: 8px;
                border: 1px solid #05B8CC;
            }
            QPushButton {
                background-color: #05B8CC;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #04a6b8;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Option 1: Generate new key
        self.generate_btn = QPushButton("Generate New License Key")
        self.generate_btn.clicked.connect(self.generate_license)
        
        # Option 2: Enter existing key
        key_label = QLabel("Or Enter Existing License Key:")
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter your license key")
        
        self.activate_btn = QPushButton("Activate License")
        self.activate_btn.clicked.connect(self.activate_license)
        
        # Add widgets to layout
        layout.addWidget(self.generate_btn)
        layout.addWidget(key_label)
        layout.addWidget(self.key_input)
        layout.addWidget(self.activate_btn)
        
    def generate_license(self):
        """Generate a new license key for this user"""
        try:
            # Get current user info
            if not os.path.exists("session.json"):
                QMessageBox.warning(self, "Error", "You need to be logged in to generate a license key")
                return
                
            with open("session.json", "r") as f:
                session_data = json.load(f)
                
            user_id = session_data.get("userId", "")
            email = session_data.get("email", "")
            
            if not user_id or not email:
                QMessageBox.warning(self, "Error", "Invalid session data. Please log in again.")
                return
                
            # Request license key generation
            response = requests.post(
                "http://localhost:3000/generate",
                json={"id": user_id, "email": email},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                license_key = data.get("key", "")
                
                if license_key:
                    # Save license data
                    with open("license.json", "w") as f:
                        json.dump({"key": license_key, "valid": True}, f)
                    
                    QMessageBox.information(self, "Success", f"Your license key has been generated:\n\n{license_key}\n\nPlease save this key for future reference.")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Could not generate license key")
            else:
                QMessageBox.warning(self, "Error", f"License generation failed: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")
        
    def activate_license(self):
        """Activate with an existing license key"""
        key = self.key_input.text().strip()
        
        if not key:
            QMessageBox.warning(self, "Error", "Please enter a license key")
            return
        
        try:
            # Save license data
            with open("license.json", "w") as f:
                json.dump({"key": key, "valid": True}, f)
            
            QMessageBox.information(self, "Success", "License activated successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving license: {str(e)}")

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

        # Check license status
        self.license_status = self.check_license()
        
        # Check login session status
        self.session_active = self.check_session()

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

        # Setup license information in footer
        self.setup_license_display()
        
        # Setup login status and buttons
        self.setup_login_display()

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
        
        # Check if logged in, if not show login dialog
        if not self.session_active:
            self.open_login_dialog()
            
    def check_license(self):
        """Check if license exists and is valid"""
        try:
            if os.path.exists("license.json"):
                with open("license.json", "r") as f:
                    license_data = json.load(f)
                    return license_data.get("valid", False)
            return False
        except:
            return False
            
    def check_session(self):
        """Check if session exists and is valid"""
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    session_data = json.load(f)
                    # Check if session is not too old (24 hours max)
                    login_time = session_data.get("login_time", 0)
                    current_time = time.time()
                    if current_time - login_time < 86400:  # 24 hours in seconds
                        return session_data.get("logged_in", False)
            return False
        except:
            return False
    
    def setup_login_display(self):
        """Setup login information and buttons in the UI"""
        # Add logout button to top right
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c313c;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F44336;
            }
        """)
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.clicked.connect(self.logout)
        
        # Get the top bar layout
        if hasattr(widgets, "titleRightBox"):
            # Add button to title right box
            widgets.titleRightBox.layout().insertWidget(0, self.logout_btn)
        
        # Update login status display
        self.update_login_display()
    
    def update_login_display(self):
        """Update the login status display"""
        if self.session_active:
            # Get username from file or registry
            username = self.get_username()
            self.login_label.setText(f"Logged in as: {username}")
            self.login_label.setStyleSheet("color: #05B8CC; font-weight: bold;")
            self.logout_btn.setVisible(True)
        else:
            self.login_label.setText("Click to Login")
            self.login_label.setStyleSheet("color: #F44336; font-weight: bold;")
            self.logout_btn.setVisible(False)
        
        # Also update home page based on login status
        if hasattr(self, "scan_button"):
            self.scan_button.setEnabled(self.session_active)
        
        # Update checkboxes
        if hasattr(self, "checkboxes"):
            for checkbox in self.checkboxes:
                checkbox.setEnabled(self.session_active and self.scan_mode == "custom")
    
    def get_username(self):
        """Get current user email from session"""
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    session_data = json.load(f)
                    return session_data.get("email", "User")
        except:
            pass
        return "User"
    
    def open_login_dialog(self, event=None):
        """Open login dialog when clicked"""
        if not self.session_active:
            dialog = LoginDialog(self)
            if dialog.exec_():
                self.session_active = self.check_session()
                self.update_login_display()
    
    def logout(self):
        """Log out the user by clearing session data"""
        try:
            # Clear file
            if os.path.exists("session.json"):
                os.remove("session.json")
                
            self.session_active = False
            self.update_login_display()
            
            QMessageBox.information(self, "Logged Out", "You have been logged out successfully")
        except Exception as e:
            print(f"Logout error: {str(e)}")
            QMessageBox.warning(self, "Error", "Could not complete logout")

    def setup_license_display(self):
        """Setup license information display in footer"""
        # Create license status label
        self.license_label = QLabel()
        self.license_label.setCursor(Qt.PointingHandCursor)
        self.license_label.mousePressEvent = self.open_license_dialog
        
        # Update license status display
        self.update_license_display()
        
        # Create login status label
        self.login_label = QLabel()
        self.login_label.setCursor(Qt.PointingHandCursor)
        self.login_label.mousePressEvent = self.open_login_dialog
        
        # Find the credits label and get its parent layout
        if hasattr(widgets, "creditsLabel"):
            parent_layout = widgets.creditsLabel.parent().layout()
            if parent_layout:
                # Remove the existing credits label
                parent_layout.removeWidget(widgets.creditsLabel)
                widgets.creditsLabel.hide()
                
                # Create a horizontal layout for status labels
                status_frame = QFrame()
                status_layout = QHBoxLayout(status_frame)
                status_layout.setContentsMargins(0, 0, 0, 0)
                status_layout.setSpacing(15)
                
                # Add license and login status labels
                status_layout.addWidget(self.license_label)
                status_layout.addWidget(self.login_label)
                
                # Add to parent layout
                parent_layout.addWidget(status_frame)
    
    def update_license_display(self):
        """Update the license status display"""
        if self.license_status:
            self.license_label.setText("Licensed ✓")
            self.license_label.setStyleSheet("color: #05B8CC; font-weight: bold;")
        else:
            self.license_label.setText("Click to Activate License")
            self.license_label.setStyleSheet("color: #F44336; font-weight: bold;")
    
    def open_license_dialog(self, event=None):
        """Open license dialog when clicked"""
        if not self.license_status:
            dialog = LicenseDialog(self)
            if dialog.exec_():
                self.license_status = self.check_license()
                self.update_license_display()

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
        # Disable scan button if not logged in
        self.scan_button.setEnabled(self.session_active)
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
        # Check if user is logged in
        if not self.session_active:
            self.log_message("⚠️ Please login first to use scanning features!")
            self.open_login_dialog()
            return
            
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
