import sys
import os
import platform
import threading
import time
import json
import requests
import psutil
from modules import *
from widgets import *
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QProgressBar, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QCheckBox, QLabel, QPushButton, QFrame, QDialog, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem, QHeaderView, QFileDialog

import TempCleaning as tc
import Temp32Cleaning as tc32
import Recycle as rc
import Browser as bs

import startup_manager
import registery_cleaner
import ram_booster
import enhanced_cleaner
from antivirus import AntiVirus

os.environ["QT_FONT_DPI"] = "96"
widgets = None

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QDialog {
                background-color: #131621;
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
                border: 1px solid #2635a5;
            }
            QPushButton {
                background-color: #2635a5;
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
                "https://full-cleaner-backend.vercel.app/login",
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
                "https://full-cleaner-backend.vercel.app/havekey",
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
                background-color: #131621;
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
                border: 1px solid #2635a5;
            }
            QPushButton {
                background-color: #2635a5;
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
                "https://full-cleaner-backend.vercel.app/generate",
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
        
        # Get the base path for resources when running as executable
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = sys._MEIPASS
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        themeFile = os.path.join(base_path, "themes", "py_dracula_dark.qss")
        
        # Check if theme file exists
        if not os.path.isfile(themeFile):
            print(f"Theme file not found: {themeFile}")
            # Fallback to a basic style if theme file is not found
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #1b1e23;
                    color: white;
                }
                QPushButton {
                    background-color: #2c313c;
                    color: white;
                    border-radius: 5px;
                    padding: 5px 10px;
                }
            """)
            useCustomTheme = False

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)
            
            # SET HACKS
            AppFunctions.setThemeHack(self)

        # Remove unused buttons from the sidebar
        self.remove_unused_menu_buttons()
        
        # Add optimization buttons to sidebar
        self.add_optimization_buttons()

        # Set up home page layout
        self.setup_home_page()

        # Create scanning interface
        self.setup_scanning_interface()
        
        # Create optimization feature pages
        self.setup_startup_page()
        self.setup_registry_page()
        self.setup_ram_page()

        # Setup license information in footer
        self.setup_license_display()
        
        # Setup login status and buttons
        self.setup_login_display()

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_startup.clicked.connect(self.buttonClick)
        widgets.btn_registry.clicked.connect(self.buttonClick)
        widgets.btn_ram.clicked.connect(self.buttonClick)

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
            
        self.antivirus = AntiVirus()
        
        # CONNECT ANTIVIRUS SIGNALS
        self.ui.btn_antivirus.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.antivirusPage))
        self.ui.btn_browse.clicked.connect(self.browse_folder)
        self.ui.btn_start_scan.clicked.connect(self.toggle_scan)
        
        # Connect scan type combo box change event
        self.ui.scan_type_combo.currentTextChanged.connect(self.on_scan_type_changed)
        
        # Initially hide scan path components since Quick Scan is default
        self.ui.scan_path.hide()
        self.ui.btn_browse.hide()
            
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
        
        # Get the title bar's right buttons area
        if hasattr(widgets, "rightButtons"):
            # Insert the logout button before the settings button
            widgets.rightButtons.layout().insertWidget(0, self.logout_btn)
        
        # Update login status display
        self.update_login_display()
    
    def update_login_display(self):
        """Update the login status display"""
        if self.session_active:
            # Get username from file or registry
            username = self.get_username()
            self.login_label.setText(f"Logged in as: {username}")
            self.login_label.setStyleSheet("color: #2635a5; font-weight: bold;")
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
        """Log out the user by clearing all session and license data"""
        try:
            # Clear session file (contains ID and EMAIL)
            if os.path.exists("session.json"):
                os.remove("session.json")
            
            # Clear license file (contains KEY)
            if os.path.exists("license.json"):
                os.remove("license.json")
                # Reset license status
                self.license_status = False
                self.update_license_display()
                
            self.session_active = False
            self.update_login_display()
            
            QMessageBox.information(self, "Logged Out", "You have been logged out successfully. All user data has been removed from the system.")
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
            self.license_label.setStyleSheet("color: #2635a5; font-weight: bold;")
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
                background-color: #131621; 
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
        scan_type_frame.setStyleSheet("background-color: #131621; border: none;")
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
                background-color: #2635a5;
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
                background-color: #2635a5;
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
                    background-color: #131621;
                    border: 1px solid #2635a5;
                    border-radius: 3px;
                }
                QCheckBox::indicator:checked {
                    background-color: #576EFC;
                    border: 1px solid #576EFC;
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
                background-color: #131621;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #2635a5;
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
                background: #2635a5;
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
                background-color: #586DFB;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2635a5;
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
                    background-color: #2635a5;
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
                    background-color: #2635a5;
                }
            """)
            for checkbox in self.checkboxes:
                checkbox.setChecked(True)
                checkbox.setEnabled(False)
        else:
            self.custom_scan_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2635a5;
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
                    background-color: #2635a5;
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
        elif btnName == "btn_startup":
            widgets.stackedWidget.setCurrentWidget(widgets.startup_page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
        elif btnName == "btn_registry":
            widgets.stackedWidget.setCurrentWidget(widgets.registry_page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
        elif btnName == "btn_ram":
            widgets.stackedWidget.setCurrentWidget(widgets.ram_page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def add_optimization_buttons(self):
        """Add optimization features buttons to the sidebar menu"""
        # Create and set up startup items manager button
        self.ui.btn_startup = QPushButton("Startup Manager", self.ui.topMenu)
        self.ui.btn_startup.setObjectName(u"btn_startup")
        self.ui.btn_startup.setMinimumSize(QSize(0, 45))
        self.ui.btn_startup.setCursor(Qt.PointingHandCursor)
        self.ui.btn_startup.setStyleSheet("""
            QPushButton {
                background-image: url(:/icons/images/icons/cil-speedometer.png);
                border-left: 22px solid transparent;
                background-position: left center;
                background-repeat: no-repeat;
                text-align: left;
                padding-left: 44px;
            }
        """)
        
        # Create and set up registry cleaner button
        self.ui.btn_registry = QPushButton("Registry Cleaner", self.ui.topMenu)
        self.ui.btn_registry.setObjectName(u"btn_registry")
        self.ui.btn_registry.setMinimumSize(QSize(0, 45))
        self.ui.btn_registry.setCursor(Qt.PointingHandCursor)
        self.ui.btn_registry.setStyleSheet("""
            QPushButton {
                background-image: url(:/icons/images/icons/cil-settings.png);
                border-left: 22px solid transparent;
                background-position: left center;
                background-repeat: no-repeat;
                text-align: left;
                padding-left: 44px;
            }
        """)
        
        # Create and set up RAM booster button
        self.ui.btn_ram = QPushButton("RAM Optimizer", self.ui.topMenu)
        self.ui.btn_ram.setObjectName(u"btn_ram")
        self.ui.btn_ram.setMinimumSize(QSize(0, 45))
        self.ui.btn_ram.setCursor(Qt.PointingHandCursor)
        self.ui.btn_ram.setStyleSheet("""
            QPushButton {
                background-image: url(:/icons/images/icons/cil-reload.png);
                border-left: 22px solid transparent;
                background-position: left center;
                background-repeat: no-repeat;
                text-align: left;
                padding-left: 44px;
            }
        """)
        
        # Add buttons to the top menu layout
        self.ui.verticalLayout_8.addWidget(self.ui.btn_startup)
        self.ui.verticalLayout_8.addWidget(self.ui.btn_registry)
        self.ui.verticalLayout_8.addWidget(self.ui.btn_ram)

    def setup_startup_page(self):
        """Create the Startup Manager page"""
        # Create the page
        self.ui.startup_page = QWidget()
        self.ui.startup_page.setObjectName("startup_page")
        self.ui.stackedWidget.addWidget(self.ui.startup_page)
        
        # Create layout
        layout = QVBoxLayout(self.ui.startup_page)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        header = QLabel("Startup Programs Manager")
        header.setStyleSheet("font-size: 18px; color: white; font-weight: bold;")
        layout.addWidget(header)
        
        description = QLabel("Manage programs that start automatically with Windows. Disabling unnecessary startup items can improve boot time.")
        description.setStyleSheet("color: #aaaaaa; margin-bottom: 15px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Create startup items table
        self.startup_table = QTableWidget()
        self.startup_table.setColumnCount(3)
        self.startup_table.setHorizontalHeaderLabels(["Program Name", "Command", "Status"])
        self.startup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.startup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.startup_table.setStyleSheet("""
            QTableWidget {
                background-color: #2c313c;
                color: white;
                border: none;
                gridline-color: #353b48;
            }
            QHeaderView::section {
                background-color: #1f232a;
                color: white;
                padding: 5px;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        layout.addWidget(self.startup_table)
        
        # Button container
        button_container = QHBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c313c;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #3c4454;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_startup_items)
        button_container.addWidget(refresh_btn)
        
        # Disable selected button
        disable_btn = QPushButton("Disable Selected")
        disable_btn.setStyleSheet("""
            QPushButton {
                background-color: #586DFB;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2635a5;
            }
        """)
        disable_btn.clicked.connect(self.disable_selected_startup)
        button_container.addWidget(disable_btn)
        
        layout.addLayout(button_container)
        
        # Initialize startup manager
        self.startup_manager = startup_manager.StartupManager()
        
        # Load startup items
        self.refresh_startup_items()
    
    def refresh_startup_items(self):
        """Refresh the list of startup items"""
        self.startup_table.setRowCount(0)
        
        try:
            startup_items = self.startup_manager.get_startup_apps()
            
            self.startup_table.setRowCount(len(startup_items))
            for i, item in enumerate(startup_items):
                self.startup_table.setItem(i, 0, QTableWidgetItem(item['name']))
                self.startup_table.setItem(i, 1, QTableWidgetItem(item['command']))
                
                status_item = QTableWidgetItem("Enabled")
                status_item.setForeground(Qt.green)
                self.startup_table.setItem(i, 2, status_item)
                
                # Store the registry info for later disabling
                item_widget = self.startup_table.item(i, 0)
                item_widget.setData(Qt.UserRole, item)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load startup items: {str(e)}")
    
    def disable_selected_startup(self):
        """Disable selected startup items"""
        selected_rows = self.startup_table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "Information", "Please select a startup item to disable.")
            return
        
        row = selected_rows[0].row()
        app_info = self.startup_table.item(row, 0).data(Qt.UserRole)
        
        try:
            success = self.startup_manager.disable_startup_app(app_info)
            if success:
                self.startup_table.item(row, 2).setText("Disabled")
                self.startup_table.item(row, 2).setForeground(Qt.red)
                QMessageBox.information(self, "Success", f"Startup item '{app_info['name']}' has been disabled.")
            else:
                QMessageBox.warning(self, "Error", f"Failed to disable startup item '{app_info['name']}'.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error disabling startup item: {str(e)}")

    def setup_registry_page(self):
        """Create the Registry Cleaner page"""
        # Create the page
        self.ui.registry_page = QWidget()
        self.ui.registry_page.setObjectName("registry_page")
        self.ui.stackedWidget.addWidget(self.ui.registry_page)
        
        # Create layout
        layout = QVBoxLayout(self.ui.registry_page)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        header = QLabel("Registry Cleaner")
        header.setStyleSheet("font-size: 18px; color: white; font-weight: bold;")
        layout.addWidget(header)
        
        description = QLabel("Clean the Windows Registry by removing invalid entries. This can improve system stability and performance.")
        description.setStyleSheet("color: #aaaaaa; margin-bottom: 15px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        warning = QLabel("⚠️ WARNING: Modifying the registry can potentially cause system instability. We recommend creating a system restore point before proceeding.")
        warning.setStyleSheet("color: #FFA500; margin-bottom: 15px;")
        warning.setWordWrap(True)
        layout.addWidget(warning)
        
        # Registry items list
        self.registry_list = QListWidget()
        self.registry_list.setStyleSheet("""
            QListWidget {
                background-color: #2c313c;
                color: white;
                border: none;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #353b48;
            }
            QListWidget::item:selected {
                background-color: #3c4454;
            }
        """)
        layout.addWidget(self.registry_list)
        
        # Category checkboxes
        category_frame = QFrame()
        category_frame.setStyleSheet("background-color: #2c313c; border-radius: 5px; padding: 10px;")
        category_layout = QHBoxLayout(category_frame)
        
        self.check_file_exts = QCheckBox("File Extensions")
        self.check_file_exts.setChecked(True)
        self.check_file_exts.setStyleSheet("color: white;")
        category_layout.addWidget(self.check_file_exts)
        
        self.check_shared_dlls = QCheckBox("Shared DLLs")
        self.check_shared_dlls.setChecked(True)
        self.check_shared_dlls.setStyleSheet("color: white;")
        category_layout.addWidget(self.check_shared_dlls)
        
        self.check_uninstall = QCheckBox("Uninstall Entries")
        self.check_uninstall.setChecked(True)
        self.check_uninstall.setStyleSheet("color: white;")
        category_layout.addWidget(self.check_uninstall)
        
        self.check_mui = QCheckBox("MUI Cache")
        self.check_mui.setChecked(True)
        self.check_mui.setStyleSheet("color: white;")
        category_layout.addWidget(self.check_mui)
        
        layout.addWidget(category_frame)
        
        # Button container
        button_container = QHBoxLayout()
        
        # Scan button
        scan_btn = QPushButton("Scan Registry")
        scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c313c;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #3c4454;
            }
        """)
        scan_btn.clicked.connect(self.scan_registry)
        button_container.addWidget(scan_btn)
        
        # Fix selected button
        fix_btn = QPushButton("Fix Selected Issues")
        fix_btn.setStyleSheet("""
            QPushButton {
                background-color: #586DFB;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2635a5;
            }
        """)
        fix_btn.clicked.connect(self.fix_registry_issues)
        button_container.addWidget(fix_btn)
        
        layout.addLayout(button_container)
        
        # Initialize registry cleaner
        self.registry_cleaner = registery_cleaner.RegistryCleaner()
        
        # Progress indicator label
        self.registry_status = QLabel("Ready to scan. Click 'Scan Registry' to begin.")
        self.registry_status.setStyleSheet("color: white; margin-top: 5px;")
        layout.addWidget(self.registry_status)
    
    def scan_registry(self):
        """Scan Windows registry for issues"""
        self.registry_list.clear()
        self.registry_status.setText("Scanning registry, please wait...")
        QApplication.processEvents()  # Update UI
        
        try:
            # Run the scanner in a thread to avoid freezing UI
            threading.Thread(target=self._do_registry_scan).start()
        except Exception as e:
            self.registry_status.setText(f"Error: {str(e)}")
    
    def _do_registry_scan(self):
        """Perform the actual registry scan in a separate thread"""
        try:
            # Scan registry
            issues = self.registry_cleaner.scan_for_issues()
            
            # Update UI from main thread
            def update_ui():
                self.registry_list.clear()
                if issues:
                    for issue in issues:
                        item = QListWidgetItem(issue['description'])
                        item.setData(Qt.UserRole, issue)
                        self.registry_list.addItem(item)
                    self.registry_status.setText(f"Scan complete. Found {len(issues)} issues.")
                else:
                    self.registry_status.setText("Scan complete. No issues found.")
            
            # Schedule UI update
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, update_ui)
        except Exception as e:
            def show_error():
                self.registry_status.setText(f"Error scanning registry: {str(e)}")
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, show_error)
    
    def fix_registry_issues(self):
        """Fix selected registry issues"""
        selected_items = self.registry_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Information", "Please select issues to fix.")
            return
        
        # Confirm action
        confirm = QMessageBox.question(
            self, "Confirm Fix", 
            "Are you sure you want to fix the selected registry issues? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Get selected issue indexes
            issues_to_fix = []
            for item in selected_items:
                issue = item.data(Qt.UserRole)
                idx = self.registry_cleaner.registry_issues.index(issue)
                issues_to_fix.append(idx)
            
            try:
                # Fix issues
                fixed_count = self.registry_cleaner.fix_issues(issues_to_fix)
                
                # Remove fixed items from list
                for item in selected_items:
                    row = self.registry_list.row(item)
                    self.registry_list.takeItem(row)
                
                QMessageBox.information(self, "Success", f"{fixed_count} registry issues have been fixed.")
                self.registry_status.setText(f"Fixed {fixed_count} issues.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to fix registry issues: {str(e)}")

    def setup_ram_page(self):
        """Create the RAM Optimizer page"""
        # Create the page
        self.ui.ram_page = QWidget()
        self.ui.ram_page.setObjectName("ram_page")
        self.ui.stackedWidget.addWidget(self.ui.ram_page)
        
        # Create layout
        layout = QVBoxLayout(self.ui.ram_page)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        header = QLabel("RAM Optimizer")
        header.setStyleSheet("font-size: 18px; color: white; font-weight: bold;")
        layout.addWidget(header)
        
        description = QLabel("Optimize your system memory to improve performance and reduce resource usage.")
        description.setStyleSheet("color: #aaaaaa; margin-bottom: 15px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Memory usage frame
        memory_frame = QFrame()
        memory_frame.setStyleSheet("background-color: #2c313c; border-radius: 5px; padding: 10px;")
        memory_layout = QVBoxLayout(memory_frame)
        
        mem_title = QLabel("Current Memory Usage")
        mem_title.setStyleSheet("color: white; font-weight: bold;")
        memory_layout.addWidget(mem_title)
        
        # Create memory usage display
        usage_layout = QHBoxLayout()
        
        # Memory usage progress bar
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)
        self.memory_bar.setValue(50)  # Placeholder value
        self.memory_bar.setTextVisible(True)
        self.memory_bar.setFormat("%p% used")
        self.memory_bar.setStyleSheet("""
            QProgressBar {
                background-color: #353b48;
                color: white;
                border-radius: 3px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #2635a5;
                border-radius: 3px;
            }
        """)
        usage_layout.addWidget(self.memory_bar, 3)
        
        # Memory details
        self.memory_details = QLabel("Total: 0 GB | Used: 0 GB | Free: 0 GB")
        self.memory_details.setStyleSheet("color: white;")
        usage_layout.addWidget(self.memory_details, 2)
        
        memory_layout.addLayout(usage_layout)
        layout.addWidget(memory_frame)
        
        # Optimization options
        options_frame = QFrame()
        options_frame.setStyleSheet("background-color: #2c313c; border-radius: 5px; padding: 10px;")
        options_layout = QVBoxLayout(options_frame)
        
        opt_title = QLabel("Optimization Options")
        opt_title.setStyleSheet("color: white; font-weight: bold;")
        options_layout.addWidget(opt_title)
        
        # Option checkboxes
        self.check_terminate = QCheckBox("Terminate low-priority processes")
        self.check_terminate.setChecked(True)
        self.check_terminate.setStyleSheet("color: white;")
        options_layout.addWidget(self.check_terminate)
        
        self.check_file_cache = QCheckBox("Clear system file cache")
        self.check_file_cache.setChecked(True)
        self.check_file_cache.setStyleSheet("color: white;")
        options_layout.addWidget(self.check_file_cache)
        
        self.check_standby = QCheckBox("Clear system standby list")
        self.check_standby.setChecked(True)
        self.check_standby.setStyleSheet("color: white;")
        options_layout.addWidget(self.check_standby)
        
        layout.addWidget(options_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Status")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c313c;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #3c4454;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_memory_status)
        button_layout.addWidget(refresh_btn)
        
        # Optimize button
        optimize_btn = QPushButton("Optimize RAM")
        optimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #586DFB;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2635a5;
            }
        """)
        optimize_btn.clicked.connect(self.optimize_ram)
        button_layout.addWidget(optimize_btn)
        
        layout.addLayout(button_layout)
        
        # Status label
        self.ram_status = QLabel("Ready to optimize. Click 'Refresh Status' to see current memory usage.")
        self.ram_status.setStyleSheet("color: white; margin-top: 5px;")
        layout.addWidget(self.ram_status)
        
        # Initialize RAM optimizer
        self.ram_booster = ram_booster.RamBooster()
        
        # Refresh memory status initially
        self.refresh_memory_status()
    
    def refresh_memory_status(self):
        """Refresh memory usage statistics"""
        try:
            # Get memory info from psutil
            memory = psutil.virtual_memory()
            
            # Update progress bar
            self.memory_bar.setValue(memory.percent)
            
            # Update memory details
            total_gb = round(memory.total / (1024 ** 3), 2)
            used_gb = round(memory.used / (1024 ** 3), 2)
            free_gb = round(memory.available / (1024 ** 3), 2)
            
            self.memory_details.setText(f"Total: {total_gb} GB | Used: {used_gb} GB | Free: {free_gb} GB")
            self.ram_status.setText("Memory status updated.")
            
            # Set progress bar color based on usage
            if memory.percent > 80:
                self.memory_bar.setStyleSheet("""
                    QProgressBar {
                        background-color: #353b48;
                        color: white;
                        border-radius: 3px;
                        text-align: center;
                    }
                    QProgressBar::chunk {
                        background-color: #e74c3c;
                        border-radius: 3px;
                    }
                """)
            elif memory.percent > 60:
                self.memory_bar.setStyleSheet("""
                    QProgressBar {
                        background-color: #353b48;
                        color: white;
                        border-radius: 3px;
                        text-align: center;
                    }
                    QProgressBar::chunk {
                        background-color: #f39c12;
                        border-radius: 3px;
                    }
                """)
            else:
                self.memory_bar.setStyleSheet("""
                    QProgressBar {
                        background-color: #353b48;
                        color: white;
                        border-radius: 3px;
                        text-align: center;
                    }
                    QProgressBar::chunk {
                        background-color: #2635a5;
                        border-radius: 3px;
                    }
                """)
        except Exception as e:
            self.ram_status.setText(f"Error refreshing memory status: {str(e)}")
    
    def optimize_ram(self):
        """Optimize RAM based on selected options"""
        self.ram_status.setText("Optimizing RAM, please wait...")
        QApplication.processEvents()  # Update UI
        
        # Start optimization in a thread to prevent UI freezing
        threading.Thread(target=self._do_ram_optimization).start()
    
    def _do_ram_optimization(self):
        """Perform RAM optimization in a separate thread"""
        try:
            # Get selected options
            terminate = self.check_terminate.isChecked()
            clear_cache = self.check_file_cache.isChecked()
            clear_standby = self.check_standby.isChecked()
            
            # Track optimization results
            optimized = False
            results = []
            
            # Perform selected optimizations
            if terminate:
                killed = self.ram_booster.terminate_low_priority_processes()
                if killed > 0:
                    results.append(f"Terminated {killed} low-priority processes")
                    optimized = True
            
            if clear_cache:
                if self.ram_booster.clear_system_file_cache():
                    results.append("Cleared system file cache")
                    optimized = True
            
            if clear_standby:
                if self.ram_booster.clear_standby_list():
                    results.append("Cleared system standby list")
                    optimized = True
            
            # Show results in the UI
            def update_ui():
                if optimized:
                    self.ram_status.setText("Optimization complete: " + ", ".join(results))
                    QMessageBox.information(self, "Optimization Complete", 
                                          "RAM optimization completed successfully.\n\n" + "\n".join(results))
                else:
                    self.ram_status.setText("No optimizations were performed.")
                
                # Refresh memory status to show the effects
                self.refresh_memory_status()
            
            # Update UI from main thread
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, update_ui)
            
        except Exception as e:
            def show_error():
                self.ram_status.setText(f"Error during optimization: {str(e)}")
                QMessageBox.warning(self, "Optimization Error", f"An error occurred during RAM optimization:\n{str(e)}")
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, show_error)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory to Scan")
        if folder:
            self.ui.scan_path.setText(folder)
            
    def toggle_scan(self):
        if self.ui.btn_start_scan.text() == "Start Scan":
            scan_type = self.ui.scan_type_combo.currentText()
            if scan_type == "Quick Scan":
                self.start_quick_scan()
            elif scan_type == "Full Scan":
                self.start_full_scan()
            else:  # Custom Scan
                if not self.ui.scan_path.text().strip():
                    QMessageBox.warning(self, "Warning", "Please select a folder to scan")
                    return
                self.start_custom_scan()
        else:
            self.stop_scan()
    
    def start_quick_scan(self):
        self.ui.btn_start_scan.setText("Stop Scan")
        self.ui.scan_progress.setValue(0)
        self.ui.results_table.setRowCount(0)
        self.ui.scan_path.setEnabled(False)
        self.ui.btn_browse.setEnabled(False)
        
        def update_progress(progress, current_file, files_scanned, total_files):
            self.ui.scan_progress.setValue(int(progress))
            self.ui.scan_status.setText(f"Scanning: {current_file}\nFiles scanned: {files_scanned}/{total_files}")
            
            results = self.antivirus.get_results()
            if results and len(results) > self.ui.results_table.rowCount():
                row = self.ui.results_table.rowCount()
                self.ui.results_table.insertRow(row)
                latest = results[-1]
                
                self.ui.results_table.setItem(row, 0, QTableWidgetItem(latest["filepath"]))
                self.ui.results_table.setItem(row, 1, QTableWidgetItem(latest["status"]))
                self.ui.results_table.setItem(row, 2, QTableWidgetItem(latest["message"]))
                self.ui.results_table.setItem(row, 3, QTableWidgetItem(str(latest["timestamp"])))
        
        self.scan_thread = self.antivirus.start_quick_scan(update_progress)
    
    def start_full_scan(self):
        self.ui.btn_start_scan.setText("Stop Scan")
        self.ui.scan_progress.setValue(0)
        self.ui.results_table.setRowCount(0)
        self.ui.scan_path.setEnabled(False)
        self.ui.btn_browse.setEnabled(False)
        
        def update_progress(progress, current_file, files_scanned, total_files):
            self.ui.scan_progress.setValue(int(progress))
            self.ui.scan_status.setText(f"Scanning: {current_file}\nFiles scanned: {files_scanned}/{total_files}")
            
            results = self.antivirus.get_results()
            if results and len(results) > self.ui.results_table.rowCount():
                row = self.ui.results_table.rowCount()
                self.ui.results_table.insertRow(row)
                latest = results[-1]
                
                self.ui.results_table.setItem(row, 0, QTableWidgetItem(latest["filepath"]))
                self.ui.results_table.setItem(row, 1, QTableWidgetItem(latest["status"]))
                self.ui.results_table.setItem(row, 2, QTableWidgetItem(latest["message"]))
                self.ui.results_table.setItem(row, 3, QTableWidgetItem(str(latest["timestamp"])))
        
        self.scan_thread = self.antivirus.start_full_scan(update_progress)
    
    def start_custom_scan(self):
        scan_path = self.ui.scan_path.text()
        if not scan_path:
            return
            
        self.ui.btn_start_scan.setText("Stop Scan")
        self.ui.scan_progress.setValue(0)
        self.ui.results_table.setRowCount(0)
        self.ui.scan_path.setEnabled(False)
        self.ui.btn_browse.setEnabled(False)
        
        def update_progress(progress, current_file, files_scanned, total_files):
            self.ui.scan_progress.setValue(int(progress))
            self.ui.scan_status.setText(f"Scanning: {current_file}\nFiles scanned: {files_scanned}/{total_files}")
            
            results = self.antivirus.get_results()
            if results and len(results) > self.ui.results_table.rowCount():
                row = self.ui.results_table.rowCount()
                self.ui.results_table.insertRow(row)
                latest = results[-1]
                
                self.ui.results_table.setItem(row, 0, QTableWidgetItem(latest["filepath"]))
                self.ui.results_table.setItem(row, 1, QTableWidgetItem(latest["status"]))
                self.ui.results_table.setItem(row, 2, QTableWidgetItem(latest["message"]))
                self.ui.results_table.setItem(row, 3, QTableWidgetItem(str(latest["timestamp"])))
        
        self.scan_thread = self.antivirus.start_scan(scan_path, update_progress)
            
    def stop_scan(self):
        self.antivirus.stop_scan()
        self.ui.btn_start_scan.setText("Start Scan")
        self.ui.scan_status.setText("Scan stopped")
        self.ui.scan_path.setEnabled(True)
        self.ui.btn_browse.setEnabled(True)

    def on_scan_type_changed(self, scan_type):
        """Handle scan type selection change"""
        if scan_type == "Custom Scan":
            self.ui.scan_path.show()
            self.ui.btn_browse.show()
            self.ui.scan_path.setEnabled(True)
            self.ui.btn_browse.setEnabled(True)
        else:
            self.ui.scan_path.hide()
            self.ui.btn_browse.hide()
            self.ui.scan_path.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
