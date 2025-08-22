from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Email Configuration - Update these with your actual email credentials
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER', 'your_email@gmail.com')  # Set EMAIL_USER environment variable
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD', 'your_app_password')  # Set EMAIL_PASSWORD environment variable
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'your_email@gmail.com')

mail = Mail(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.json')

def load_db():
    try:
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create default database structure if file doesn't exist
        default_db = {
            "alerts": [],
            "users": [],
            "feedback": []
        }
        save_db(default_db)
        return default_db
    except json.JSONDecodeError:
        print("Error: Invalid JSON in database file")
        return {"alerts": [], "users": [], "feedback": []}
    except Exception as e:
        print(f"Error loading database: {e}")
        return {"alerts": [], "users": [], "feedback": []}

def save_db(data):
    try:
        with open(DB_PATH, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving database: {e}")
        raise

def send_alert_email(recipient_email, alert_type, threshold_value, current_value):
    """Send smart alert email with intelligent recommendations"""
    try:
        # Check if email configuration is properly set
        if app.config['MAIL_USERNAME'] == 'your_email@gmail.com' or app.config['MAIL_PASSWORD'] == 'your_app_password':
            print("❌ Email configuration not set! Please set EMAIL_USER and EMAIL_PASSWORD environment variables.")
            return False
            
        # Validate email address
        if not recipient_email or '@' not in recipient_email:
            print(f"❌ Invalid email address: {recipient_email}")
            return False
            
        print(f"📧 Attempting to send email to: {recipient_email}")
        print(f"📧 Using email: {app.config['MAIL_USERNAME']}")
        
        # Calculate severity and urgency
        severity, urgency, recommendations = analyze_alert_severity(alert_type, threshold_value, current_value)
        
        # Priority-based subject line
        priority_emoji = "🔴" if urgency == "CRITICAL" else "🟡" if urgency == "HIGH" else "🟢"
        subject = f"{priority_emoji} URGENT: {alert_type.replace('_', ' ').title()} Alert - {urgency} Priority"
        
        # Smart recommendations based on severity
        smart_recommendations = get_smart_recommendations(alert_type, threshold_value, current_value, severity)
        
        # Time-based urgency
        time_context = get_time_context()
        
        message_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 2px solid {'#dc2626' if urgency == 'CRITICAL' else '#f59e0b' if urgency == 'HIGH' else '#10b981'}; border-radius: 8px;">
                <div style="background: {'linear-gradient(135deg, #dc2626, #b91c1c)' if urgency == 'CRITICAL' else 'linear-gradient(135deg, #f59e0b, #d97706)' if urgency == 'HIGH' else 'linear-gradient(135deg, #10b981, #059669)'}; color: white; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                    <h2 style="margin: 0; font-size: 24px;">🚨 {alert_type.replace('_', ' ').title()} Alert</h2>
                    <p style="margin: 5px 0 0 0; font-size: 16px;">{urgency} Priority - Immediate Action Required</p>
                </div>
                
                <div style="background-color: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0; border-radius: 4px;">
                    <h3 style="color: #dc2626; margin: 0 0 10px 0;">⚠️ CRITICAL ISSUE DETECTED</h3>
                    <p style="margin: 0; font-weight: bold;">Your system has crossed the threshold limit and needs immediate attention!</p>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                    <div style="background-color: #f8fafc; padding: 15px; border-radius: 6px;">
                        <h4 style="margin: 0 0 10px 0; color: #374151;">📊 Alert Details</h4>
                        <p><strong>Type:</strong> {alert_type.replace('_', ' ').title()}</p>
                        <p><strong>Threshold:</strong> {threshold_value}</p>
                        <p><strong>Current Value:</strong> <span style="color: #dc2626; font-weight: bold;">{current_value}</span></p>
                        <p><strong>Severity:</strong> <span style="color: {'#dc2626' if severity == 'HIGH' else '#f59e0b' if severity == 'MEDIUM' else '#10b981'}; font-weight: bold;">{severity}</span></p>
                        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    <div style="background-color: #f8fafc; padding: 15px; border-radius: 6px;">
                        <h4 style="margin: 0 0 10px 0; color: #374151;">⚡ Urgency Level</h4>
                        <p><strong>Priority:</strong> <span style="color: #dc2626; font-weight: bold;">{urgency}</span></p>
                        <p><strong>Response Time:</strong> {get_response_time(urgency)}</p>
                        <p><strong>Impact:</strong> {get_impact_assessment(alert_type, severity)}</p>
                        <p><strong>Time Context:</strong> {time_context}</p>
                    </div>
                </div>
                
                <div style="background-color: #fef3c7; border: 1px solid #f59e0b; padding: 20px; border-radius: 6px; margin: 20px 0;">
                    <h3 style="color: #92400e; margin: 0 0 15px 0;">🎯 IMMEDIATE ACTION REQUIRED</h3>
                    <div style="background-color: white; padding: 15px; border-radius: 4px;">
                        <p style="margin: 0 0 10px 0; font-weight: bold; color: #dc2626;">What needs to be fixed ASAP:</p>
                        {smart_recommendations}
                    </div>
                </div>
                
                <div style="background-color: #ecfdf5; border: 1px solid #10b981; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <h4 style="color: #065f46; margin: 0 0 10px 0;">📋 Step-by-Step Resolution</h4>
                    {get_step_by_step_resolution(alert_type, severity)}
                </div>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #374151;">🔗 Quick Actions</h4>
                    <p style="margin: 0 0 10px 0;">• <strong>Dashboard:</strong> <a href="http://127.0.0.1:5000/dashboard.html" style="color: #3b82f6;">View Real-time Status</a></p>
                    <p style="margin: 0 0 10px 0;">• <strong>Settings:</strong> <a href="http://127.0.0.1:5000/settings.html" style="color: #3b82f6;">Adjust Alert Thresholds</a></p>
                    <p style="margin: 0 0 10px 0;">• <strong>Support:</strong> Contact your system administrator immediately</p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    <p style="color: #6b7280; font-size: 12px; margin: 0;">🚨 This is an automated critical alert from AutoAlert Pro</p>
                    <p style="color: #6b7280; font-size: 12px; margin: 5px 0 0 0;">Response time: {get_response_time(urgency)} | Severity: {severity}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            html=message_body
        )
        
        print(f"📧 Sending email with subject: {subject}")
        mail.send(msg)
        print(f"✅ Smart alert email sent successfully to {recipient_email} - {urgency} priority")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        print(f"❌ Email config - Server: {app.config['MAIL_SERVER']}, Port: {app.config['MAIL_PORT']}")
        print(f"❌ Email config - Username: {app.config['MAIL_USERNAME']}")
        return False



def analyze_alert_severity(alert_type, threshold_value, current_value):
    """Analyze alert severity and provide intelligent recommendations"""
    threshold = int(threshold_value)
    current = int(current_value)
    
    # Calculate deviation percentage
    if alert_type == 'traffic_drop':
        deviation = ((threshold - current) / threshold) * 100
        if deviation > 50:
            severity = "HIGH"
            urgency = "CRITICAL"
        elif deviation > 25:
            severity = "MEDIUM"
            urgency = "HIGH"
        else:
            severity = "LOW"
            urgency = "MEDIUM"
    elif alert_type == 'site_down':
        deviation = ((current - threshold) / threshold) * 100
        if deviation > 100:
            severity = "HIGH"
            urgency = "CRITICAL"
        elif deviation > 50:
            severity = "MEDIUM"
            urgency = "HIGH"
        else:
            severity = "LOW"
            urgency = "MEDIUM"
    elif alert_type == 'test_alert':
        # For test alerts, simulate a critical situation
        deviation = 25  # Simulate 25% deviation
        severity = "HIGH"
        urgency = "CRITICAL"
    else:
        # Default case for any other alert types
        deviation = 30  # Default deviation
        severity = "MEDIUM"
        urgency = "HIGH"
    
    return severity, urgency, deviation

def get_smart_recommendations(alert_type, threshold_value, current_value, severity):
    """Get intelligent recommendations based on alert type and severity"""
    if alert_type == 'traffic_drop':
        if severity == "HIGH":
            return """
            <ul style="margin: 0; padding-left: 20px; color: #dc2626;">
                <li><strong>URGENT:</strong> Website may be completely down - check server status immediately</li>
                <li><strong>CRITICAL:</strong> DNS issues detected - verify domain configuration</li>
                <li><strong>IMMEDIATE:</strong> Contact hosting provider for emergency support</li>
                <li><strong>MONITOR:</strong> Check server logs for error patterns</li>
            </ul>
            """
        elif severity == "MEDIUM":
            return """
            <ul style="margin: 0; padding-left: 20px; color: #f59e0b;">
                <li><strong>CHECK:</strong> Website performance and loading times</li>
                <li><strong>VERIFY:</strong> Server resources and bandwidth usage</li>
                <li><strong>REVIEW:</strong> Recent code deployments or changes</li>
                <li><strong>MONITOR:</strong> Traffic patterns and user behavior</li>
            </ul>
            """
        else:
            return """
            <ul style="margin: 0; padding-left: 20px; color: #10b981;">
                <li><strong>MONITOR:</strong> Keep an eye on traffic trends</li>
                <li><strong>OPTIMIZE:</strong> Consider performance improvements</li>
                <li><strong>ANALYZE:</strong> Review marketing campaigns and SEO</li>
            </ul>
            """
    elif alert_type == 'site_down':
        if severity == "HIGH":
            return """
            <ul style="margin: 0; padding-left: 20px; color: #dc2626;">
                <li><strong>EMERGENCY:</strong> Server may be overloaded or crashed</li>
                <li><strong>CRITICAL:</strong> Database connection issues - check DB status</li>
                <li><strong>URGENT:</strong> Restart critical services immediately</li>
                <li><strong>MONITOR:</strong> Check CPU, memory, and disk usage</li>
            </ul>
            """
        elif severity == "MEDIUM":
            return """
            <ul style="margin: 0; padding-left: 20px; color: #f59e0b;">
                <li><strong>OPTIMIZE:</strong> Server performance needs improvement</li>
                <li><strong>SCALE:</strong> Consider adding more resources</li>
                <li><strong>REVIEW:</strong> Check for memory leaks or inefficient code</li>
                <li><strong>MONITOR:</strong> Response time patterns</li>
            </ul>
            """
        else:
            return """
            <ul style="margin: 0; padding-left: 20px; color: #10b981;">
                <li><strong>OPTIMIZE:</strong> Minor performance improvements needed</li>
                <li><strong>MONITOR:</strong> Keep tracking response times</li>
                <li><strong>ANALYZE:</strong> Review server configuration</li>
            </ul>
            """
    else:
        return """
        <ul style="margin: 0; padding-left: 20px;">
            <li>Review system configuration</li>
            <li>Check for any recent changes</li>
            <li>Monitor system performance</li>
        </ul>
        """

def get_step_by_step_resolution(alert_type, severity):
    """Get step-by-step resolution guide"""
    if alert_type == 'traffic_drop':
        if severity == "HIGH":
            return """
            <ol style="margin: 0; padding-left: 20px; color: #dc2626;">
                <li><strong>Step 1:</strong> Immediately check if website is accessible</li>
                <li><strong>Step 2:</strong> Verify server is running and responsive</li>
                <li><strong>Step 3:</strong> Check DNS settings and domain configuration</li>
                <li><strong>Step 4:</strong> Review server logs for error messages</li>
                <li><strong>Step 5:</strong> Contact hosting provider if issues persist</li>
            </ol>
            """
        else:
            return """
            <ol style="margin: 0; padding-left: 20px;">
                <li><strong>Step 1:</strong> Check website performance metrics</li>
                <li><strong>Step 2:</strong> Review recent changes or deployments</li>
                <li><strong>Step 3:</strong> Analyze traffic patterns and sources</li>
                <li><strong>Step 4:</strong> Optimize website performance if needed</li>
            </ol>
            """
    elif alert_type == 'site_down':
        if severity == "HIGH":
            return """
            <ol style="margin: 0; padding-left: 20px; color: #dc2626;">
                <li><strong>Step 1:</strong> Check server status and health</li>
                <li><strong>Step 2:</strong> Verify database connectivity</li>
                <li><strong>Step 3:</strong> Restart critical services</li>
                <li><strong>Step 4:</strong> Monitor system resources</li>
                <li><strong>Step 5:</strong> Check for security issues</li>
            </ol>
            """
        else:
            return """
            <ol style="margin: 0; padding-left: 20px;">
                <li><strong>Step 1:</strong> Analyze server performance metrics</li>
                <li><strong>Step 2:</strong> Review application logs</li>
                <li><strong>Step 3:</strong> Optimize database queries</li>
                <li><strong>Step 4:</strong> Consider scaling resources</li>
            </ol>
            """
    else:
        return """
        <ol style="margin: 0; padding-left: 20px;">
            <li><strong>Step 1:</strong> Identify the root cause</li>
            <li><strong>Step 2:</strong> Review system configuration</li>
            <li><strong>Step 3:</strong> Implement necessary fixes</li>
            <li><strong>Step 4:</strong> Monitor for improvements</li>
        </ol>
        """

def get_response_time(urgency):
    """Get recommended response time based on urgency"""
    if urgency == "CRITICAL":
        return "IMMEDIATE (within 5 minutes)"
    elif urgency == "HIGH":
        return "URGENT (within 15 minutes)"
    elif urgency == "MEDIUM":
        return "PRIORITY (within 1 hour)"
    else:
        return "NORMAL (within 4 hours)"

def get_impact_assessment(alert_type, severity):
    """Get impact assessment based on alert type and severity"""
    if alert_type == 'traffic_drop':
        if severity == "HIGH":
            return "SEVERE - Potential revenue loss and user experience impact"
        elif severity == "MEDIUM":
            return "MODERATE - User experience degradation"
        else:
            return "MINOR - Slight performance impact"
    elif alert_type == 'site_down':
        if severity == "HIGH":
            return "CRITICAL - Complete service outage"
        elif severity == "MEDIUM":
            return "SIGNIFICANT - Performance degradation"
        else:
            return "MINOR - Slight response time increase"
    else:
        return "VARIABLE - Depends on system impact"

def get_time_context():
    """Get time-based context for urgency"""
    current_hour = datetime.now().hour
    if 9 <= current_hour <= 17:
        return "Business Hours - High Impact"
    elif 18 <= current_hour <= 22:
        return "Evening Hours - Moderate Impact"
    else:
        return "Off Hours - Lower Impact"

@app.route('/')
def serve_dashboard():
    return send_from_directory('../frontend', 'dashboard.html')

@app.route('/set-alert', methods=['POST'])
def set_alert():
    try:
        data = request.json
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['type', 'value', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # Add timestamp if not provided
        if 'date' not in data:
            data['date'] = datetime.now().isoformat()
        
        # Add default status
        if 'status' not in data:
            data['status'] = 'Normal'
        
        # Check if threshold is exceeded and send email
        threshold_value = int(data.get('value', 0))
        current_value = int(data.get('current_value', 0))  # This would come from monitoring
        
        # For demo purposes, let's simulate some values
        if data['type'] == 'traffic_drop':
            # Simulate current traffic (in real app, this would come from monitoring)
            import random
            current_value = random.randint(50, 150)
        elif data['type'] == 'site_down':
            # Simulate response time (in real app, this would come from monitoring)
            import random
            current_value = random.randint(100, 500)
        
        # Check if threshold is exceeded
        alert_triggered = False
        if data['type'] == 'traffic_drop' and current_value < threshold_value:
            alert_triggered = True
        elif data['type'] == 'site_down' and current_value > threshold_value:
            alert_triggered = True
        
        # Update status and send notifications if alert is triggered
        if alert_triggered:
            data['status'] = 'Alert Sent'
            data['current_value'] = current_value
            
            # Send email notification
            email_sent = send_alert_email(
                data['email'], 
                data['type'], 
                threshold_value, 
                current_value
            )
            if email_sent:
                print(f"Alert email sent to {data['email']}")
            else:
                print(f"Failed to send alert email to {data['email']}")
            

        else:
            data['status'] = 'Normal'
            data['current_value'] = current_value
        
        db = load_db()
        db['alerts'].append(data)
        save_db(db)
        
        response_message = 'Alert saved!'
        if alert_triggered:
            response_message = 'Alert saved and email notification sent!'
        
        return jsonify({
            'message': response_message,
            'alert_triggered': alert_triggered,
            'current_value': current_value
        })
    except Exception as e:
        print(f"Error saving alert: {e}")
        return jsonify({'message': 'Failed to save alert'}), 500

@app.route('/check-alerts', methods=['POST'])
def check_alerts():
    """Endpoint to check all active alerts and send emails if thresholds are exceeded"""
    try:
        db = load_db()
        alerts = db.get('alerts', [])
        active_alerts = [alert for alert in alerts if alert.get('status') != 'Alert Sent']
        
        alerts_checked = 0
        emails_sent = 0
        
        for alert in active_alerts:
            alerts_checked += 1
            threshold_value = int(alert.get('value', 0))
            
            # Simulate current values (in real app, this would come from actual monitoring)
            import random
            if alert['type'] == 'traffic_drop':
                current_value = random.randint(50, 150)
                alert_triggered = current_value < threshold_value
            elif alert['type'] == 'site_down':
                current_value = random.randint(100, 500)
                alert_triggered = current_value > threshold_value
            else:
                continue
            
            if alert_triggered:
                # Send email
                email_sent = send_alert_email(
                    alert['email'],
                    alert['type'],
                    threshold_value,
                    current_value
                )
                
                if email_sent:
                    emails_sent += 1
                    alert['status'] = 'Alert Sent'
                    alert['current_value'] = current_value
                    alert['last_checked'] = datetime.now().isoformat()
        
        # Save updated alerts
        if emails_sent > 0:
            save_db(db)
        
        return jsonify({
            'message': f'Checked {alerts_checked} alerts, sent {emails_sent} emails',
            'alerts_checked': alerts_checked,
            'emails_sent': emails_sent
        })
        
    except Exception as e:
        print(f"Error checking alerts: {e}")
        return jsonify({'message': 'Failed to check alerts'}), 500

@app.route('/get-alerts', methods=['GET'])
def get_alerts():
    try:
        db = load_db()
        return jsonify({'alerts': db.get('alerts', [])})
    except Exception as e:
        print(f"Error loading alerts: {e}")
        return jsonify({'alerts': []})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    db = load_db()
    for user in db.get('users', []):
        if user['email'] == email and user['password'] == password:
            return jsonify({"success": True, "message": "Login successful!"})
    return jsonify({"success": False, "message": "Invalid email or password."})
@app.route('/login.html')
def serve_login_html():
    return send_from_directory('../frontend', 'login.html')
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    db = load_db()
    # Check if user already exists
    for user in db.get('users', []):
        if user['email'] == email:
            return jsonify({"success": False, "message": "Email already registered."})
    # Add new user
    db.setdefault('users', []).append({"email": email, "password": password})
    save_db(db)
    return jsonify({"success": True, "message": "Registration successful!"})

@app.route('/dashboard.html')
def serve_dashboard_html():
    return send_from_directory('../frontend', 'dashboard.html')
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_msg = data.get('message', '').lower().strip()
    
    if not user_msg:
        return jsonify({"reply": "Please enter a message."})
    
    # Simple rule-based chatbot responses
    responses = {
        'hello': "Hello! I'm your AutoAlert Pro assistant. How can I help you today?",
        'hi': "Hi there! Welcome to AutoAlert Pro. What can I assist you with?",
        'help': "I can help you with:\n• Setting up alerts\n• Checking alert status\n• Understanding alert types\n• Troubleshooting issues\nWhat would you like to know?",
        'alert': "To set up an alert:\n1. Choose the alert type (traffic drop or site down)\n2. Set your threshold value\n3. Enter your email\n4. Click 'Set Alert'\nThe system will monitor and notify you when conditions are met.",
        'traffic': "Traffic alerts monitor your website's visitor count. Set a threshold and get notified when traffic drops below that level.",
        'site down': "Site down alerts check if your website is accessible. You'll be notified if the site becomes unavailable.",
        'email': "Email notifications are sent to the address you provide when setting up alerts. Make sure to use a valid email address.",
        'threshold': "The threshold is the value that triggers an alert. For traffic, it's the minimum visitor count. For site down, it's the response time limit.",
        'status': "You can check alert status in the 'Recent Submissions' table on the dashboard. Green means normal, red means alert was sent.",
        'how to': "To get started:\n1. Fill out the alert form on the dashboard\n2. Choose your alert type and threshold\n3. Enter your email\n4. Submit and you're all set!",
        'troubleshoot': "Common issues:\n• Check your email address is correct\n• Ensure threshold values are reasonable\n• Verify your internet connection\nNeed more specific help?",
        'thanks': "You're welcome! Let me know if you need anything else.",
        'thank you': "You're welcome! Feel free to ask if you have more questions.",
        'bye': "Goodbye! Have a great day with AutoAlert Pro!",
        'goodbye': "See you later! Your alerts will keep running in the background."
    }
    
    # Check for exact matches first
    if user_msg in responses:
        return jsonify({"reply": responses[user_msg]})
    
    # Check for partial matches
    for key, response in responses.items():
        if key in user_msg:
            return jsonify({"reply": response})
    
    # Check for common patterns
    if any(word in user_msg for word in ['what', 'how', 'when', 'where', 'why']):
        return jsonify({"reply": "That's a great question! Could you be more specific about what you'd like to know about AutoAlert Pro?"})
    
    if any(word in user_msg for word in ['problem', 'issue', 'error', 'broken']):
        return jsonify({"reply": "I'm sorry to hear you're having issues. Can you describe the problem in more detail? I'll do my best to help you resolve it."})
    
    if any(word in user_msg for word in ['monitor', 'track', 'watch']):
        return jsonify({"reply": "AutoAlert Pro continuously monitors your specified metrics. Once you set up an alert, it runs in the background and notifies you when conditions are met."})
    
    # Default response
    return jsonify({"reply": "I'm not sure I understand. Try asking about alerts, traffic monitoring, site status, or how to set up notifications. You can also type 'help' for a list of things I can assist with."})
@app.route('/settings', methods=['GET'])
def get_settings():
    try:
        db = load_db()
        users = db.get('users', [])
        if users:
            user = users[0]
            return jsonify({
                "email": user.get("email", ""),
                "notifications": user.get("notifications", True)
            })
        else:
            return jsonify({
                "email": "",
                "notifications": True
            })
    except Exception as e:
        print(f"Error loading settings: {e}")
        return jsonify({
            "email": "",
            "notifications": True
        })

@app.route('/settings', methods=['POST'])
def update_settings():
    data = request.get_json()
    db = load_db()
    if db.get('users'):
        db['users'][0]['email'] = data.get('email', db['users'][0].get('email', ''))
        db['users'][0]['notifications'] = data.get('notifications', True)
        save_db(db)
        return jsonify({"message": "Settings updated!"})
    return jsonify({"message": "No user found."}), 400
@app.route('/settings.html')
def serve_settings_html():
    return send_from_directory('../frontend', 'settings.html')
@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    db = load_db()
    if 'feedback' not in db:
        db['feedback'] = []
    
    feedback_entry = {
        "type": data.get("type"),
        "alertId": data.get("alertId"),
        "rating": data.get("rating"),
        "text": data.get("text"),
        "date": datetime.now().isoformat()
    }
    db['feedback'].append(feedback_entry)
    save_db(db)
    return jsonify({"message": "Feedback submitted. Thank you!"})

@app.route('/test-email', methods=['POST'])
def test_email():
    """Test endpoint to verify email functionality"""
    try:
        data = request.get_json()
        test_email = data.get('email', '')
        
        if not test_email:
            return jsonify({'success': False, 'message': 'Please provide an email address'}), 400
            
        print(f"🧪 Testing email functionality for: {test_email}")
        
        # Send a test email
        success = send_alert_email(
            recipient_email=test_email,
            alert_type='test_alert',
            threshold_value=80,
            current_value=95
        )
        
        if success:
            return jsonify({
                'success': True, 
                'message': f'Test email sent successfully to {test_email}! Check your inbox and spam folder.'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Failed to send test email. Check console for details.'
            }), 500
            
    except Exception as e:
        print(f"❌ Error in test email endpoint: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'Error testing email: {str(e)}'
        }), 500



if __name__ == '__main__':
    app.run(debug=True)

