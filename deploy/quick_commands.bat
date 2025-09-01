@echo off
REM PDF Processor Application - Quick Commands
REM Usage: quick_commands.bat [command]
REM Commands: setup, build, test, deploy, clean, help

setlocal enabledelayedexpansion

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="setup" goto setup
if "%1"=="build" goto build
if "%1"=="test" goto test
if "%1"=="deploy" goto deploy
if "%1"=="clean" goto clean
if "%1"=="install" goto install
if "%1"=="status" goto status
if "%1"=="logs" goto logs

echo Invalid command: %1
goto help

:help
echo.
echo PDF Processor Application - Quick Commands
echo ==========================================
echo.
echo Usage: quick_commands.bat [command]
echo.
echo Available commands:
echo   setup   - Set up development environment
echo   build   - Build application for deployment
echo   test    - Run complete test suite
echo   deploy  - Create deployment package
echo   clean   - Clean build directories
echo   install - Install application (run as admin)
echo   status  - Check application status
echo   logs    - View recent application logs
echo   help    - Show this help message
echo.
echo Examples:
echo   quick_commands.bat setup
echo   quick_commands.bat build
echo   quick_commands.bat test
echo.
goto end

:setup
echo.
echo 🔧 Setting up development environment...
echo ========================================

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.9+ first.
    echo    Download from: https://www.python.org/downloads/
    goto end
)

echo ✅ Python found: 
python --version

REM Create virtual environment
echo.
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ℹ️  Virtual environment already exists
)

REM Activate virtual environment and install dependencies
echo.
echo Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements-build.txt

if %errorlevel% equ 0 (
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ Failed to install dependencies
    goto end
)

REM Create configuration file if it doesn't exist
echo.
echo Setting up configuration...
if not exist "config\.env" (
    copy "config\.env.template" "config\.env" >nul
    echo ✅ Configuration file created: config\.env
    echo ℹ️  Please edit config\.env with your settings
) else (
    echo ℹ️  Configuration file already exists
)

echo.
echo ✅ Development environment setup complete!
echo.
echo Next steps:
echo 1. Edit config\.env with your database settings
echo 2. Set up PostgreSQL database
echo 3. Run: quick_commands.bat test
echo.
goto end

:build
echo.
echo 🔨 Building application...
echo ==========================

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found. Run 'quick_commands.bat setup' first.
    goto end
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if source files exist
if not exist "src\main.py" (
    echo ❌ Source files not found. Please check project structure.
    goto end
)

echo Running build script...
python deploy\build_installer.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ Build completed successfully!
    echo 📦 Package location: PDFProcessor_Package\
    echo 🚀 Ready for deployment
) else (
    echo ❌ Build failed. Check error messages above.
)
goto end

:test
echo.
echo 🧪 Running test suite...
echo ========================

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found. Run 'quick_commands.bat setup' first.
    goto end
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Running comprehensive tests...
python tests\test_runner.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ All tests passed!
    echo 🚀 Ready for build and deployment
) else (
    echo ❌ Some tests failed. Please fix issues before deployment.
)
goto end

:deploy
echo.
echo 🚀 Creating deployment package...
echo =================================

REM Run build first
echo Step 1: Building application...
call :build

if %errorlevel% neq 0 (
    echo ❌ Build failed, cannot create deployment package
    goto end
)

REM Verify package was created
if not exist "PDFProcessor_Package" (
    echo ❌ Deployment package not created
    goto end
)

echo.
echo Step 2: Preparing deployment package...

REM Create deployment archive
if exist "PDFProcessor_Package.zip" del "PDFProcessor_Package.zip"
powershell -Command "Compress-Archive -Path 'PDFProcessor_Package\*' -DestinationPath 'PDFProcessor_Package.zip'"

if exist "PDFProcessor_Package.zip" (
    echo ✅ Deployment archive created: PDFProcessor_Package.zip
    
    echo.
    echo 📋 Deployment Instructions:
    echo 1. Copy PDFProcessor_Package.zip to target machine
    echo 2. Extract the archive
    echo 3. Run install.bat as Administrator
    echo 4. Follow the installation prompts
    echo.
    
    REM Show package contents
    echo 📦 Package contents:
    dir PDFProcessor_Package /b
) else (
    echo ❌ Failed to create deployment archive
)
goto end

