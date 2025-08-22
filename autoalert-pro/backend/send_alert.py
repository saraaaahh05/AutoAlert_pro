import smtplib

def send_email(to, message):
    sender = "your@gmail.com"
    password = "your-app-password"

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, to, f"Subject: AutoAlert 🚨\n\n{message}")