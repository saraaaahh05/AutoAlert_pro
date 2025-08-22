import time
import json
from send_alert import send_email

def check_traffic():
    current_traffic = 789  # Dummy value

    with open("db.json") as f:
        alerts = json.load(f)["alerts"]

    for alert in alerts:
        if alert["type"] == "traffic" and current_traffic < alert["value"]:
            send_email(alert["email"], f"Traffic dropped to {current_traffic}!")

while True:
    check_traffic()
    time.sleep(300)