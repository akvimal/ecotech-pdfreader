# PDF Processor Application - Complete Deployment Guide

## 🚀 Development to Production Deployment Pipeline

### Prerequisites
- Windows 10/11 (64-bit) development machine
- Python 3.9+ installed
- Git for version control
- Administrator privileges for deployment

---

## Phase 1: Development Environment Setup

### 1.1 Clone and Setup Project
```bash
# Clone repository
git clone <your-repo-url> pdf-processor-app
cd pdf-processor-app

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install development dependencies
pip install -r requirements-build.txt
```

### 1.2 Environment Configuration
```bash
# Copy environment template
copy config\.env.template config\.env

# Edit config\.env with your settings
notepad config\.env
```

**Required Environment Variables:**
```env
PDF_PROCESSOR_DATABASE_URL=postgresql://postgres:password@localhost:5432/pdf_processor
PDF_PROCESSOR_SECRET_KEY=your-super-secret-key-here
PDF_PROCESSOR_API_HOST=127.0.0.1
PDF_PROCESSOR_API_PORT=8000
PDF_PROCESSOR_DEBUG=True
PDF_PROCESSOR_LOG_LEVEL=DEBUG
```

### 1.3 Database Setup
```bash
# Install PostgreSQL locally for development
# Download from: https://www.postgresql.org/download/windows/

# Create database
psql -U postgres -c "CREATE DATABASE pdf_processor;"

# Run migrations
psql -U postgres -d pdf_processor -f migrations/init.sql
```

---

## Phase 2: Development and Testing

### 2.1 Run Development Server
```bash
# Activate virtual environment
venv\Scripts\activate

# Start application in development mode
python src/main.py
```

### 2.2 Run Tests
```bash
# Run complete test suite
python tests/test_runner.py

# Run specific test categories
pytest tests/test_pdf_processor.py -v
pytest tests/test_email_monitor.py -v
pytest tests/test_api_endpoints.py -v
```

### 2.3 Code Quality Checks
```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/
```

---

## Phase 3: Build Application

### 3.1 Run Build Script
```bash
# Execute complete build process
python deploy/build_installer.py
```

**The build script will:**
- Clean previous builds
- Install build dependencies
- Create PyInstaller spec file
- Build application executable
- Download PostgreSQL portable
- Create installer package
- Generate installation scripts

### 3.2 Build Output Structure
```
PDFProcessor_Package/
├── install.bat              # Main installer script
├── README.txt              # Installation instructions
├── package_info.json       # Build information
├── app/
│   └── PDFProcessor/       # Built application
│       ├── PDFProcessor.exe
│       ├── _internal/      # Dependencies
│       └── ...
├── database/
│   ├── postgresql/         # Portable PostgreSQL
│   └── migrations/         # Database scripts
├── config/
│   ├── .env.template      # Configuration template
│   └── settings.yaml     # Default settings
└── scripts/
    ├── service.bat        # Service management
    └── uninstall.bat     # Uninstaller
```

---

## Phase 4: Pre-Deployment Testing

### 4.1 Test Built Application
```bash
# Navigate to built application
cd PDFProcessor_Package\app\PDFProcessor

# Test executable
PDFProcessor.exe --test

# Check dependencies
PDFProcessor.exe --check-deps
```

### 4.2 Test Installation Package
```bash
# Create test VM or clean Windows environment
# Copy PDFProcessor_Package to test machine

# Run installer in test environment
# Right-click install.bat -> "Run as administrator"
```

### 4.3 Integration Testing
```bash
# Test complete workflow:
# 1. Install application
# 2. Create user account
# 3. Configure email account
# 4. Create PDF mapping rule
# 5. Process test PDF
# 6. Verify Excel output
# 7. Test API endpoints
# 8. Check notifications
```

---

## Phase 5: Production Deployment

### 5.1 Client Machine Requirements
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for email processing
- **Permissions**: Administrator rights for installation

### 5.2 Pre-Installation Checklist
```powershell
# Check system requirements
systeminfo | findstr /C:"OS Name" /C:"Total Physical Memory"

# Check available disk space
dir C:\ | findstr "bytes free"

# Check if ports are available
netstat -an | findstr ":8000"
netstat -an | findstr ":5432"

# Check firewall settings
netsh advfirewall show allprofiles

# Verify PowerShell execution policy
Get-ExecutionPolicy
```

### 5.3 Installation Process
```batch
:: 1. Copy package to target machine
xcopy "\\source\PDFProcessor_Package" "C:\temp\PDFProcessor_Package" /E /I

:: 2. Run installer as Administrator
cd "C:\temp\PDFProcessor_Package"
install.bat

:: 3. Verify installation
dir "%PROGRAMFILES%\PDFProcessor"
sc query PDFProcessorService
```