:clean
echo.
echo 🧹 Cleaning build directories...
echo =================================

REM Clean Python cache
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "src\__pycache__" rmdir /s /q "src\__pycache__"

REM Clean build directories
if exist "build" (
    rmdir /s /q "build"
    echo ✅ Removed build directory
)

if exist "dist" (
    rmdir /s /q "dist"
    echo ✅ Removed dist directory
)

if exist "PDFProcessor_Package" (
    rmdir /s /q "PDFProcessor_Package"
    echo ✅ Removed package directory
)

if exist "PDFProcessor_Package.zip" (
    del "PDFProcessor_Package.zip"
    echo ✅ Removed package archive
)

REM Clean PyInstaller files
if exist "*.spec" del "*.spec"
if exist "version_info.txt" del "version_info.txt"

REM Clean test files
if exist "test.db" del "test.db"
if exist "test_pdf_processor.db" del "test_pdf_processor.db"

REM Clean log files (optional)
if exist "logs" (
    echo Do you want to clean log files? (y/N)
    set /p clean_logs=
    if /i "!clean_logs!"=="y" (
        rmdir /s /q "logs"
        echo ✅ Removed log files
    )
)

echo.
echo ✅ Cleanup completed!
goto end

:install
echo.
echo 📦 Installing PDF Processor Application...
echo ==========================================

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ This command requires administrator privileges.
    echo Please run Command Prompt as Administrator and try again.
    goto end
)

REM Check if package exists
if not exist "PDFProcessor_Package\install.bat" (
    echo ❌ Installation package not found.
    echo Please run 'quick_commands.bat deploy' first to create the package.
    goto end
)

echo Running installer...
cd PDFProcessor_Package
call install.bat
cd ..

echo.
echo ✅ Installation completed!
echo 🚀 PDF Processor is now installed and ready to use.
goto end

:status
echo.
echo 📊 PDF Processor Application Status
echo ===================================

REM Check if application is installed
if exist "%PROGRAMFILES%\PDFProcessor" (
    echo ✅ Application installed at: %PROGRAMFILES%\PDFProcessor
) else (
    echo ❌ Application not installed
    goto end
)

REM Check service status
echo.
echo Service Status:
sc query PDFProcessorService >nul 2>&1
if %errorlevel% equ 0 (
    sc query PDFProcessorService | findstr "STATE"
) else (
    echo ❌ Service not registered
)

REM Check if PostgreSQL is running
echo.
echo Database Status:
if exist "%PROGRAMFILES%\PDFProcessor\database\postgresql\bin\pg_isready.exe" (
    "%PROGRAMFILES%\PDFProcessor\database\postgresql\bin\pg_isready.exe" -p 5432 >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Database is running
    ) else (
        echo ❌ Database is not responding
    )
) else (
    echo ❌ Database tools not found
)

REM Check API status
echo.
echo API Status:
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API is responding
) else (
    echo ❌ API is not accessible
)

REM Show recent activity
echo.
echo Recent Processing Activity:
if exist "%PROGRAMDATA%\PDFProcessor\logs\app.log" (
    type "%PROGRAMDATA%\PDFProcessor\logs\app.log" | findstr /C:"INFO" /C:"SUCCESS" | tail -5
) else (
    echo ℹ️  No log file found
)

goto end

:logs
echo.
echo 📋 Recent Application Logs
echo ==========================

REM Application logs
echo Application Logs:
if exist "%PROGRAMDATA%\PDFProcessor\logs\app.log" (
    echo Last 20 entries from app.log:
    type "%PROGRAMDATA%\PDFProcessor\logs\app.log" | tail -20
) else (
    echo ℹ️  No application log file found
)

echo.
echo Database Logs:
if exist "%PROGRAMDATA%\PDFProcessor\logs\postgresql.log" (
    echo Last 10 entries from postgresql.log:
    type "%PROGRAMDATA%\PDFProcessor\logs\postgresql.log" | tail -10
) else (
    echo ℹ️  No database log file found
)

echo.
echo Error Logs:
if exist "%PROGRAMDATA%\PDFProcessor\logs\app.log" (
    echo Recent errors:
    type "%PROGRAMDATA%\PDFProcessor\logs\app.log" | findstr /C:"ERROR" /C:"CRITICAL" | tail -10
) else (
    echo ℹ️  No error logs found
)

goto end

:end
endlocal
echo.
pause