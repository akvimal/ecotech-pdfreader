#!/usr/bin/env python3
"""
PDF Processor Application
Main entry point for the desktop application
"""

import sys
import os
import asyncio
import threading
import signal
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
import uvicorn
from loguru import logger

# Add src to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config import settings
from models.database import init_database, check_database_connection
from services.api_server import create_app
from services.email_monitor import EmailMonitorService
from services.notification_service import NotificationService
from ui.main_window import MainWindow
from ui.login_dialog import LoginDialog


class BackgroundServices(QThread):
    """Background services manager"""
    service_started = pyqtSignal(str)
    service_failed = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.api_server = None
        self.email_monitor = None
        self.notification_service = None
        self.running = False
    
    def run(self):
        """Start all background services"""
        self.running = True
        
        try:
            # Start FastAPI server
            self.start_api_server()
            
            # Start email monitoring
            self.start_email_monitor()
            
            # Start notification service
            self.start_notification_service()
            
            self.service_started.emit("All services started successfully")
            
            # Keep thread alive
            while self.running:
                self.msleep(1000)  # Sleep for 1 second
                
        except Exception as e:
            logger.error(f"Failed to start background services: {e}")
            self.service_failed.emit("Background Services", str(e))
    
    def start_api_server(self):
        """Start FastAPI server in background thread"""
        def run_server():
            app = create_app()
            uvicorn.run(
                app,
                host=settings.api_host,
                port=settings.api_port,
                log_level="info"
            )
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        logger.info(f"API server started on {settings.api_host}:{settings.api_port}")
    
    def start_email_monitor(self):
        """Start email monitoring service"""
        self.email_monitor = EmailMonitorService()
        self.email_monitor.start()
        logger.info("Email monitoring service started")
    
    def start_notification_service(self):
        """Start notification service"""
        self.notification_service = NotificationService()
        logger.info("Notification service started")
    
    def stop_services(self):
        """Stop all background services"""
        self.running = False
        
        if self.email_monitor:
            self.email_monitor.stop()
        
        logger.info("Background services stopped")


class PDFProcessorApp:
    """Main application class"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("PDF Processor")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("PDF Processor Inc.")
        
        # Setup logging
        self.setup_logging()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Application components
        self.main_window = None
        self.background_services = None
        self.splash_screen = None
        
    def setup_logging(self):
        """Configure application logging"""
        log_dir = Path(settings.log_dir)
        log_dir.mkdir(exist_ok=True)
        
        logger.remove()  # Remove default handler
        logger.add(
            log_dir / "app.log",
            rotation="10 MB",
            retention="30 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
        )
        logger.add(sys.stdout, level="INFO")
    
    def show_splash_screen(self):
        """Show splash screen during initialization"""
        try:
            splash_pixmap = QPixmap(str(Path("assets") / "splash_screen.png"))
            self.splash_screen = QSplashScreen(splash_pixmap)
            self.splash_screen.show()
            self.app.processEvents()
        except Exception as e:
            logger.warning(f"Could not load splash screen: {e}")
    
    def initialize_database(self):
        """Initialize database connection and schema"""
        try:
            if not check_database_connection():
                raise Exception("Cannot connect to database")
            
            init_database()
            logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            QMessageBox.critical(
                None,
                "Database Error",
                f"Failed to initialize database:\n{str(e)}\n\nPlease check your database configuration."
            )
            return False
    
    def show_login_dialog(self):
        """Show login dialog and authenticate user"""
        login_dialog = LoginDialog()
        if login_dialog.exec() == LoginDialog.DialogCode.Accepted:
            return login_dialog.get_current_user()
        return None
    
    def start_background_services(self):
        """Start background services"""
        self.background_services = BackgroundServices()
        self.background_services.service_started.connect(self.on_service_started)
        self.background_services.service_failed.connect(self.on_service_failed)
        self.background_services.start()
    
    def on_service_started(self, message):
        """Handle successful service startup"""
        logger.info(f"Service started: {message}")
        if self.splash_screen:
            self.splash_screen.showMessage(
                f"Services started: {message}",
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                Qt.GlobalColor.white
            )
    
    def on_service_failed(self, service_name, error):
        """Handle service startup failure"""
        logger.error(f"Service failed: {service_name} - {error}")
        QMessageBox.critical(
            None,
            f"{service_name} Error",
            f"Failed to start {service_name}:\n{error}"
        )
    
    def show_main_window(self, user):
        """Show main application window"""
        self.main_window = MainWindow(user)
        self.main_window.show()
        
        # Hide splash screen
        if self.splash_screen:
            self.splash_screen.finish(self.main_window)
    
    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
    
    def shutdown(self):
        """Graceful application shutdown"""
        logger.info("Shutting down application...")
        
        # Stop background services
        if self.background_services:
            self.background_services.stop_services()
            self.background_services.quit()
            self.background_services.wait(5000)  # Wait up to 5 seconds
        
        # Close main window
        if self.main_window:
            self.main_window.close()
        
        # Quit application
        self.app.quit()
    
    def run(self):
        """Main application execution flow"""
        try:
            # Show splash screen
            self.show_splash_screen()
            
            # Initialize database
            if not self.initialize_database():
                return 1
            
            # Authenticate user
            user = self.show_login_dialog()
            if not user:
                logger.info("User cancelled login")
                return 0
            
            # Start background services
            self.start_background_services()
            
            # Show main window
            self.show_main_window(user)
            
            # Run application
            return self.app.exec()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            QMessageBox.critical(
                None,
                "Application Error",
                f"An unexpected error occurred:\n{str(e)}"
            )
            return 1
        
        finally:
            self.shutdown()


def main():
    """Application entry point"""
    try:
        app = PDFProcessorApp()
        exit_code = app.run()
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()