### 5.4 Post-Installation Configuration
```batch
:: 1. Start application
"%PROGRAMFILES%\PDFProcessor\app\PDFProcessor\PDFProcessor.exe"

:: 2. Create admin user (first run)
:: Follow GUI prompts to create administrator account

:: 3. Configure application settings
:: - Email accounts
:: - PDF mapping rules
:: - Notification preferences
:: - User accounts

:: 4. Test functionality
:: - Send test email with PDF attachment
:: - Verify processing and Excel generation
:: - Check API endpoints: http://localhost:8000/docs
```

---

## Phase 6: Post-Deployment Verification

### 6.1 System Health Checks
```powershell
# Check service status
Get-Service PDFProcessorService

# Check application logs
Get-Content "$env:PROGRAMDATA\PDFProcessor\logs\app.log" -Tail 50

# Check database connectivity
& "$env:PROGRAMFILES\PDFProcessor\database\postgresql\bin\psql.exe" -U postgres -d pdf_processor -c "SELECT version();"

# Check API health
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
```

### 6.2 Functional Testing
```powershell
# Test email processing
# 1. Configure email account in application
# 2. Send email with PDF attachment to configured account
# 3. Verify PDF processing and Excel generation
# 4. Check notification delivery

# Test API endpoints
$token = "your-jwt-token"
$headers = @{ "Authorization" = "Bearer $token" }

# Get processing jobs
Invoke-RestMethod -Uri "http://localhost:8000/api/jobs" -Headers $headers

# Get user statistics
Invoke-RestMethod -Uri "http://localhost:8000/api/users/stats" -Headers $headers
```

### 6.3 Performance Monitoring
```powershell
# Monitor resource usage
Get-Counter "\Process(PDFProcessor)\% Processor Time"
Get-Counter "\Process(PDFProcessor)\Working Set"

# Check processing queue
# Monitor logs for processing times and success rates
```

---

## Phase 7: Maintenance and Updates

### 7.1 Regular Maintenance Tasks
```batch
:: Weekly maintenance script
@echo off
echo Running weekly maintenance...

:: Clean temporary files
del /q "%PROGRAMDATA%\PDFProcessor\temp\*"

:: Rotate logs (keep last 30 days)
forfiles /p "%PROGRAMDATA%\PDFProcessor\logs" /s /m *.log /d -30 /c "cmd /c del @path"

:: Clean old processed files (optional)
:: forfiles /p "%PROGRAMDATA%\PDFProcessor\data\excel" /s /m *.xlsx /d -90 /c "cmd /c del @path"

:: Database maintenance
"%PROGRAMFILES%\PDFProcessor\database\postgresql\bin\psql.exe" -U postgres -d pdf_processor -c "VACUUM ANALYZE;"

echo Maintenance completed.
```

### 7.2 Backup Procedures
```batch
:: Daily backup script
@echo off
set BACKUP_DIR=%PROGRAMDATA%\PDFProcessor\backups\%date:~-4,4%-%date:~-10,2%-%date:~-7,2%
mkdir "%BACKUP_DIR%" 2>nul

:: Backup database
"%PROGRAMFILES%\PDFProcessor\database\postgresql\bin\pg_dump.exe" -U postgres pdf_processor > "%BACKUP_DIR%\database_backup.sql"

:: Backup configuration
xcopy "%PROGRAMFILES%\PDFProcessor\config" "%BACKUP_DIR%\config\" /E /I

:: Backup user data (optional - may be large)
:: xcopy "%PROGRAMDATA%\PDFProcessor\data" "%BACKUP_DIR%\data\" /E /I

echo Backup completed: %BACKUP_DIR%
```

### 7.3 Update Deployment
```batch
:: Application update process
@echo off
echo Updating PDF Processor Application...

:: Stop service
sc stop PDFProcessorService

:: Backup current version
xcopy "%PROGRAMFILES%\PDFProcessor\app" "%PROGRAMDATA%\PDFProcessor\backups\pre_update_backup\" /E /I

:: Install new version
xcopy "new_version\app\*" "%PROGRAMFILES%\PDFProcessor\app\" /E /I /Y

:: Run database migrations if needed
"%PROGRAMFILES%\PDFProcessor\database\postgresql\bin\psql.exe" -U postgres -d pdf_processor -f "new_version\migrations\update.sql"

:: Start service
sc start PDFProcessorService

echo Update completed.
```

---

## Phase 8: Troubleshooting

### 8.1 Common Issues and Solutions

