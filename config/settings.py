# config/settings.py
from pydantic import BaseSettings
from typing import Optional
import os

class AppSettings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/pdf_processor"
    
    # API
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    secret_key: str = "your-secret-key-change-in-production"
    
    # File Paths
    pdf_storage_path: str = "./data/pdfs"
    excel_output_path: str = "./data/excel"
    log_file_path: str = "./logs/app.log"
    
    # Email Settings
    max_concurrent_email_checks: int = 5
    email_check_interval: int = 60  # seconds
    
    # Processing
    max_concurrent_pdf_processing: int = 3
    pdf_processing_timeout: int = 300  # seconds
    
    # Notifications
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = AppSettings()