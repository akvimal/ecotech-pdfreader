# ui/main_window.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_system_tray()
    
    def setup_ui(self):
        # Create tabbed interface
        self.tabs = QTabWidget()
        
        # Dashboard tab
        self.dashboard_tab = DashboardWidget()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        
        # Email Accounts tab
        self.email_tab = EmailAccountsWidget()
        self.tabs.addTab(self.email_tab, "Email Accounts")
        
        # PDF Mapping tab
        self.mapping_tab = PDFMappingWidget()
        self.tabs.addTab(self.mapping_tab, "PDF Mapping")
        
        # Processing History tab
        self.history_tab = ProcessingHistoryWidget()
        self.tabs.addTab(self.history_tab, "Processing History")
        
        # Settings tab
        self.settings_tab = SettingsWidget()
        self.tabs.addTab(self.settings_tab, "Settings")
        
        self.setCentralWidget(self.tabs)

# ui/pdf_mapping_designer.py
class PDFMappingDesigner(QDialog):
    """Visual designer for creating PDF-to-Excel mapping rules"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # Left panel - PDF preview and table detection
        left_panel = QVBoxLayout()
        
        # PDF viewer
        self.pdf_viewer = QPdfViewer()  # Custom PDF viewer widget
        left_panel.addWidget(QLabel("PDF Preview:"))
        left_panel.addWidget(self.pdf_viewer)
        
        # Table detection controls
        self.table_detection_controls = QGroupBox("Table Detection")
        detection_layout = QVBoxLayout()
        
        self.auto_detect_btn = QPushButton("Auto-Detect Tables")
        self.manual_select_btn = QPushButton("Manual Selection")
        detection_layout.addWidget(self.auto_detect_btn)
        detection_layout.addWidget(self.manual_select_btn)
        
        self.table_detection_controls.setLayout(detection_layout)
        left_panel.addWidget(self.table_detection_controls)
        
        # Right panel - Mapping configuration
        right_panel = QVBoxLayout()
        
        # Excel template designer
        self.excel_template = ExcelTemplateDesigner()
        right_panel.addWidget(QLabel("Excel Output Template:"))
        right_panel.addWidget(self.excel_template)
        
        # Transformation rules
        self.transformation_rules = TransformationRulesEditor()
        right_panel.addWidget(QLabel("Data Transformation Rules:"))
        right_panel.addWidget(self.transformation_rules)
        
        layout.addLayout(left_panel, 60)  # 60% width
        layout.addLayout(right_panel, 40)  # 40% width
        
        self.setLayout(layout)