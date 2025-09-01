#!/usr/bin/env python3
"""
PDF Processor Application Build Script
Creates a complete Windows installer package
"""

import os
import sys
import shutil
import subprocess
import zipfile
import json
from pathlib import Path
import requests
import tempfile


class ApplicationBuilder:
    """Build PDF Processor Application for deployment"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.package_dir = self.project_root / "PDFProcessor_Package"
        
        # Version info
        self.app_version = "1.0.0"
        self.app_name = "PDFProcessor"
        
    def clean_build_directories(self):
        """Clean previous build directories"""
        print("🧹 Cleaning build directories...")
        
        directories_to_clean = [self.build_dir, self.dist_dir, self.package_dir]
        for directory in directories_to_clean:
            if directory.exists():
                shutil.rmtree(directory)
                print(f"   Removed: {directory}")
        
        print("✅ Build directories cleaned")
    
    def install_build_dependencies(self):
        """Install required build dependencies"""
        print("📦 Installing build dependencies...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.project_root / "requirements-build.txt")
            ])
            print("✅ Build dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install build dependencies: {e}")
            sys.exit(1)
    
    def create_pyinstaller_spec(self):
        """Create PyInstaller specification file"""
        print("📝 Creating PyInstaller spec file...")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

# Define paths
project_root = Path("{str(self.project_root)}")
src_dir = project_root / "src"
assets_dir = project_root / "assets"
config_dir = project_root / "config"
migrations_dir = project_root / "migrations"

# Analysis configuration
a = Analysis(
    [str(src_dir / "main.py")],
    pathex=[str(src_dir)],
    binaries=[],
    datas=[
        (str(assets_dir), "assets"),
        (str(config_dir), "config"),
        (str(migrations_dir), "migrations"),
    ],
    hiddenimports=[
        "pdfplumber",
        "camelot",
        "tabula",
        "psycopg2",
        "PyQt6.QtWebEngine",
        "PyQt6.QtWebEngineWidgets",
        "uvicorn",
        "fastapi",
        "sqlalchemy",
        "alembic",
        "openpyxl",
        "xlsxwriter",
        "pandas",
        "numpy",
        "cv2",
        "PIL",
        "fitz",  # PyMuPDF
        "exchangelib",
        "imapclient",
        "plyer.platforms.win.notification",
        "win32api",
        "win32con",
        "win32gui",
        "pywintypes",
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "scipy",
        "jupyter",
        "notebook",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary modules to reduce size
a.binaries = [x for x in a.binaries if not x[0].startswith("lib")]
a.datas = [x for x in a.datas if not x[0].endswith(('.pyc', '.pyo'))]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{self.app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windows app, not console
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(assets_dir / "app_icon.ico"),
    version_file=None,  # We'll create this separately
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{self.app_name}',
)
'''
        
        spec_file = self.project_root / f"{self.app_name}.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        print(f"✅ Created spec file: {spec_file}")
        return spec_file
    
    def create_version_file(self):
        """Create version file for Windows executable"""
        print("📋 Creating version file...")
        
        version_info = f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({self.app_version.replace('.', ', ')}, 0),
    prodvers=({self.app_version.replace('.', ', ')}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'PDF Processor Inc.'),
        StringStruct(u'FileDescription', u'PDF to Excel Processor'),
        StringStruct(u'FileVersion', u'{self.app_version}'),
        StringStruct(u'InternalName', u'{self.app_name}'),
        StringStruct(u'LegalCopyright', u'Copyright © 2024 PDF Processor Inc.'),
        StringStruct(u'OriginalFilename', u'{self.app_name}.exe'),
        StringStruct(u'ProductName', u'PDF Processor Application'),
        StringStruct(u'ProductVersion', u'{self.app_version}')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
        
        version_file = self.project_root / "version_info.txt"
        with open(version_file, 'w') as f:
            f.write(version_info)
        
        print(f"✅ Created version file: {version_file}")
        return version_file
    
    def download_postgresql_portable(self):
        """Download portable PostgreSQL for bundling"""
        print("🐘 Downloading portable PostgreSQL...")
        
        postgresql_dir = self.package_dir / "postgresql"
        if postgresql_dir.exists():
            print("   PostgreSQL already exists, skipping download")
            return postgresql_dir
        
        # PostgreSQL portable download URL (adjust version as needed)
        postgresql_version = "15.4"
        download_url = f"https://get.enterprisedb.com/postgresql/postgresql-{postgresql_version}-1-windows-x64-binaries.zip"
        
        try:
            print(f"   Downloading from: {download_url}")
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # Download to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_zip_path = temp_file.name
            
            # Extract PostgreSQL
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.package_dir)
            
            # Rename extracted folder to postgresql
            extracted_folders = [d for d in self.package_dir.iterdir() if d.is_dir() and 'postgresql' in d.name.lower()]
            if extracted_folders:
                extracted_folders[0].rename(postgresql_dir)
            
            # Cleanup
            os.unlink(temp_zip_path)
            
            print("✅ PostgreSQL downloaded and extracted")
            return postgresql_dir
            
        except Exception as e:
            print(f"❌ Failed to download PostgreSQL: {e}")
            print("   You'll need to manually download and place PostgreSQL in the package directory")
            return None
    
    def build_application(self):
        """Build the application using PyInstaller"""
        print("🔨 Building application with PyInstaller...")
        
        spec_file = self.create_pyinstaller_spec()
        version_file = self.create_version_file()
        
        try:
            # Run PyInstaller
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(spec_file)
            ]
            
            print(f"   Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ PyInstaller failed:")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")
                sys.exit(1)
            
            print("✅ Application built successfully")
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            sys.exit(1)
    
    def create_installer_package(self):
        """Create complete installer package"""
        print("📦 Creating installer package...")
        
        # Create package directory structure
        self.package_dir.mkdir(exist_ok=True)
        (self.package_dir / "app").mkdir(exist_ok=True)
        (self.package_dir / "database").mkdir(exist_ok=True)
        (self.package_dir / "config").mkdir(exist_ok=True)
        (self.package_dir / "scripts").mkdir(exist_ok=True)
        
        # Copy built application
        app_source = self.dist_dir / self.app_name
        app_dest = self.package_dir / "app"
        
        if app_source.exists():
            shutil.copytree(app_source, app_dest / self.app_name, dirs_exist_ok=True)
            print(f"   Copied application: {app_source} -> {app_dest}")
        else:
            print(f"❌ Built application not found at: {app_source}")
            sys.exit(1)
        
        # Download PostgreSQL
        self.download_postgresql_portable()
        
        # Copy configuration files
        config_source = self.project_root / "config"
        if config_source.exists():
            shutil.copytree(config_source, self.package_dir / "config", dirs_exist_ok=True)
        
        # Copy database migrations
        migrations_source = self.project_root / "migrations"
        if migrations_source.exists():
            shutil.copytree(migrations_source, self.package_dir / "database" / "migrations", dirs_exist_ok=True)
        
        print("✅ Package structure created")
    
    def create_installation_scripts(self):
        """Create installation and setup scripts"""
        print("📜 Creating installation scripts...")
        
        # Main installer script
        installer_script = '''@echo off
setlocal enabledelayedexpansion

echo ========================================
echo PDF Processor Application Installer
echo Version {app_version}
echo ========================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo ERROR: Administrator privileges required.
    echo Please run this installer as Administrator.
    pause
    exit /b 1
)

REM Set installation directory
set INSTALL_DIR=%PROGRAMFILES%\\PDFProcessor
set DATA_DIR=%PROGRAMDATA%\\PDFProcessor
set LOG_DIR=%DATA_DIR%\\logs

echo Installing to: %INSTALL_DIR%
echo Data directory: %DATA_DIR%

REM Create directories
echo Creating directories...
mkdir "%INSTALL_DIR%" 2>nul
mkdir "%INSTALL_DIR%\\app" 2>nul
mkdir "%INSTALL_DIR%\\database" 2>nul
mkdir "%INSTALL_DIR%\\scripts" 2>nul
mkdir "%DATA_DIR%" 2>nul
mkdir "%DATA_DIR%\\pdfs" 2>nul
mkdir "%DATA_DIR%\\excel" 2>nul
mkdir "%DATA_DIR%\\temp" 2>nul
mkdir "%LOG_DIR%" 2>nul

REM Copy application files
echo Copying application files...
xcopy "app\\*" "%INSTALL_DIR%\\app\\" /E /I /Q /Y
xcopy "database\\*" "%INSTALL_DIR%\\database\\" /E /I /Q /Y
xcopy "config\\*" "%INSTALL_DIR%\\config\\" /E /I /Q /Y
xcopy "scripts\\*" "%INSTALL_DIR%\\scripts\\" /E /I /Q /Y

REM Setup PostgreSQL
echo Setting up PostgreSQL database...
cd "%INSTALL_DIR%\\database\\postgresql\\bin"

REM Initialize database if not exists
if not exist "%DATA_DIR%\\database\\postgresql" (
    echo Initializing PostgreSQL database...
    initdb.exe -D "%DATA_DIR%\\database\\postgresql" -U postgres --auth-local=trust --encoding=UTF8
    if !errorLevel! NEQ 0 (
        echo ERROR: Failed to initialize PostgreSQL database
        pause
        exit /b 1
    )
)

REM Start PostgreSQL service
echo Starting PostgreSQL service...
pg_ctl.exe -D "%DATA_DIR%\\database\\postgresql" -l "%LOG_DIR%\\postgresql.log" start
timeout /t 5 >nul

REM Create application database
echo Creating application database...
createdb.exe -U postgres pdf_processor
if !errorLevel! NEQ 0 (
    echo WARNING: Database may already exist or failed to create
)

REM Run database migrations
echo Running database migrations...
psql.exe -U postgres -d pdf_processor -f "%INSTALL_DIR%\\database\\migrations\\init.sql"

REM Create configuration file
echo Creating configuration file...
(
echo PDF_PROCESSOR_DATABASE_URL=postgresql://postgres:@localhost:5432/pdf_processor
echo PDF_PROCESSOR_DATA_DIR=%DATA_DIR%
echo PDF_PROCESSOR_LOG_DIR=%LOG_DIR%
echo PDF_PROCESSOR_DEBUG=False
) > "%INSTALL_DIR%\\config\\.env"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%PUBLIC%\\Desktop\\PDF Processor.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\app\\{app_name}\\{app_name}.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%\\app\\{app_name}'; $Shortcut.IconLocation = '%INSTALL_DIR%\\app\\{app_name}\\{app_name}.exe'; $Shortcut.Save()"

REM Create start menu shortcut
echo Creating start menu shortcut...
mkdir "%PROGRAMDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\PDF Processor" 2>nul
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%PROGRAMDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\PDF Processor\\PDF Processor.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\app\\{app_name}\\{app_name}.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%\\app\\{app_name}'; $Shortcut.IconLocation = '%INSTALL_DIR%\\app\\{app_name}\\{app_name}.exe'; $Shortcut.Save()"

REM Register Windows service (optional)
echo Registering Windows service...
sc create "PDFProcessorService" binpath= "%INSTALL_DIR%\\app\\{app_name}\\{app_name}.exe --service" start= auto displayname= "PDF Processor Service"

REM Create uninstaller
echo Creating uninstaller...
(
echo @echo off
echo echo Uninstalling PDF Processor Application...
echo.
echo REM Stop service
echo sc stop "PDFProcessorService" ^>nul 2^>^&1
echo sc delete "PDFProcessorService" ^>nul 2^>^&1
echo.
echo REM Stop PostgreSQL
echo "%INSTALL_DIR%\\database\\postgresql\\bin\\pg_ctl.exe" -D "%DATA_DIR%\\database\\postgresql" stop ^>nul 2^>^&1
echo.
echo REM Remove files
echo rmdir /s /q "%INSTALL_DIR%" ^>nul 2^>^&1
echo rmdir /s /q "%DATA_DIR%" ^>nul 2^>^&1
echo del "%PUBLIC%\\Desktop\\PDF Processor.lnk" ^>nul 2^>^&1
echo rmdir /s /q "%PROGRAMDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\PDF Processor" ^>nul 2^>^&1
echo.
echo echo PDF Processor has been uninstalled.
echo pause
) > "%INSTALL_DIR%\\scripts\\uninstall.bat"

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo Application installed to: %INSTALL_DIR%
echo Data directory: %DATA_DIR%
echo.
echo You can now start PDF Processor from:
echo - Desktop shortcut
echo - Start menu
echo - Or run: %INSTALL_DIR%\\app\\{app_name}\\{app_name}.exe
echo.
pause
'''.format(app_version=self.app_version, app_name=self.app_name)
        
        # Save installer script
        installer_path = self.package_dir / "install.bat"
        with open(installer_path, 'w') as f:
            f.write(installer_script)
        
        # Create service script
        service_script = '''@echo off
REM PDF Processor Service Management Script

if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="install" goto install
if "%1"=="uninstall" goto uninstall

echo Usage: service.bat [start^|stop^|restart^|install^|uninstall]
goto end

:start
echo Starting PDF Processor Service...
sc start "PDFProcessorService"
goto end

:stop
echo Stopping PDF Processor Service...
sc stop "PDFProcessorService"
goto end

:restart
echo Restarting PDF Processor Service...
sc stop "PDFProcessorService"
timeout /t 5 >nul
sc start "PDFProcessorService"
goto end

:install
echo Installing PDF Processor Service...
sc create "PDFProcessorService" binpath= "%~dp0..\\app\\{app_name}\\{app_name}.exe --service" start= auto displayname= "PDF Processor Service"
goto end

:uninstall
echo Uninstalling PDF Processor Service...
sc stop "PDFProcessorService"
sc delete "PDFProcessorService"
goto end

:end
'''.format(app_name=self.app_name)
        
        service_path = self.package_dir / "scripts" / "service.bat"
        with open(service_path, 'w') as f:
            f.write(service_script)
        
        print("✅ Installation scripts created")
    
    def create_readme(self):
        """Create README file for the package"""
        print("📖 Creating README file...")
        
        readme_content = f'''# PDF Processor Application v{self.app_version}

## Installation Instructions

### Prerequisites
- Windows 10 or Windows 11 (64-bit)
- Administrator privileges for installation
- At least 4GB RAM (8GB recommended)
- 2GB free disk space

### Installation Steps

1. **Extract Package**: Extract the PDF Processor package to a temporary directory
2. **Run Installer**: Right-click on `install.bat` and select "Run as administrator"
3. **Follow Prompts**: The installer will:
   - Install the application to Program Files
   - Set up PostgreSQL database
   - Create desktop and start menu shortcuts
   - Register Windows service (optional)

### First-Time Setup

1. **Launch Application**: Use desktop shortcut or start menu
2. **Create Admin User**: Set up the first administrator account
3. **Configure Email**: Add email accounts to monitor
4. **Create PDF Mappings**: Set up PDF-to-Excel conversion rules

### Usage

#### Email Configuration
1. Go to "Email Accounts" tab
2. Click "Add Account"
3. Enter IMAP server details:
   - Server: imap.gmail.com (for Gmail)
   - Port: 993
   - Use SSL: Yes
   - Username/Password: Your credentials

#### PDF Mapping
1. Go to "PDF Mapping" tab
2. Click "Create New Rule"
3. Upload sample PDF to design mapping
4. Configure table detection and Excel output format
5. Save and test the rule

#### Processing
- The application monitors emails automatically
- PDFs are processed using configured rules
- Excel files are generated and stored
- Notifications are sent upon completion

### API Access

The application provides a REST API for programmatic access:
- Base URL: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Authentication: JWT tokens required

### Troubleshooting

#### Application Won't Start
- Check if PostgreSQL service is running
- Verify database connection in logs
- Ensure no port conflicts (8000 for API)

#### Email Not Processing
- Verify email account credentials
- Check IMAP server settings
- Review email filtering rules

#### PDF Processing Errors
- Check PDF file size (max 100MB)
- Verify PDF contains tables
- Review mapping rules configuration

### Log Files
- Application logs: `%PROGRAMDATA%\\PDFProcessor\\logs\\app.log`
- PostgreSQL logs: `%PROGRAMDATA%\\PDFProcessor\\logs\\postgresql.log`

### Uninstallation
Run `%PROGRAMFILES%\\PDFProcessor\\scripts\\uninstall.bat` as administrator

### Support
For technical support, please contact your system administrator or refer to the application documentation.

---
PDF Processor Application v{self.app_version}
Copyright © 2024 PDF Processor Inc.
'''
        
        readme_path = self.package_dir / "README.txt"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print("✅ README file created")
    
    def create_package_info(self):
        """Create package information file"""
        package_info = {
            "name": "PDF Processor Application",
            "version": self.app_version,
            "build_date": "2024-12-01",
            "platform": "Windows x64",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "dependencies": {
                "postgresql": "15.4",
                "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            }
        }
        
        info_path = self.package_dir / "package_info.json"
        with open(info_path, 'w') as f:
            json.dump(package_info, f, indent=2)
    
    def build_complete_package(self):
        """Build complete deployment package"""
        print("🚀 Starting complete build process...")
        print(f"   Project root: {self.project_root}")
        print(f"   Build directory: {self.build_dir}")
        print(f"   Package directory: {self.package_dir}")
        print()
        
        # Step 1: Clean and prepare
        self.clean_build_directories()
        
        # Step 2: Install dependencies
        self.install_build_dependencies()
        
        # Step 3: Build application
        self.build_application()
        
        # Step 4: Create package
        self.create_installer_package()
        
        # Step 5: Create scripts
        self.create_installation_scripts()
        
        # Step 6: Create documentation
        self.create_readme()
        self.create_package_info()
        
        print("🎉 Build completed successfully!")
        print(f"   Package location: {self.package_dir}")
        print(f"   Installer: {self.package_dir / 'install.bat'}")
        print()
        print("To install:")
        print(f"   1. Copy {self.package_dir} to target machine")
        print("   2. Run install.bat as Administrator")


def main():
    """Main build script execution"""
    builder = ApplicationBuilder()
    
    try:
        builder.build_complete_package()
    except KeyboardInterrupt:
        print("\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()