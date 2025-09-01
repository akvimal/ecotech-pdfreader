"""
Configuration management for PDF Processor Application
"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Info
    app_name: str = "PDF Processor"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database Configuration
    database_url: str = "postgresql://postgres:password@localhost:5432/pdf_processor"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    
    # API Configuration
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_workers: int = 1
    secret_key: str = "your-secret-key-change-in-production-environment"
    
    # File System Paths
    base_dir: Path = Path.cwd()
    data_dir: Path = base_dir / "data"
    pdf_storage_path: Path = data_dir / "pdfs"
    excel_output_path: Path = data_dir / "excel"
    temp_dir: Path = data_dir / "temp"
    log_dir: Path = base_dir / "logs"
    config_dir: Path = base_dir / "config"
    
    # Email Processing
    max_concurrent_email_checks: int = 5
    email_check_interval: int = 60  # seconds
    email_timeout: int = 30  # seconds
    max_email_size: int = 50 * 1024 * 1024  # 50MB
    
    # PDF Processing
    max_concurrent_pdf_processing: int = 3
    pdf_processing_timeout: int = 300  # seconds
    max_pdf_size: int = 100 * 1024 * 1024  # 100MB
    pdf_dpi: int = 150
    
    # Excel Generation
    excel_max_rows: int = 1000000
    excel_max_columns: int = 16384
    excel_sheet_name: str = "Processed_Data"
    
    # Notification Settings
    enable_desktop_notifications: bool = True
    enable_email_notifications: bool = True
    notification_timeout: int = 10  # seconds
    
    # Email Notification SMTP
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_use_tls: bool = True
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    notification_from_email: str = "noreply@pdfprocessor.local"
    
    # Security
    password_hash_rounds: int = 12
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24 hours
    
    # Logging
    log_level: str = "INFO"
    log_rotation: str = "10 MB"
    log_retention: str = "30 days"
    
    # UI Settings
    window_width: int = 1200
    window_height: int = 800
    theme: str = "default"  # default, dark, light
    
    # Performance
    worker_threads: int = 4
    queue_max_size: int = 1000
    
    # Development/Testing
    test_mode: bool = False
    mock_email: bool = False
    mock_pdf_processing: bool = False
    
    class Config:
        env_file = ".env"
        env_prefix = "PDF_PROCESSOR_"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_directories()
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.data_dir,
            self.pdf_storage_path,
            self.excel_output_path,
            self.temp_dir,
            self.log_dir,
            self.config_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for SQLAlchemy"""
        return self.database_url
    
    @property
    def database_url_async(self) -> str:
        """Asynchronous database URL"""
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    def get_user_data_dir(self, user_id: int) -> Path:
        """Get user-specific data directory"""
        user_dir = self.data_dir / f"user_{user_id}"
        user_dir.mkdir(exist_ok=True)
        return user_dir
    
    def get_user_pdf_dir(self, user_id: int) -> Path:
        """Get user-specific PDF directory"""
        pdf_dir = self.get_user_data_dir(user_id) / "pdfs"
        pdf_dir.mkdir(exist_ok=True)
        return pdf_dir
    
    def get_user_excel_dir(self, user_id: int) -> Path:
        """Get user-specific Excel directory"""
        excel_dir = self.get_user_data_dir(user_id) / "excel"
        excel_dir.mkdir(exist_ok=True)
        return excel_dir


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def update_settings(**kwargs) -> Settings:
    """Update settings with new values"""
    global settings
    
    # Create new settings instance with updated values
    current_dict = settings.dict()
    current_dict.update(kwargs)
    settings = Settings(**current_dict)
    
    return settings


def load_settings_from_file(config_file: Path) -> Settings:
    """Load settings from configuration file"""
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    # Load environment variables from file
    from dotenv import load_dotenv
    load_dotenv(config_file)
    
    # Create new settings instance
    return Settings()


def save_settings_to_file(config_file: Path, settings_obj: Optional[Settings] = None) -> None:
    """Save current settings to configuration file"""
    if settings_obj is None:
        settings_obj = settings
    
    config_content = []
    for key, value in settings_obj.dict().items():
        if value is not None:
            config_content.append(f"PDF_PROCESSOR_{key.upper()}={value}")
    
    with open(config_file, 'w') as f:
        f.write('\n'.join(config_content))


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings"""
    debug: bool = True
    log_level: str = "DEBUG"
    test_mode: bool = True


class ProductionSettings(Settings):
    """Production environment settings"""
    debug: bool = False
    log_level: str = "INFO"
    test_mode: bool = False
    # Override with secure values in production
    secret_key: str = os.getenv("PDF_PROCESSOR_SECRET_KEY", "CHANGE-ME-IN-PRODUCTION")


class TestingSettings(Settings):
    """Testing environment settings"""
    debug: bool = True
    test_mode: bool = True
    mock_email: bool = True
    mock_pdf_processing: bool = True
    database_url: str = "sqlite:///./test.db"


def get_settings_for_environment(env: str = None) -> Settings:
    """Get settings based on environment"""
    if env is None:
        env = os.getenv("ENVIRONMENT", "development").lower()
    
    settings_map = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
        "testing": TestingSettings,
    }
    
    settings_class = settings_map.get(env, DevelopmentSettings)
    return settings_class()