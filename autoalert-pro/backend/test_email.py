import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email_config():
    """Test email configuration"""
    print("🧪 Testing Email Configuration...")
    
    # Check environment variables
    email_user = os.environ.get('EMAIL_USER')
    email_password = os.environ.get('EMAIL_PASSWORD')
    
    print(f"📧 Email User: {email_user}")
    print(f"🔑 Email Password: {'*' * len(email_password) if email_password else 'NOT SET'}")
    
    if not email_user or not email_password:
        print("❌ Environment variables not set!")
        print("Please run:")
        print("$env:EMAIL_USER='your_email@gmail.com'")
        print("$env:EMAIL_PASSWORD='your_app_password'")
        return False
    
    if email_user == 'your_email@gmail.com' or email_password == 'your_app_password':
        print("❌ Using default placeholder values!")
        print("Please set real email credentials.")
        return False
    
    # Test SMTP connection
    try:
        print("🔌 Testing SMTP connection...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("🔐 Attempting login...")
        server.login(email_user, email_password)
        print("✅ Login successful!")
        
        # Test sending a simple email
        print("📤 Testing email send...")
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_user
        msg['Subject'] = "🧪 AutoAlert Pro - Email Test"
        
        body = """
        This is a test email from AutoAlert Pro.
        
        If you receive this, your email configuration is working correctly!
        
        🎉 Email system is ready for production use.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server.send_message(msg)
        server.quit()
        
        print("✅ Test email sent successfully!")
        print("📧 Check your inbox for the test email.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_email_config() 