#### Application Won't Start
```powershell
# Check service status
Get-Service PDFProcessorService

# Check logs for errors
Get-Content "$env:PROGRAMDATA\PDFProcessor\logs\app.log" -Tail 20

# Verify database connection
& "$env:PROGRAMFILES\PDFProcessor\database\postgresql\bin\pg_isready.exe" -p 5432

# Common solutions:
# - Restart PostgreSQL service
# - Check port conflicts
# - Verify file permissions
```

#### Email Processing Not Working
```powershell
# Check email account configuration
# Verify IMAP settings and credentials
# Check firewall settings for email ports (993, 587)
# Review email processing logs
```

#### PDF Processing Failures
```powershell
# Check PDF file format and size
# Verify mapping rule configuration
# Check available disk space
# Review processing error logs
```

### 8.2 Diagnostic Commands
```batch
:: System diagnostic script
@echo off
echo PDF Processor System Diagnostics
echo ================================

:: Check installation
echo Checking installation...
dir "%PROGRAMFILES%\PDFProcessor" >nul 2>&1 && echo "✓ Application installed" || echo "✗ Application not found"

:: Check service
sc query PDFProcessorService | findstr "RUNNING" >nul && echo "✓ Service running" || echo "✗ Service not running"

:: Check database
"%PROGRAMFILES%\PDFProcessor\database\postgresql\bin\pg_isready.exe" -p 5432 >nul 2>&1 && echo "✓ Database accessible" || echo "✗ Database connection failed"

:: Check API
curl -s http://localhost:8000/health >nul 2>&1 && echo "✓ API responding" || echo "✗ API not accessible"

:: Check logs
echo.
echo Recent log entries:
type "%PROGRAMDATA%\PDFProcessor\logs\app.log" | findstr /C:"ERROR" /C:"CRITICAL" | tail -5

echo.
echo Diagnostics completed.
```

---

## Phase 9: Security Considerations

### 9.1 Security Hardening
```powershell
# Change default passwords immediately after installation
# Configure strong JWT secret key
# Set up proper file permissions
# Enable Windows Firewall rules for necessary ports only
# Regular security updates

# File permission hardening
icacls "%PROGRAMFILES%\PDFProcessor" /inheritance:r
icacls "%PROGRAMFILES%\PDFProcessor" /grant:r "Administrators:(OI)(CI)F"
icacls "%PROGRAMFILES%\PDFProcessor" /grant:r "SYSTEM:(OI)(CI)F"
icacls "%PROGRAMFILES%\PDFProcessor" /grant:r "Users:(OI)(CI)RX"
```

### 9.2 Network Security
```batch
:: Configure Windows Firewall
netsh advfirewall firewall add rule name="PDF Processor API" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="PostgreSQL Local" dir=in action=allow protocol=TCP localport=5432

:: Disable unnecessary ports
:: Review and restrict access to API endpoints
```

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Development environment tested
- [ ] All tests passing (unit, integration, security)
- [ ] Application built successfully
- [ ] Installation package created
- [ ] Documentation updated
- [ ] Client machine requirements verified

### Installation
- [ ] System requirements met
- [ ] Installation completed successfully
- [ ] Database initialized
- [ ] Service registered and started
- [ ] Desktop shortcuts created
- [ ] Configuration completed

### Post-Installation
- [ ] Application starts correctly
- [ ] Admin user created
- [ ] Email account configured
- [ ] PDF mapping rule tested
- [ ] Excel output generated successfully
- [ ] API endpoints accessible
- [ ] Notifications working
- [ ] Logs monitoring setup
- [ ] Backup procedures configured

### Production Ready
- [ ] Security hardening applied
- [ ] Performance monitoring enabled
- [ ] Maintenance schedule established
- [ ] Support documentation provided
- [ ] User training completed

---

## 🆘 Support and Maintenance

### Log Locations
- **Application Logs**: `%PROGRAMDATA%\PDFProcessor\logs\app.log`
- **Database Logs**: `%PROGRAMDATA%\PDFProcessor\logs\postgresql.log`
- **Windows Service Logs**: Windows Event Viewer → Application Logs

### Configuration Files
- **Main Config**: `%PROGRAMFILES%\PDFProcessor\config\.env`
- **Database Config**: `%PROGRAMDATA%\PDFProcessor\database\postgresql\postgresql.conf`
- **User Settings**: `%PROGRAMDATA%\PDFProcessor\config\user_settings.json`

### Important Ports
- **8000**: Application API
- **5432**: PostgreSQL Database (local only)

For additional support or advanced configuration, refer to the technical documentation or contact your system administrator.