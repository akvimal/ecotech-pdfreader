# services/notification_service.py
from plyer import notification
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class NotificationService:
    def __init__(self):
        self.load_settings()
    
    def send_desktop_notification(self, title, message, icon_path=None):
        """Send desktop notification"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_icon=icon_path,
                timeout=10
            )
        except Exception as e:
            print(f"Desktop notification failed: {e}")
    
    def send_email_notification(self, user_email, subject, body):
        """Send email notification"""
        try:
            # Configure SMTP settings
            msg = MimeMultipart()
            msg['From'] = "noreply@pdfprocessor.local"
            msg['To'] = user_email
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'html'))
            
            # Send email using local SMTP or configured service
            # Implementation depends on your email setup
            
        except Exception as e:
            print(f"Email notification failed: {e}")
    
    def notify_processing_complete(self, job_details):
        """Notify user when PDF processing is complete"""
        title = "PDF Processing Complete"
        message = f"Successfully processed {job_details['pdf_name']} → {job_details['excel_name']}"
        
        # Desktop notification
        self.send_desktop_notification(title, message)
        
        # Email notification
        if job_details['email_notifications_enabled']:
            email_body = f"""
            <h2>PDF Processing Complete</h2>
            <p><strong>PDF File:</strong> {job_details['pdf_name']}</p>
            <p><strong>Excel File:</strong> {job_details['excel_name']}</p>
            <p><strong>Tables Processed:</strong> {job_details['tables_count']}</p>
            <p><strong>Rows Converted:</strong> {job_details['rows_count']}</p>
            <p><strong>Processing Time:</strong> {job_details['processing_time']}</p>
            """
            self.send_email_notification(
                job_details['user_email'], 
                title, 
                email_body
            )