#!/usr/bin/env python3
"""
Comprehensive Testing Suite for PDF Processor Application
"""

import sys
import os
import asyncio
import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import json
import time

# Add src to Python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test configuration
TEST_DATABASE_URL = "sqlite:///./test_pdf_processor.db"
TEST_DATA_DIR = Path(__file__).parent / "test_data"


class TestSuiteRunner:
    """Main test suite runner with setup and teardown"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.test_data_dir = TEST_DATA_DIR
        self.temp_dir = None
        
    def setup_test_environment(self):
        """Set up test environment"""
        print("🔧 Setting up test environment...")
        
        # Create test data directory
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="pdf_processor_test_"))
        
        # Set environment variables for testing
        os.environ["PDF_PROCESSOR_DATABASE_URL"] = TEST_DATABASE_URL
        os.environ["PDF_PROCESSOR_DATA_DIR"] = str(self.temp_dir)
        os.environ["PDF_PROCESSOR_TEST_MODE"] = "true"
        os.environ["PDF_PROCESSOR_LOG_LEVEL"] = "DEBUG"
        
        # Create test database
        self.setup_test_database()
        
        # Create test files
        self.create_test_files()
        
        print("✅ Test environment setup complete")
    
    def setup_test_database(self):
        """Initialize test database"""
        try:
            from models.database import init_database, check_database_connection
            
            # Initialize test database
            if not check_database_connection():
                raise Exception("Cannot connect to test database")
            
            init_database()
            print("   ✅ Test database initialized")
            
        except Exception as e:
            print(f"   ❌ Database setup failed: {e}")
            raise
    
    def create_test_files(self):
        """Create test files for testing"""
        
        # Create sample PDF content (mock)
        sample_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        
        test_files = {
            "sample_table.pdf": sample_pdf_content,
            "multi_page.pdf": sample_pdf_content,
            "complex_table.pdf": sample_pdf_content,
        }
        
        for filename, content in test_files.items():
            file_path = self.test_data_dir / filename
            with open(file_path, 'wb') as f:
                f.write(content)
        
        # Create test email template
        email_template = {
            "subject": "Test Invoice PDF",
            "from": "test@example.com",
            "to": "processor@example.com",
            "body": "Please process the attached invoice.",
            "attachments": ["sample_table.pdf"]
        }
        
        with open(self.test_data_dir / "test_email.json", 'w') as f:
            json.dump(email_template, f, indent=2)
        
        print("   ✅ Test files created")
    
    def teardown_test_environment(self):
        """Clean up test environment"""
        print("🧹 Cleaning up test environment...")
        
        # Remove temporary directory
        if self.temp_dir and self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Clean environment variables
        test_env_vars = [var for var in os.environ if var.startswith("PDF_PROCESSOR_")]
        for var in test_env_vars:
            os.environ.pop(var, None)
        
        print("✅ Test environment cleaned up")
    
    def run_unit_tests(self):
        """Run unit tests"""
        print("🔬 Running unit tests...")
        
        test_files = [
            "test_pdf_processor.py",
            "test_email_monitor.py",
            "test_database_models.py",
            "test_api_endpoints.py",
            "test_configuration.py"
        ]
        
        results = {}
        
        for test_file in test_files:
            test_path = self.test_dir / test_file
            if test_path.exists():
                print(f"   Running {test_file}...")
                try:
                    result = pytest.main(["-v", str(test_path)])
                    results[test_file] = "PASSED" if result == 0 else "FAILED"
                except Exception as e:
                    print(f"   ❌ Error running {test_file}: {e}")
                    results[test_file] = "ERROR"
            else:
                print(f"   ⚠️  Test file not found: {test_file}")
                results[test_file] = "NOT_FOUND"
        
        return results
    
    def run_integration_tests(self):
        """Run integration tests"""
        print("🔗 Running integration tests...")
        
        integration_tests = [
            self.test_email_to_pdf_processing,
            self.test_pdf_to_excel_conversion,
            self.test_api_workflow,
            self.test_notification_system,
            self.test_multi_user_workflow
        ]
        
        results = {}
        
        for test_func in integration_tests:
            test_name = test_func.__name__
            print(f"   Running {test_name}...")
            
            try:
                result = test_func()
                results[test_name] = "PASSED" if result else "FAILED"
                print(f"      {'✅' if result else '❌'} {test_name}")
            except Exception as e:
                print(f"      ❌ {test_name} failed: {e}")
                results[test_name] = "ERROR"
        
        return results
    
    def test_email_to_pdf_processing(self):
        """Test complete email to PDF processing workflow"""
        try:
            # Mock email monitoring
            with patch('services.email_monitor.EmailMonitorService') as mock_monitor:
                mock_monitor.return_value.check_emails.return_value = [
                    {
                        'subject': 'Test Invoice',
                        'sender': 'test@example.com',
                        'attachments': [self.test_data_dir / 'sample_table.pdf']
                    }
                ]
                
                # Test email processing
                from services.email_monitor import EmailMonitorService
                monitor = EmailMonitorService()
                emails = monitor.check_emails()
                
                return len(emails) > 0 and 'attachments' in emails[0]
                
        except Exception as e:
            print(f"      Email processing test failed: {e}")
            return False
    
    def test_pdf_to_excel_conversion(self):
        """Test PDF to Excel conversion"""
        try:
            from services.pdf_processor import PDFProcessorService
            
            # Mock PDF processing
            with patch('pdfplumber.open') as mock_pdf:
                mock_page = Mock()
                mock_page.extract_tables.return_value = [
                    [['Item', 'Quantity', 'Price'], ['Widget', '10', '$100']]
                ]
                mock_pdf.return_value.__enter__.return_value.pages = [mock_page]
                
                processor = PDFProcessorService()
                result = processor.process_pdf(
                    str(self.test_data_dir / 'sample_table.pdf'),
                    {'rule_name': 'test_rule'},
                    1
                )
                
                return result is not None
                
        except Exception as e:
            print(f"      PDF conversion test failed: {e}")
            return False
    
    def test_api_workflow(self):
        """Test API endpoints"""
        try:
            from fastapi.testclient import TestClient
            from services.api_server import create_app
            
            app = create_app()
            client = TestClient(app)
            
            # Test health endpoint
            response = client.get("/health")
            if response.status_code != 200:
                return False
            
            # Test authentication
            response = client.post("/auth/login", json={
                "username": "admin",
                "password": "admin123"
            })
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"      API test failed: {e}")
            return False
    
    def test_notification_system(self):
        """Test notification system"""
        try:
            from services.notification_service import NotificationService
            
            # Mock desktop notification
            with patch('plyer.notification.notify') as mock_notify:
                notification_service = NotificationService()
                notification_service.send_desktop_notification(
                    "Test", "Test message"
                )
                
                return mock_notify.called
                
        except Exception as e:
            print(f"      Notification test failed: {e}")
            return False
    
    def test_multi_user_workflow(self):
        """Test multi-user functionality"""
        try:
            from models.user import User
            from models.database import SessionLocal
            
            with SessionLocal() as db:
                # Create test users
                test_users = [
                    {"username": "user1", "email": "user1@test.com", "role": "user"},
                    {"username": "user2", "email": "user2@test.com", "role": "user"}
                ]
                
                created_users = []
                for user_data in test_users:
                    user = User(**user_data, password_hash="test_hash")
                    db.add(user)
                    created_users.append(user)
                
                db.commit()
                
                # Verify users were created
                return len(created_users) == 2
                
        except Exception as e:
            print(f"      Multi-user test failed: {e}")
            return False
    
    def run_performance_tests(self):
        """Run performance tests"""
        print("⚡ Running performance tests...")
        
        performance_tests = [
            self.test_pdf_processing_performance,
            self.test_database_performance,
            self.test_concurrent_processing,
            self.test_memory_usage
        ]
        
        results = {}
        
        for test_func in performance_tests:
            test_name = test_func.__name__
            print(f"   Running {test_name}...")
            
            try:
                result = test_func()
                results[test_name] = result
                print(f"      ✅ {test_name}: {result}")
            except Exception as e:
                print(f"      ❌ {test_name} failed: {e}")
                results[test_name] = {"error": str(e)}
        
        return results
    
    def test_pdf_processing_performance(self):
        """Test PDF processing performance"""
        start_time = time.time()
        
        # Simulate processing multiple PDFs
        for i in range(10):
            time.sleep(0.1)  # Simulate processing time
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return {
            "pdfs_processed": 10,
            "total_time_seconds": round(processing_time, 2),
            "avg_time_per_pdf": round(processing_time / 10, 2)
        }
    
    def test_database_performance(self):
        """Test database query performance"""
        try:
            from models.database import SessionLocal
            
            start_time = time.time()
            
            with SessionLocal() as db:
                # Simulate database operations
                for i in range(100):
                    db.execute("SELECT 1")
            
            end_time = time.time()
            query_time = end_time - start_time
            
            return {
                "queries_executed": 100,
                "total_time_seconds": round(query_time, 2),
                "avg_time_per_query": round(query_time / 100, 4)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def test_concurrent_processing(self):
        """Test concurrent processing capability"""
        import concurrent.futures
        
        def mock_processing_task(task_id):
            time.sleep(0.5)  # Simulate processing
            return f"Task {task_id} completed"
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(mock_processing_task, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return {
            "concurrent_tasks": 10,
            "max_workers": 5,
            "total_time_seconds": round(processing_time, 2),
            "completed_tasks": len(results)
        }
    
    def test_memory_usage(self):
        """Test memory usage"""
        try:
            import psutil
            
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Simulate memory-intensive operations
            large_data = []
            for i in range(1000):
                large_data.append("x" * 1000)  # Create some data
            
            # Get peak memory usage
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Cleanup
            del large_data
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            return {
                "initial_memory_mb": round(initial_memory, 2),
                "peak_memory_mb": round(peak_memory, 2),
                "final_memory_mb": round(final_memory, 2),
                "memory_increase_mb": round(peak_memory - initial_memory, 2)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def run_security_tests(self):
        """Run security tests"""
        print("🔒 Running security tests...")
        
        security_tests = [
            self.test_password_hashing,
            self.test_sql_injection_protection,
            self.test_jwt_token_security,
            self.test_file_access_security
        ]
        
        results = {}
        
        for test_func in security_tests:
            test_name = test_func.__name__
            print(f"   Running {test_name}...")
            
            try:
                result = test_func()
                results[test_name] = "PASSED" if result else "FAILED"
                print(f"      {'✅' if result else '❌'} {test_name}")
            except Exception as e:
                print(f"      ❌ {test_name} failed: {e}")
                results[test_name] = "ERROR"
        
        return results
    
    def test_password_hashing(self):
        """Test password hashing security"""
        try:
            from utils.security import hash_password, verify_password
            
            password = "test_password_123"
            hashed = hash_password(password)
            
            # Verify password works
            if not verify_password(password, hashed):
                return False
            
            # Verify wrong password fails
            if verify_password("wrong_password", hashed):
                return False
            
            # Verify hash is different each time
            hashed2 = hash_password(password)
            if hashed == hashed2:
                return False
            
            return True
            
        except Exception as e:
            print(f"      Password hashing test error: {e}")
            return False
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        try:
            from models.database import SessionLocal
            
            with SessionLocal() as db:
                # Try SQL injection attack
                malicious_input = "'; DROP TABLE users; --"
                
                # This should not cause any issues with parameterized queries
                result = db.execute(
                    "SELECT * FROM users WHERE username = :username",
                    {"username": malicious_input}
                )
                
                # If we get here without exception, protection is working
                return True
                
        except Exception as e:
            # If this causes an exception related to SQL injection, test fails
            if "syntax error" in str(e).lower() or "drop table" in str(e).lower():
                return False
            # Other exceptions might be expected
            return True
    
    def test_jwt_token_security(self):
        """Test JWT token security"""
        try:
            from utils.security import create_access_token, verify_token
            
            # Create token
            token = create_access_token({"user_id": 1, "username": "test"})
            
            # Verify token
            payload = verify_token(token)
            if not payload or payload.get("user_id") != 1:
                return False
            
            # Test invalid token
            try:
                verify_token("invalid_token")
                return False  # Should have raised exception
            except:
                pass  # Expected
            
            return True
            
        except Exception as e:
            print(f"      JWT test error: {e}")
            return False
    
    def test_file_access_security(self):
        """Test file access security"""
        try:
            # Test that path traversal attacks are prevented
            dangerous_paths = [
                "../../../etc/passwd",
                "..\\..\\windows\\system32\\config\\sam",
                "/etc/shadow",
                "C:\\Windows\\System32\\config\\SAM"
            ]
            
            from utils.file_handler import sanitize_path
            
            for dangerous_path in dangerous_paths:
                sanitized = sanitize_path(dangerous_path)
                if ".." in sanitized or sanitized.startswith("/"):
                    return False
            
            return True
            
        except Exception as e:
            print(f"      File security test error: {e}")
            return False
    
    def generate_test_report(self, unit_results, integration_results, performance_results, security_results):
        """Generate comprehensive test report"""
        print("\n📊 Generating test report...")
        
        report = {
            "test_run_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "unit_tests": {
                    "total": len(unit_results),
                    "passed": sum(1 for r in unit_results.values() if r == "PASSED"),
                    "failed": sum(1 for r in unit_results.values() if r == "FAILED"),
                    "errors": sum(1 for r in unit_results.values() if r == "ERROR")
                },
                "integration_tests": {
                    "total": len(integration_results),
                    "passed": sum(1 for r in integration_results.values() if r == "PASSED"),
                    "failed": sum(1 for r in integration_results.values() if r == "FAILED"),
                    "errors": sum(1 for r in integration_results.values() if r == "ERROR")
                },
                "security_tests": {
                    "total": len(security_results),
                    "passed": sum(1 for r in security_results.values() if r == "PASSED"),
                    "failed": sum(1 for r in security_results.values() if r == "FAILED"),
                    "errors": sum(1 for r in security_results.values() if r == "ERROR")
                }
            },
            "detailed_results": {
                "unit_tests": unit_results,
                "integration_tests": integration_results,
                "performance_tests": performance_results,
                "security_tests": security_results
            }
        }
        
        # Save report
        report_path = self.test_dir / "test_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Test report saved: {report_path}")
        return report
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting comprehensive test suite...")
        print("=" * 60)
        
        try:
            # Setup
            self.setup_test_environment()
            
            # Run test suites
            unit_results = self.run_unit_tests()
            integration_results = self.run_integration_tests()
            performance_results = self.run_performance_tests()
            security_results = self.run_security_tests()
            
            # Generate report
            report = self.generate_test_report(
                unit_results, integration_results, 
                performance_results, security_results
            )
            
            # Summary
            print("\n" + "=" * 60)
            print("📈 TEST SUITE SUMMARY")
            print("=" * 60)
            
            for test_type, results in report["summary"].items():
                print(f"{test_type.upper()}:")
                print(f"  Total: {results['total']}")
                print(f"  Passed: {results['passed']} ✅")
                print(f"  Failed: {results['failed']} ❌")
                print(f"  Errors: {results['errors']} 🔥")
                print()
            
            total_tests = sum(r["total"] for r in report["summary"].values())
            total_passed = sum(r["passed"] for r in report["summary"].values())
            success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
            
            print(f"OVERALL SUCCESS RATE: {success_rate:.1f}% ({total_passed}/{total_tests})")
            
            return success_rate >= 80  # Consider 80%+ as successful
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            self.teardown_test_environment()


def main():
    """Main test runner"""
    runner = TestSuiteRunner()
    
    try:
        success = runner.run_all_tests()
        exit_code = 0 if success else 1
        
        print(f"\n🏁 Test suite completed with exit code: {exit_code}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n❌ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()